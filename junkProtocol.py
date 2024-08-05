from opentrons import protocol_api

# metadata
metadata = {
    "protocolName": "1.5ml tube testing Protocol",
    "author": "Hugge Mann",
    "description": "Hullo world!",
}
requirements = {"robotType": "Flex", "apiLevel": "2.19"}

# requirements
# requirements = {"robotType": "Flex", "apiLevel": "2.16"}
def add_parameters(parameters: protocol_api.Parameters):
    parameters.add_float(
        variable_name="sample_stock_amt",
        display_name="sample stock amount",
        description="amount of the protein sample inside the 1.5 ml tubes",
        default=500,
        minimum=1,
        maximum=1500,
        unit="µl"
    )
    parameters.add_int(
        variable_name="num_samples",
        display_name="number of samples",
        description="total number of samples",
        default=20,
        minimum=1,
        maximum=100,     # change to 24 later (100 is for testing purposes)
        unit="samples"
    )
    parameters.add_int(
        variable_name="sample_in_solution_amt",
        display_name="sample in solution amount",
        description="amount of the peptide sample solution that needs to be added to the buffer in microlitres",
        default=15,
        minimum=1,
        maximum=50,
        unit="µl"
    )
def get_height(volume):
    '''
    Get's the height of the liquid in the tube
    Volume: volume of liquid in tube in µl
    Return: hieght from top of tube in millimeters
    '''
    volume = volume/1000
    if volume <= 500:     # cone part aaa
        # print(-3.33*(volume**2)+15.45*volume+9.50)
        return 26.7963 * (volume**2) - 45.1042*volume + 36.0163 +1#26.7963x2 −45.1042x+36.0163
    elif volume > 500:
        return -15*(volume) + 27.5
# protocol run function
def run(protocol):
    sample_in_solution_amt = protocol.params.sample_in_solution_amt    # amount of sample that goes into each solution in microlitres
    num_samples = protocol.params.num_samples
    
    tips1000 = [protocol.load_labware("opentrons_flex_96_filtertiprack_1000uL", slot) for slot in ["A3"]]   # add more later
    tips50 = [protocol.load_labware("opentrons_flex_96_filtertiprack_50uL", slot) for slot in ["B3"]]   # add more later
    trash = protocol.load_waste_chute()

    left_pipette = protocol.load_instrument("flex_1channel_1000", "left", tip_racks=tips1000)
    right_pipette = protocol.load_instrument("flex_1channel_50", "right", tip_racks=tips50)
    
    tube_rack = protocol.load_labware("opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap", "D2", "tube rack")
    sample_sol = protocol.define_liquid("Sample Solution", "sample solution in the 1.5ml tubes", "#969696")
    # tube_rack["A1"].load_liquid(sample_sol, protocol.params.sample_stock_amt)
    sample_stock = tube_rack["D1"]
    amount_of_sample_remaining = protocol.params.sample_stock_amt
    right_pipette.pick_up_tip()
    for i in range (0, num_samples):
        amount_of_sample_remaining -= sample_in_solution_amt
        protocol.comment("AAAAAAAAAA: " + str(get_height(amount_of_sample_remaining)))
        protocol.comment("VOLUME: " + str(amount_of_sample_remaining))
        right_pipette.aspirate(sample_in_solution_amt, sample_stock.top(-get_height(amount_of_sample_remaining)))
        right_pipette.dispense(sample_in_solution_amt, tube_rack["D2"].top())
        right_pipette.blow_out(tube_rack["D2"].top())
    right_pipette.return_tip()
