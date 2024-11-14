metadata = {
    "protocolName": "Testing partial tip pickup",
    "author": "Nico To",
    "description": '''testing protocol''',
}

from opentrons import protocol_api
from opentrons.protocol_api import PARTIAL_COLUMN, ALL

requirements = {"robotType": "Flex", "apiLevel": "2.20"}

def run(protocol: protocol_api.ProtocolContext):
    partial_rack = protocol.load_labware(
        load_name="opentrons_flex_96_tiprack_1000ul",
        location="B2"
    )
    trash = protocol.load_trash_bin("A3")
    pipette = protocol.load_instrument("flex_8channel_1000", mount="right")
    pipette.configure_nozzle_layout(
        style=PARTIAL_COLUMN,
        start="H1",
        end="E1"
    )

    tips_by_row = partial_rack.rows_by_name()["D"] + partial_rack.rows_by_name()["H"]
    print(tips_by_row)

    # pick up A1-D1 from tip rack
    pipette.pick_up_tip(location=tips_by_row.pop(0))
    pipette.drop_tip()
    # pick up A2-D2 from tip rack
    pipette.pick_up_tip(location=tips_by_row.pop(0))
