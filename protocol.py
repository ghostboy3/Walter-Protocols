from opentrons import protocol_api

def add_parameters(parameters: protocol_api.Parameters):

    parameters.add_int(
        variable_name="amt",
        display_name="amount",
        description="just testing here",
        default=5,
        minimum=1,
        maximum=10,
        unit="µL"
    )


# metadata
metadata = {
    "protocolName": "My Protocol",
    "author": "Hugge Mann",
    "description": "Hullo world!",
}

# requirements
requirements = {"robotType": "Flex", "apiLevel": "2.19"}

# protocol run function
def run(protocol: protocol_api.ProtocolContext):
    protocol.comment("LESSGOOOO")
    # labware
    plate = protocol.load_labware(
            "corning_96_wellplate_360ul_flat", location="D1"
        )
    tiprack = protocol.load_labware(
            "opentrons_flex_96_tiprack_200ul", location="D2"
        )
    trash = protocol.load_trash_bin(location="A3")

        # pipettes
    left_pipette = protocol.load_instrument(
            "flex_1channel_1000", mount="left", tip_racks=[tiprack]
        )
    for i in range (1, protocol.params.amt+1):
        protocol.comment("RUN NUMBER " + str(i))
        # commands
        left_pipette.pick_up_tip()
        left_pipette.aspirate(100, plate["A1"])
        left_pipette.dispense(100, plate["B2"])
        left_pipette.drop_tip(trash)
