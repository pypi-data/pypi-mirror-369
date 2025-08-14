import numpy
import time
from batem.core.data import DataProvider, Bindings
from batem.core.control import SignalBuilder
from batem.core.solar import SolarModel, SolarSystem, Collector
from batem.core.model import BuildingStateModelMaker
from batem.core.components import SideFactory
from batem.core.control import TemperatureController, Simulation, WEEKDAYS, SignalBuilder, TemperatureSetpointPort, HvacContinuousModePort, Port
from batem.core.inhabitants import Preference
from batem.core.library import SIDE_TYPES, DIRECTIONS_SREF, SLOPES
from batem.core.statemodel import StateModel


# #### DESIGN PARAMETERS ####

# human actors
body_metabolism = 100
occupant_consumption = 200
body_PCO2 = 7

# Window
surface_window: float = 2.2 * 0.9
exposure_window = DIRECTIONS_SREF.NORTH.value
slope_window = SLOPES.VERTICAL.value
solar_protection = 90  # Notice that 90°C ->no protection
solar_factor = 0.56

# Physics
insulation_thickness = 150e-3
container_height = 2.29
container_width = 2.44
container_length = 6
toilet_length = 1.18
container_floor_surface: float = container_length * container_width
cabinet_volume: float = container_floor_surface * container_height
toilet_surface: float = toilet_length * container_width
toilet_volume: float = toilet_surface * container_height
cabinet_surface_wall: float = (2 * container_length + container_width) * container_height - surface_window

# ventilation
q_infiltration: float = cabinet_volume/3600
q_ventilation: float = 6 * cabinet_volume/3600
q_freecooling: float = 15 * cabinet_volume/3600


# #### DATA PROVIDER AND SIGNALS ####
starting_stringdate = "1/1/2022"
ending_stringdate = "31/12/2023"
location = 'Saint-Julien-en-Saint-Alban'
latitude_deg_north = 44.71407488275519
longitude_deg_east = 4.633318302898348

bindings = Bindings()
bindings('TZoutdoor', 'weather_temperature')

dp = DataProvider(location=location, latitude_deg_north=latitude_deg_north, longitude_deg_east=longitude_deg_east, starting_stringdate=starting_stringdate, ending_stringdate=ending_stringdate, bindings=bindings, albedo=0.1, pollution=0.1, number_of_levels=4)

solar_model = SolarModel(dp.weather_data)
dp.solar_model = solar_model
solar_system = SolarSystem(solar_model)
Collector(solar_system, 'main', surface_m2=surface_window, exposure_deg=exposure_window, slope_deg=slope_window, solar_factor=solar_factor)
solar_gains_with_mask: list[float] = solar_system.powers_W(gather_collectors=True)
dp.add_external_variable('Psun_window', solar_gains_with_mask)

signal_builder = SignalBuilder(dp.series('datetime'))
occupancy: list[float | None] = signal_builder.build_daily([WEEKDAYS.MONDAY, WEEKDAYS.TUESDAY, WEEKDAYS.WEDNESDAY, WEEKDAYS.THURSDAY, WEEKDAYS.FRIDAY], {0: 0, 7: 1, 8: 3, 18: 0})
occupancy = signal_builder.filter_denonify(occupancy)
PCO2cabinet: list[float | None] = signal_builder.filter(occupancy, lambda x: x * body_PCO2 if x is not None else 0)
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
dp.add_parameter('PZtoilet', 0)
dp.add_parameter('PCO2toilet', 0)

dp.add_parameter('CCO2outdoor', 400)
dp.add_parameter('cabinet:volume', cabinet_volume)
dp.add_parameter('toilet:volume', toilet_volume)

ventilation: list[float] = signal_builder.build_daily([WEEKDAYS.MONDAY, WEEKDAYS.TUESDAY, WEEKDAYS.WEDNESDAY, WEEKDAYS.THURSDAY, WEEKDAYS.FRIDAY], {0: 0, 7: 1, 18: 0})
dp.add_external_variable('ventilation', ventilation)
dp.add_external_variable('cabinet-outdoor:Q', [q_infiltration + ventilation[k]*q_ventilation if ventilation[k] is not None else q_infiltration for k in range(len(dp))])
dp.add_external_variable('toilet-outdoor:Q', [q_infiltration + ventilation[k]*q_ventilation if ventilation[k] is not None else q_infiltration for k in range(len(dp))])


# #### STATE MODEL MAKER AND TEMPERATURE CONTROLLERS ####
state_model_maker = BuildingStateModelMaker('cabinet', 'toilet', data_provider=dp, periodic_depth_seconds=3600, state_model_order_max=5)

