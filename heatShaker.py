from opentrons import protocol_api

metadata = {
    "protocolName": "Shakey Shakey",
    "author": "Hugge Mann",
    "description": "1000rpm for 1min at 37 deg temp",
}
requirements = {"robotType": "Flex", "apiLevel": "2.19"}

def add_parameters(parameters: protocol_api.Parameters):

    parameters.add_int(
        variable_name="minutes",
        display_name="Number of Minutes",
        description="Number of minutes it should shake for",
        default=1,
        minimum=1,
        maximum=100,
        unit="min"
    )
    parameters.add_int(
        variable_name="temp",
        display_name="Temperature",
        description="Shaking temperature in degrees Celcius",
        default=22,
        minimum=1,
        maximum=95,
        unit="°C"
    )
def run(protocol: protocol_api.ProtocolContext):
    hs_mod = protocol.load_module(module_name="heaterShakerModuleV1", location="D1")    #heat shaker module
    hs_mod.close_labware_latch()
    hs_mod.set_and_wait_for_shake_speed(1000)       #1000 rpm
    if protocol.params.temp >=37 and protocol.params.temp <=95:
        hs_mod.set_and_wait_for_temperature(protocol.params.temp)
    protocol.delay(minutes=protocol.params.minutes, msg= str(str(protocol.params.minutes) + " minute incubation"))
    # deactivating heat shaker
    hs_mod.deactivate_shaker()
    hs_mod.deactivate_heater()
    hs_mod.open_labware_latch()