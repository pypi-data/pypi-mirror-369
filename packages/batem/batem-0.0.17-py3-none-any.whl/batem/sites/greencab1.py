from batem.core.data import DataProvider, Bindings
from batem.core.solar import SolarModel, SolarSystem, Collector
from batem.core.model import BuildingStateModelMaker
from batem.core.components import SideFactory
from batem.core.control import TemperatureController, Simulation, WEEKDAYS, SignalBuilder, TemperatureSetpointPort, HvacContinuousModePort
from batem.core.inhabitants import Preference
from batem.core.library import SIDE_TYPES
from batem.core.statemodel import StateModel

# #### DESIGN PARAMETERS ####

surface_window = 1.8 * 1.9
direction_window = -90
solar_protection = 90  # no protection
solar_factor = 0.56
cabinet_length = 5.77
cabinet_width = 2.21
cabinet_height = 2.29
body_metabolism = 100
occupant_consumption = 200
body_PCO2 = 7

surface_cabinet: float = cabinet_length*cabinet_width
volume_cabinet: float = surface_cabinet*cabinet_height
surface_cabinet_wall: float = 2 * (cabinet_length + cabinet_width) * cabinet_height - surface_window
q_infiltration: float = volume_cabinet / 3600

wall = SideFactory(('plaster', 13e-3), ('steel', 5e-3), ('wood', 3e-3))
floor = SideFactory(('wood', 10e-3), ('steel', 5e-3))
ceiling = SideFactory(('plaster', 13e-3), ('steel', 5e-3))
glazing = SideFactory(('glass', 4e-3), ('air', 10e-3), ('glass', 4e-3), ('air', 10e-3), ('glass', 4e-3))

# #### DATA PROVIDER ####
bindings = Bindings()
bindings('TZoutdoor', 'weather_temperature')

dp = DataProvider(location='Saint-Julien-en-Saint-Alban', latitude_deg_north=44.71407488275519, longitude_deg_east=4.633318302898348, starting_stringdate='1/1/2022', ending_stringdate='31/12/2022', bindings=bindings, albedo=0.1, pollution=0.1, number_of_levels=4)

# #### SOLAR MODEL ####

solar_model = SolarModel(dp.weather_data)
dp.solar_model = solar_model
solar_system = SolarSystem(solar_model)
Collector(solar_system, 'main', surface_m2=surface_window, exposure_deg=direction_window, slope_deg=90, solar_factor=solar_factor)
solar_gains_with_mask: list[float] = solar_system.powers_W(gather_collectors=True)
dp.add_external_variable('Psun_window', solar_gains_with_mask)

# #### SIGNAL GENERATION ####
signal_builder = SignalBuilder(dp.series('datetime'))

occupancy: list[float | None] = signal_builder.build_daily([WEEKDAYS.MONDAY, WEEKDAYS.TUESDAY, WEEKDAYS.WEDNESDAY, WEEKDAYS.THURSDAY, WEEKDAYS.FRIDAY], {0: 0, 7: 1, 8: 3, 19: 0})
occupancy = signal_builder.filter_denonify(occupancy)
PCO2cabinet = signal_builder.filter(occupancy, lambda x: x * body_PCO2 if x is not None else 0)
dp.add_external_variable('PCO2cabinet', PCO2cabinet)
dp.add_external_variable('occupancy', occupancy)
presence: list[int] = [int(occupancy[k] > 0) for k in range(len(dp))]
dp.add_external_variable('presence', presence)