wall = SideFactory(('wood', 3e-3), ('polystyrene', insulation_thickness), ('steel', 5e-3), ('wood', 3e-3))
floor = SideFactory(('wood', 10e-3), ('polystyrene', insulation_thickness), ('steel', 5e-3))
ceiling = SideFactory(('wood', 3e-3), ('polystyrene', insulation_thickness), ('steel', 5e-3))
glazing = SideFactory(('glass', 4e-3), ('air', 10e-3), ('glass', 4e-3), ('air', 10e-3), ('glass', 4e-3))
internal = SideFactory(('wood', 9e-3), ('air', 20e-3), ('wood', 9e-3))

# Cabinet
state_model_maker.make_side(wall('cabinet', 'outdoor', SIDE_TYPES.WALL, cabinet_surface_wall))
state_model_maker.make_side(floor('cabinet', 'outdoor', SIDE_TYPES.FLOOR, container_floor_surface))
state_model_maker.make_side(ceiling('cabinet', 'outdoor', SIDE_TYPES.CEILING, container_floor_surface))
state_model_maker.make_side(glazing('cabinet', 'outdoor', SIDE_TYPES.GLAZING, surface_window))

# Toilet
state_model_maker.make_side(internal('cabinet', 'toilet', SIDE_TYPES.WALL, container_width * container_height))
state_model_maker.make_side(wall('toilet', 'outdoor', SIDE_TYPES.WALL, (toilet_length * 2 + container_width) * container_height))
state_model_maker.make_side(floor('toilet', 'outdoor', SIDE_TYPES.FLOOR, container_width * toilet_length))
state_model_maker.make_side(ceiling('toilet', 'outdoor', SIDE_TYPES.CEILING, container_width * toilet_length))

state_model_maker.simulate_zone('cabinet', 'toilet')
state_model_maker.connect_airflow('cabinet', 'outdoor', dp('cabinet-outdoor:Q'))  # nominal value
state_model_maker.connect_airflow('toilet', 'outdoor', dp('toilet-outdoor:Q'))  # nominal value
nominal_state_model: StateModel = state_model_maker.make_k()


# #### CONTROL PORTS ####
hvac_port = HvacContinuousModePort(data_provider=dp, model_variable_name='PZcabinet', feeding_variable_name='cabinet:Phvac', max_heating_power=3000, max_cooling_power=3000, mode_variable='cabinet:mode')
temperature_setpoint_port = TemperatureSetpointPort(data_provider=dp, model_variable_name='TZcabinet', feeding_variable_name='TZcabinet_setpoint', heating_levels=[13, 19, 20, 21, 22, 23], cooling_levels=[24, 25, 26, 28, 29, 32], mode_variable='cabinet:mode')
temperature_controller = TemperatureController(hvac_heat_port=hvac_port, temperature_setpoint_port=temperature_setpoint_port, state_model_nominal=nominal_state_model)

simulation = Simulation(dp, state_model_maker, control_ports=[hvac_port])
simulation.add_zone(zone_name='cabinet', heat_gain_name='cabinet:Pheat_gain', CO2production_name='PCO2cabinet', hvac_power_port=hvac_port, temperature_controller=temperature_controller)

# Initialize the power variable that the model expects
dp.add_external_variable('PZcabinet', dp.series('cabinet:Pheat_gain'))
simulation.run(suffix='_sim')

# #### PRINT THE SIMULATION RESULTS ####
preference = Preference(preferred_temperatures=(19, 24), extreme_temperatures=(16, 29), preferred_CO2_concentration=(500, 1500), temperature_weight_wrt_CO2=0.5, power_weight_wrt_comfort=0.5, mode_cop={1: 2, -1: 2})

print(simulation)
print(simulation.control_ports)
preference.print_assessment(dp.datetimes, dp.series('cabinet:Phvac'), dp.series('TZcabinet_sim'), dp.series('CCO2cabinet_sim'), dp.series('occupancy'))
dp.plot()
Phvac = dp.series('cabinet:Phvac')
electricity_needs = [abs(Phvac[k])/2 + occupancy[k] * occupant_consumption for k in dp.ks]
dp.add_external_variable('electricity needs', electricity_needs)

exposure_in_deg = 0
slope_in_deg = 180
solar_factor = .2
surface = 7
solar_system = SolarSystem(dp.solar_model)
Collector(solar_system, 'PVpanel', surface_m2=surface, exposure_deg=exposure_in_deg, slope_deg=slope_in_deg, solar_factor=solar_factor)
global_productions_in_Wh = solar_system.powers_W(gather_collectors=True)
print('PV production in kWh:', round(sum(global_productions_in_Wh) / 1000))
dp.add_external_variable('productionPV', global_productions_in_Wh)
dp.plot()

