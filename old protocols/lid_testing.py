from opentrons import protocol_api
from opentrons import types
import opentrons


metadata = {
    "protocolName": "lid testing",
    "author": "Nico To",
    "description": "lid testing",
}

requirements = {"robotType": "Flex", "apiLevel": "2.19"}


def run(protocol: protocol_api.ProtocolContext):
    sample_plate = protocol.load_labware("corning_96_wellplate_360ul_flat", "C2")
    lid = protocol.load_labware("corning_96_wellplate_360ul_flat", location= "C1")
    hs_mod = protocol.load_module(module_name="heaterShakerModuleV1", location="D1")    #heat shaker module

    hs_mod.open_labware_latch()
    # protocol.move_labware(labware=sample_plate, new_location=hs_mod, use_gripper=True)
    protocol.move_labware(labware=lid, new_location="D1", use_gripper=True)