hvac_mode: list[float | None] = signal_builder.build_seasonal('16/11', '15/3', 1, 0, '1/5', '30/9', -1)
heating_setpoints: list[float | None] = signal_builder.build_daily([WEEKDAYS.MONDAY, WEEKDAYS.TUESDAY, WEEKDAYS.WEDNESDAY, WEEKDAYS.THURSDAY, WEEKDAYS.FRIDAY], {0: None, 7: 19, 19: None}, hvac_mode, 1)
cooling_setpoints = signal_builder.build_daily([WEEKDAYS.MONDAY, WEEKDAYS.TUESDAY, WEEKDAYS.WEDNESDAY, WEEKDAYS.THURSDAY, WEEKDAYS.FRIDAY], {0: None, 7: 24, 19: None}, hvac_mode, -1)
hvac_setpoints = signal_builder.merge(heating_setpoints, cooling_setpoints, operator=max)
dp.add_external_variable('TZcabinet_setpoint', hvac_setpoints)
dp.add_external_variable('cabinet:mode', hvac_mode)
dp.add_external_variable('cabinet:Pheat_gain', [occupancy[k] * (body_metabolism + occupant_consumption) + solar_gains_with_mask[k] for k in dp.ks])

hvac_port = HvacContinuousModePort(data_provider=dp, model_variable_name='PZcabinet', feeding_variable_name='cabinet:Pheater', max_heating_power=2000, max_cooling_power=2000, mode_variable='cabinet:mode')

dp.add_parameter('CCO2outdoor', 400)
dp.add_parameter('cabinet-outdoor:Q', q_infiltration)
dp.add_parameter('cabinet:volume', volume_cabinet)

state_model_maker = BuildingStateModelMaker('cabinet', data_provider=dp, periodic_depth_seconds=3600, state_model_order_max=5)

# Cabinet
state_model_maker.make_side(wall('cabinet', 'outdoor', SIDE_TYPES.WALL, surface_cabinet_wall))
state_model_maker.make_side(floor('cabinet', 'outdoor', SIDE_TYPES.FLOOR, surface_cabinet))
state_model_maker.make_side(ceiling('cabinet', 'outdoor', SIDE_TYPES.CEILING, surface_cabinet))
state_model_maker.make_side(glazing('cabinet', 'outdoor', SIDE_TYPES.GLAZING, surface_window))
state_model_maker.simulate_zone('cabinet')
state_model_maker.connect_airflow('cabinet', 'outdoor', dp('cabinet-outdoor:Q'))  # nominal value
print(state_model_maker)

state_model_nominal: StateModel = state_model_maker.make_k()

temperature_setpoint_port = TemperatureSetpointPort(data_provider=dp, model_variable_name='TZcabinet', feeding_variable_name='TZcabinet_setpoint', heating_levels=[13, 19, 20, 21, 22, 23], cooling_levels=[24, 25, 26, 28, 29, 32], mode_variable='cabinet:mode')
temperature_controller = TemperatureController(hvac_heat_port=hvac_port, temperature_setpoint_port=temperature_setpoint_port, state_model_nominal=state_model_nominal)

simulation = Simulation(dp, state_model_maker, control_ports=[hvac_port])
simulation.add_zone(zone_name='cabinet', heat_gain_name='cabinet:Pheat_gain', CO2production_name='PCO2cabinet', hvac_power_port=hvac_port, temperature_controller=temperature_controller)

# Initialize the power variable that the model expects
dp.add_external_variable('PZcabinet', dp.series('cabinet:Pheat_gain'))
simulation.run(suffix='_sim')

# #### PRINT THE SIMULATION RESULTS ####
preference = Preference(preferred_temperatures=(19, 24), extreme_temperatures=(16, 29), preferred_CO2_concentration=(500, 1500), temperature_weight_wrt_CO2=0.5, power_weight_wrt_comfort=0.5, mode_cop={1: 2, -1: 2})

print(simulation)
print(simulation.control_ports)
preference.print_assessment(dp.datetimes, dp.series('cabinet:Pheater'), dp.series('TZcabinet_sim'), dp.series('CCO2cabinet_sim'), dp.series('occupancy'))
# dp.plot('PCO2cabinet', 'presence', 'Psun_window', 'cabinet:Pheat_gain')
dp.plot()