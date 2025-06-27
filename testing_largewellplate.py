from opentrons import protocol_api

from opentrons import types
metadata = {
    "protocolName": "Testing Large Well Plate",
    "author": "Nico To",
    "description": "Testing a large well plate with a 96-well format, V bottom",
}

requirements = {"robotType": "Flex", "apiLevel": "2.20"}

def run(protocol: protocol_api.ProtocolContext):
    reagent_plate = protocol.load_labware("opentrons_96_wellplate_200ul_pcr_full_skirt","A2","reagent plate")
    reagent_plate.set_offset(x=0, y=0, z=-4.1)
    tips200 = [protocol.load_labware("opentrons_flex_96_filtertiprack_200uL", "A3")]
    left_pipette = protocol.load_instrument("flex_1channel_1000", "left", tip_racks=tips200)
    left_pipette.pick_up_tip()
    left_pipette.aspirate(100, reagent_plate.wells_by_name()["A1"].bottom(0.1))
    left_pipette.return_tip()