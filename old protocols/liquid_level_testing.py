from opentrons import protocol_api
metadata = {
    "protocolName": "Testing Liquid Level Detection",
    "author": "Nico To and my boi walt",
    "description": "HILIC sp3 protocol",
}
requirements = {"robotType": "Flex", "apiLevel": "2.19"}

def run(protocol: protocol_api.ProtocolContext):
    tips1000 = [protocol.load_labware("opentrons_flex_96_filtertiprack_1000uL", slot) for slot in ["A3"]]
    left_pipette = protocol.load_instrument("flex_1channel_1000", "left", tip_racks=tips1000)
    tube_rack = protocol.load_labware("opentrons_10_tuberack_falcon_4x50ml_6x15ml_conical", "D2", "tube rack")
    falcon_tube = tube_rack.wells_by_name()['A1']
    water = protocol.define_liquid("water", "just water", "#32a852")
    falcon_tube.load_liquid(water, 10000)   # load 10ml of water into falcon
    
    left_pipette.pick_up_tip()
    left_pipette.aspirate(100, falcon_tube)
    left_pipette.dispense(100, falcon_tube.top())
    left_pipette.return_tip()
    
