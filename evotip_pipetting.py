from opentrons import protocol_api
import math


metadata = {
    "protocolName": "EvoTip pipetting",
    "author": "Hugge Mann",
    "description": "Automating the pipetting for STrap",
}
requirements = {"robotType": "Flex", "apiLevel": "2.19"}

def get_height(volume):
    '''
    Get's the height of the liquid in the tube
    Volume: volume of liquid in tube in ml
    Return: hieght in millimeters
    '''
    if volume <= 1:     # cone part aaa
        # print(-3.33*(volume**2)+15.45*volume+9.50)
        return -3.33*(volume**2)+15.45*volume+9.50 - 1   #−3.33x2+15.45x+9.50
    else:
        return 6.41667*volume +15.1667
def add_parameters(parameters: protocol_api.Parameters):

    parameters.add_float(
        variable_name="buffer_stock_amt",
        display_name="buffer stock amount",
        description="amount of the buffer stock inside the falcon tube in ml",
        default=5,
        minimum=1,
        maximum=15,
        unit="ml"
    )
    parameters.add_int(
        variable_name="buffer_in_solution_amt",
        display_name="buffer in solution amount",
        description="amount of the buffer that needs to be added to each sample in microlitres",
        default=72,
        minimum=1,
        maximum=200,
        unit="µl"
    )
    parameters.add_int(
        variable_name="num_samples",
        display_name="number of samples",
        description="total number of samples",
        default=60,
        minimum=1,
        maximum=100,     # change to 24 later (100 is for testing purposes)
        unit="samples"
    )
# print(get_height(5))
def run(protocol: protocol_api.ProtocolContext):
    buffer_stock_amt = protocol.params.buffer_stock_amt            # amount of the buffer stock in ml
    buffer_in_solution_amt = protocol.params.buffer_in_solution_amt     # amount of buffer that goes into each solution in microlitres
    # sample_in_solution_amt = 8    # amount of sample that goes into each solution in microlitres
    num_samples = protocol.params.num_samples                 # total number of samples
    
    #loading stuff
    tips1000 = [protocol.load_labware("opentrons_flex_96_filtertiprack_1000uL", slot) for slot in ["A3","B3","C3"]]   # add more later
    # tips50 = [protocol.load_labware("opentrons_flex_96_filtertiprack_50uL", slot) for slot in ["B3"]]   # add more later
    reagent_rack = protocol.load_labware("opentrons_10_tuberack_falcon_4x50ml_6x15ml_conical", "D2", "reagent stock rack")
    # solution_rack = protocol.load_labware("opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap", "B2", "solution rack")
    # left_pipette = protocol.load_instrument("flex_1channel_1000", "left", tip_racks=tips1000)
    left_pipette = protocol.load_instrument("flex_1channel_1000", "left", tip_racks=tips1000)
    chute = protocol.load_waste_chute()

    #defining liquids
    buffer_a = protocol.define_liquid("Buffer A", "Buffer in 15ml falcon. 0.19 formic acid", "#969696")
    
    #loading liquids
    reagent_rack["A1"].load_liquid(buffer_a, buffer_stock_amt*1000)
    reagent_stock_storage = reagent_rack["C2"]
    left_pipette.pick_up_tip()

    for i in range (0, num_samples):
        amount_of_buffer_remaining = buffer_stock_amt*1000-(i*buffer_in_solution_amt)       # in ml
        protocol.comment(str(amount_of_buffer_remaining))
        left_pipette.aspirate(buffer_in_solution_amt, reagent_stock_storage.bottom(get_height((amount_of_buffer_remaining-buffer_in_solution_amt)/1000)-2))
        left_pipette.dispense(buffer_in_solution_amt, reagent_rack["C1"].top())
        left_pipette.blow_out()
        
    left_pipette.return_tip()