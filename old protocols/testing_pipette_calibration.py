from opentrons import protocol_api

def add_parameters(parameters: protocol_api.Parameters):

    parameters.add_int(
        variable_name="numSamples",
        display_name="Number of Samples",
        description="Number of samples",
        default=16,
        minimum=1,
        maximum=100,
        unit="samples"
    )
    parameters.add_int(
        variable_name="tip_type",
        display_name="types of tips",
        choices=[
            {"display_name": "1000ul", "value": 1000},
            {"display_name": "200ul", "value": 200},
        ],
        default=200,
    )
    parameters.add_int(
        variable_name="mount",
        display_name="mount",
        choices=[
            {"display_name": "left", "value": 1},
            {"display_name": "right", "value": 2},
        ],
        default=2,
    )



metadata = {
    "protocolName": "Pipette 25ul Testing customisable",
    "author": "Nico To",
    "description": "pipette 25ul testing",
}
requirements = {"robotType": "Flex", "apiLevel": "2.21"}
def run(protocol: protocol_api.ProtocolContext):
    if protocol.params.tip_type == 1000:
        tips = [protocol.load_labware("opentrons_flex_96_filtertiprack_1000uL", slot) for slot in ["A3"]]
    else:
        tips = [protocol.load_labware("opentrons_flex_96_filtertiprack_200uL", slot) for slot in ["A3"]]
    if protocol.params.mount == 1:
        pipette = protocol.load_instrument("flex_1channel_1000", "left", tip_racks=tips)
    else:
        pipette = protocol.load_instrument("flex_1channel_1000", "right", tip_racks=tips)
    
    tube_rack = protocol.load_labware("opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap", "C2", "bead + final solution rack")
    water_storage = tube_rack["D1"]
    tips.set_offset(x=0.00, y=0.00, z=-6)
    
    reagent_plate = protocol.load_labware("opentrons_96_wellplate_200ul_pcr_full_skirt", location="D2")
    pipette.pick_up_tip()
    for i in range (0,protocol.params.numSamples):
        pipette.aspirate(25, water_storage.bottom(0.1), 0.3)
        pipette.dispense(25, reagent_plate.wells()[i])
        pipette.blow_out(reagent_plate.wells()[i].top())
    pipette.return_tip()
