from opentrons import protocol_api
metadata = {
    "protocolName": "pipette 25ul testing",
    "author": "Nico To",
    "description": "pipette 25ul testing",
}
requirements = {"robotType": "Flex", "apiLevel": "2.19"}
def run(protocol: protocol_api.ProtocolContext):
    tips1000 = [protocol.load_labware("opentrons_flex_96_filtertiprack_1000uL", slot) for slot in ["A3"]]
    left_pipette = protocol.load_instrument("flex_1channel_1000", "left", tip_racks=tips1000)
    tube_rack = protocol.load_labware("opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap", "A2", "bead + final solution rack")
    water_storage = tube_rack["A1"]
    
    reagent_plate = protocol.load_labware("opentrons_96_wellplate_200ul_pcr_full_skirt", location="D2")
    for i in range (0,32):
        left_pipette.pick_up_tip()
        left_pipette.aspirate(25, water_storage)
        left_pipette.dispense(25, reagent_plate.wells()[i])
        left_pipette.blow_out(reagent_plate.wells()[i].top())
        left_pipette.return_tip()
