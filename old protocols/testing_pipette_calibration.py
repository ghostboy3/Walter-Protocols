from opentrons import protocol_api
metadata = {
    "protocolName": "pipette 25ul testing.",
    "author": "Nico To",
    "description": "lid testing",
}
requirements = {"robotType": "Flex", "apiLevel": "2.19"}
def run(protocol: protocol_api.ProtocolContext):
    tips1000 = [protocol.load_labware("opentrons_flex_96_filtertiprack_1000uL", slot) for slot in ["A3"]]
    left_pipette = protocol.load_instrument("flex_1channel_1000", "left", tip_racks=tips1000)
    right_pipette = protocol.load_instrument("flex_8channel_1000", "right", tip_racks=tips1000)
    # tube_rack = protocol.load_labware("opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap", "A2", "bead + final solution rack")
    # bead_storage = tube_rack["A1"]
    water_storage = protocol.load_labware("nest_96_wellplate_2ml_deep", location= "C2")
    
    hs_mod = protocol.load_module(module_name="heaterShakerModuleV1", location="D1")    #heat shaker module
    reagent_plate = protocol.load_labware("opentrons_96_wellplate_200ul_pcr_full_skirt", location="D2")
    hs_mod.open_labware_latch()
    hs_mod.close_labware_latch()
    right_pipette.pick_up_tip()
    for i in range (0,32):
        right_pipette.aspirate(25, water_storage['A1'])
        right_pipette.dispense(25, reagent_plate['A1'].top(-3))
        right_pipette.blow_out(reagent_plate['A1'].top())
    right_pipette.return_tip()
