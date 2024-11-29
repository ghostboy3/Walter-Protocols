from opentrons import protocol_api
metadata = {
    "protocolName": "lid testing",
    "author": "Nico To",
    "description": "lid testing",
}

requirements = {"robotType": "Flex", "apiLevel": "2.19"}
def add_parameters(parameters: protocol_api.Parameters):

    parameters.add_int(
        variable_name="z_offset",
        display_name="z offset",
        description="z offset",
        default=-50,
        minimum=-1000,
        maximum=1000,
        unit="mm"
    )


def run(protocol: protocol_api.ProtocolContext):
    # hs_mod = protocol.load_module(module_name="heaterShakerModuleV1", location="D1")    #heat shaker module
    # sample_plate = hs_mod.load_labware("corning_96_wellplate_360ul_flat")
    # lid = protocol.load_labware("corning_96_wellplate_360ul_flat", location= "C1")
    # lid.set_offset(x=0.00, y=0.00, z=30)
    # print(protocol.deck.__delitem__(hs_mod.))
    # protocol.move_labware(labware=lid, new_location="C2", use_gripper=True)

    hs_mod = protocol.load_module(module_name="heaterShakerModuleV1", location="D1")    #heat shaker module
    sample_plate = hs_mod.load_labware("corning_96_wellplate_360ul_flat")
    lid = protocol.load_labware("corning_96_wellplate_360ul_flat", location= "C1")
    lid.set_offset(x=0.00, y=0.00, z=0)
    print(protocol.deck.__delitem__('D1'))
    # del protocol.deck['D1']
    # protocol.move_labware(labware=lid, new_location="C2", use_gripper=True)
    # del hs_mod.labware
    print(hs_mod.labware)
    # print(protocol.deck['D1'])
    # lid.set_offset(x=0.00, y=0.00)
    hs_mod.open_labware_latch()
    # lid.set_offset(0,0,z=protocol.params.z_offset)
    # protocol.move_labware(lid, new_location=hs_mod, use_gripper=True)
    