from opentrons import protocol_api
from opentrons.protocol_api import PARTIAL_COLUMN, ALL, SINGLE

requirements = {"robotType": "Flex", "apiLevel": "2.20"}

metadata = {
    "protocolName": "Testing Partial pickup",
    "author": "Nico To",
    "description": "aaaaaaaaa",
}


def run(protocol: protocol_api.ProtocolContext):
    partial_rack = protocol.load_labware(
        load_name="opentrons_flex_96_tiprack_1000ul", location="A3"
    )
    tips1000 = [
        protocol.load_labware("opentrons_flex_96_filtertiprack_1000uL", slot)
        for slot in ["A3", "B3", "C3"]
    ]

    right_pipette = protocol.load_instrument(
        "flex_8channel_1000", mount="right", tip_racks=tips1000
    )

    right_pipette.configure_nozzle_layout(
        style=SINGLE,
        start="A1",
        # end="D1",
    )
    tips_by_row = sum(partial_rack.rows(), [])
    pipette.pick_up_tip(location=tips_by_row.pop(0))


    pipette.drop_tip()
    # pick up A2 from tip rack
    pipette.pick_up_tip(location=tips_by_row.pop(0))
