# D2 -> Reagent Rack, falcon tube in 

from opentrons import protocol_api
import math

metadata = {
    "protocolName": "Pre EvoTip pipetting",
    "author": "Nico To",
    "description": "Automating the pipetting for evotip loading.",
}
requirements = {"robotType": "Flex", "apiLevel": "2.19"}

def get_height_falcon(volume):
    '''
    Get's the height of the liquid in the tube
    Volume: volume of liquid in tube in ml
    Return: hieght in millimeters
    '''
    volume = volume/1000
    if volume <= 1:     # cone part aaa
        # print(-3.33*(volume**2)+15.45*volume+9.50)
        return -3.33*(volume**2)+15.45*volume+9.50 - 1   #−3.33x2+15.45x+9.50
    else:
        return 6.41667*volume +15.1667 -5
def get_height_smalltube(volume):
    '''
    Volume: amount of liquid in 1.5ml tube in µL
    Returns height in mm from the bottom of tube that pipette should go to
    '''  
    # volume = volume/1000
    if volume <= 500:     # cone part aaa
        volume = volume/1000
        return -26.8*(volume**2)+45.1*volume+3.98-4 #−26.80x2 +45.10x+3.98

    elif volume > 500:
        return 0.015*volume+11.5-1
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
        maximum=1000,
        unit="µl"
    )
    parameters.add_int(
        variable_name="sample_in_solution_amt",
        display_name="sample in solution amount",
        description="amount of the peptide sample solution that needs to be added to the buffer in microlitres",
        default=8,
        minimum=1,
        maximum=50,
        unit="µl"
    )
    # parameters.add_int(
    #     variable_name="sample_stock_amt",
    #     display_name="sample stock amount",
    #     description="amount of sample in each stock",
    #     default=100,
    #     minimum=5,
    #     maximum=1500,
    #     unit="µl"
    # )
    parameters.add_int(
        variable_name="num_samples",
        display_name="number of samples",
        description="total number of samples",
        default=5,
        minimum=1,
        maximum=24,     # change to 24 later (100 is for testing purposes)
        unit="samples"
    )
    parameters.add_bool(
        variable_name = "resuspend",
        display_name = "resuspend",
        description="do you want Walt to resuspend the peptides?",
        default = True
    )
    parameters.add_int(
        variable_name="resuspend_amt",
        display_name="Resuspend Amount",
        description="Amout of buffer that peptides are resuspended in or amount of buffer walt should resuspend in",
        default=15,
        minimum=1,
        maximum=1500,
        unit="µl"
    )
    parameters.add_bool(
        variable_name="dry_run",
        display_name="Dry Run",
        description="Skip incubation delays and return tips.",
        default=False
    )

# pipette speeds in µl/min
default_aspriate_speed = 300
default_dispense_speed = 500
slow_aspirate_speed = 300
slow_dispense_speed = 500

