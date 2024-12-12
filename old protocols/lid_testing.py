from opentrons import protocol_api
metadata = {
    "protocolName": "lid testing",
    "author": "Nico To",
    "description": "lid testing",
}

requirements = {"robotType": "Flex", "apiLevel": "2.19"}

def run(protocol: protocol_api.ProtocolContext):
    # MOVING LID ONTO LOCATION C2
    # sample_plate = protocol.load_labware("corning_96_wellplate_360ul_flat", "C2")
    # lid = protocol.load_labware("corning_96_wellplate_360ul_flat", location= "C1")
    # lid.set_offset(x=0.00, y=0.00, z=30)
    # protocol.deck.__delitem__('C2')
    # protocol.move_labware(labware=lid, new_location="C2", use_gripper=True)


    # MOVING LID ONTO HEAT SHAKER (DOES NOT WORK)
    hs_mod = protocol.load_module(module_name="heaterShakerModuleV1", location="D1")    #heat shaker module
    sample_plate = protocol.load_labware("opentrons_96_wellplate_200ul_pcr_full_skirt", "C2")
    lid = protocol.load_labware("opentrons_tough_pcr_auto_sealing_lid", location= "C1")
    hs_mod.open_labware_latch()
    protocol.move_labware(labware=sample_plate, new_location=hs_mod, use_gripper=True)
    sample_plate.set_offset(x=0.00, y=0.00, z=30)
    hs_mod.close_labware_latch()
    hs_mod.open_labware_latch()
    protocol.move_labware(labware=lid, new_location=sample_plate, use_gripper=True)
    protocol.move_labware(labware=lid, new_location='C1', use_gripper=True)
    protocol.move_labware(labware=sample_plate, new_location='C2', use_gripper=True)