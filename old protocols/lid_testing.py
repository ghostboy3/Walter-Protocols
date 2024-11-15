from opentrons import protocol_api
from opentrons import types


metadata = {
    "protocolName": "SP3 HILIC protocol",
    "author": "Nico To",
    "description": "HILIC sp3 protocol",
}

requirements = {"robotType": "Flex", "apiLevel": "2.19"}


def run(protocol: protocol_api.ProtocolContext):
    sample_plate = protocol.load_labware("corning_96_wellplate_360ul_flat", "C2")
    lid = protocol.load_labware("corning_96_wellplate_360ul_flat", location= "C1")

    protocol.move_labware(labware=lid, new_location=sample_plate, use_gripper=True)