# print(get_height(5))
def run(protocol: protocol_api.ProtocolContext):
    buffer_stock_amt = protocol.params.buffer_stock_amt            # amount of the buffer stock in ml
    buffer_in_solution_amt = protocol.params.buffer_in_solution_amt     # amount of buffer that goes into each solution in microlitres
    sample_in_solution_amt = protocol.params.sample_in_solution_amt    # amount of sample that goes into each solution in microlitres
    sample_stock_amt = protocol.params.resuspend_amt        # amount of buffer in each peptide sample
    num_samples = protocol.params.num_samples                 # total number of samples
    
    #loading stuff
    tips1000 = [protocol.load_labware("opentrons_flex_96_filtertiprack_1000uL", slot) for slot in ["A3"]]   # add more later
    tips50 = [protocol.load_labware("opentrons_flex_96_filtertiprack_50uL", slot) for slot in ["B3"]]   # add more later
    reagent_rack = protocol.load_labware("opentrons_10_tuberack_falcon_4x50ml_6x15ml_conical", "D2", "reagent stock rack")
    sample_rack = protocol.load_labware("opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap", "C1", "peptide sample rack")
    solution_rack = protocol.load_labware("opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap", "C2", "final solution rack")
    # left_pipette = protocol.load_instrument("flex_1channel_1000", "left", tip_racks=tips1000)
    left_pipette = protocol.load_instrument("flex_1channel_1000", "left", tip_racks=tips1000)
    right_pipette = protocol.load_instrument("flex_1channel_50", "right", tip_racks=tips50)
    chute = protocol.load_waste_chute()

    #defining liquids
    buffer_a = protocol.define_liquid("Buffer A", "Buffer in 15ml falcon. 0.19 formic acid", "#969696")
    # sample_sol = protocol.define_liquid("Sample Solution", "Resuspended Peptide solution")
    
    #loading liquids
    reagent_rack["C2"].load_liquid(buffer_a, buffer_stock_amt*1000)
    reagent_stock_storage = reagent_rack["C2"]    
    def get_pipette(volume):
        if volume <=50:
            return right_pipette
        else:
            return left_pipette
    def remove_tip(pipette, is_dry_run):
        if is_dry_run:
            pipette.return_tip()
        else:
            pipette.drop_tip(chute)  
    amount_of_buffer_remaining = buffer_stock_amt*1000

    for i in range (0, num_samples):
        #respspending peptides
        if protocol.params.resuspend:
            for i in range (0, num_samples):
                amount_of_buffer_remaining-= sample_in_solution_amt
                get_pipette(sample_stock_amt).pick_up_tip()
                get_pipette(sample_stock_amt).aspirate(sample_stock_amt, reagent_stock_storage.bottom(get_height_falcon(amount_of_buffer_remaining)+1))
                get_pipette(sample_stock_amt).dispense(sample_stock_amt, sample_rack.wells()[i].bottom(1))
                # get_pipette(sample_stock_amt).mix(12, sample_stock_amt-3,sample_rack.wells()[i].bottom(1),2)
                get_pipette(sample_stock_amt).mix(3, sample_stock_amt-3,sample_rack.wells()[i].bottom(1),2)
                remove_tip(get_pipette(sample_stock_amt), protocol.params.dry_run)
        #loading sample
        right_pipette.pick_up_tip()
        protocol.comment("\n\n" + str(get_height_smalltube(sample_stock_amt-sample_in_solution_amt)) + "\n\n")
        protocol.comment("\n\n" + str(sample_stock_amt-sample_in_solution_amt) + "\n\n")

        right_pipette.aspirate(sample_in_solution_amt, sample_rack.wells()[i].bottom(0.1))#get_height_smalltube(sample_stock_amt-sample_in_solution_amt)))
        right_pipette.dispense(sample_in_solution_amt, solution_rack.wells()[i])
        right_pipette.blow_out(solution_rack.wells()[i].top())
        right_pipette.touch_tip()
        # right_pipette.return_tip()
        remove_tip(right_pipette, protocol.params.dry_run)
        
        #loading buffer
        amount_of_buffer_remaining -= buffer_in_solution_amt       # in ml
        left_pipette.pick_up_tip()
        left_pipette.aspirate(buffer_in_solution_amt, reagent_stock_storage.bottom(get_height_falcon((amount_of_buffer_remaining))+1))
        left_pipette.dispense(buffer_in_solution_amt, solution_rack.wells()[i])
        left_pipette.blow_out(solution_rack.wells()[i].top())
        left_pipette.flow_rate.aspirate = slow_aspirate_speed
        left_pipette.flow_rate.dispense = slow_dispense_speed
        left_pipette.mix(5, buffer_in_solution_amt-5, solution_rack.wells()[i].bottom(2))
        left_pipette.flow_rate.aspirate = default_aspriate_speed
        left_pipette.flow_rate.dispense = default_dispense_speed
        
        left_pipette.blow_out(solution_rack.wells()[i].top())
        left_pipette.touch_tip()
        left_pipette.blow_out(solution_rack.wells()[i].top())
        # left_pipette.return_tip()
        remove_tip(left_pipette, protocol.params.dry_run)