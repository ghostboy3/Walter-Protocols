from opentrons import protocol_api

def add_parameters(parameters: protocol_api.Parameters):

    parameters.add_int(
        variable_name="numSamples",
        display_name="Number of Samples",
        description="Number of samples",
        default=32,
        minimum=1,
        maximum=100,
        unit="samples"
    )

metadata = {
    "protocolName": "Pipette 25ul 100 flow rate",
    "author": "Nico To",
    "description": "pipette 25ul testing",
}
requirements = {"robotType": "Flex", "apiLevel": "2.21"}
def run(protocol: protocol_api.ProtocolContext):
    tips = [protocol.load_labware("opentrons_flex_96_filtertiprack_1000uL", slot) for slot in ["A3"]]
    pipette = protocol.load_instrument("flex_1channel_1000", "left", tip_racks=tips)
    
    tube_rack = protocol.load_labware("opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap", "C2", "bead + final solution rack")
    water_storage = tube_rack["A1"]
    
    
    reagent_plate = protocol.load_labware("opentrons_96_wellplate_200ul_pcr_full_skirt", location="D2")
    pipette.pick_up_tip()
    for i in range (0,protocol.params.numSamples):
        pipette.aspirate(25, water_storage.bottom(0.1))
        pipette.dispense(25, reagent_plate.wells()[i])
        pipette.blow_out(reagent_plate.wells()[i].top())
    pipette.return_tip()
