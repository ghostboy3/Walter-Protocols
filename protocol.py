from opentrons import protocol_api

# metadata
metadata = {
    "protocolName": "Testing Protocol",
    "author": "Hugge Mann",
    "description": "Hullo world!",
}

# requirements
requirements = {"robotType": "Flex", "apiLevel": "2.16"}


# protocol run function
def run(protocol):
    # protocol.comment("Testing")
    # labware
    # plate = protocol.load_labware(
    #         "opentrons_96_wellplate_200ul_pcr_full_skirt", location="B2"
    #     )
    tips1000 = [protocol.load_labware("opentrons_flex_96_filtertiprack_1000uL", slot) for slot in ["A3","B3","C3"]]

    trash = protocol.load_waste_chute()

    # # pipettes
    right_pipette = protocol.load_instrument("flex_8channel_1000", "right", tip_racks=tips1000)
    

    # left_pipette.pick_up_tip()
    # left_pipette.aspirate(50, plate["A1"].bottom(2))
    # left_pipette.dispense(50, plate["B2"].bottom(2))
    right_pipette.drop_tip(trash)
