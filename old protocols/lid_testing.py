from opentrons import protocol_api
metadata = {
    "protocolName": "lid testing",
    "author": "Nico To",
    "description": "lid testing",
}

requirements = {"robotType": "Flex", "apiLevel": "2.19"}


def run(protocol: protocol_api.ProtocolContext):
    sample_plate = protocol.load_labware("corning_96_wellplate_360ul_flat", "C2")
    lid = protocol.load_labware("corning_96_wellplate_360ul_flat", location= "C1")
    protocol.move_labware(labware=lid, new_location="C2", use_gripper=True)
