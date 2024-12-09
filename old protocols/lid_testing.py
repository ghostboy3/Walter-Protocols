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
    sample_plate = hs_mod.load_labware("corning_96_wellplate_360ul_flat")
    lid = protocol.load_labware("corning_96_wellplate_360ul_flat", location= "C1")
    lid.set_offset(x=0.00, y=0.00, z=-30)
    print(protocol.deck.__delitem__('D1'))
    # del protocol.deck['D1']
    # protocol.move_labware(labware=lid, new_location="C2", use_gripper=True)
    # del hs_mod.labware
    print(hs_mod.labware)
    
    # print(protocol.deck['D1'])
    # lid.set_offset(x=0.00, y=0.00)
    hs_mod.open_labware_latch()
    protocol.move_labware(lid, new_location=hs_mod, use_gripper=True)
    