from opentrons import protocol_api
# import requests
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
        default=50,
        minimum=1,
        maximum=1500,
        unit="µl"
    )
    parameters.add_int(
        variable_name="num_samples",
        display_name="number of samples",
        description="total number of samples",
        default=10,
        minimum=1,
        maximum=1000,     # change to 24 later (100 is for testing purposes)
        unit="samples"
    )
    parameters.add_int(
        variable_name="sample_in_solution_amt",
        display_name="sample in solution amount",
        description="amount of the peptide sample solution that needs to be added to the buffer in microlitres",
        default=5,
        minimum=1,
        maximum=100,
        unit="µl"
    )


# protocol run function
def run(protocol):
    # def send_command_to_raspberry_pi(command):
        # url = 'https://httpbin.org/post'#'http://<raspberry-pi-ip>:5000/command'
        # data = {'command': command}
        # response = requests.post(url)
        # if response.status_code == 200:
        #     protocol.comment('\n\n\n command sent successfully\n\n\n')
        # else:
        #     protocol.comment('\n\n\n command not sent successfully\n\n\n')

    def get_height(volume):
        '''
        Get's the height of the liquid in the tube
        Volume: volume of liquid in tube in µl
        Return: hieght from bottom of tube in millimeters
        '''
        height = 1
        # return 0.1
        
        #cylinder part
        if volume > 500:
            height= 0.015*volume+11.5
            height -= 4
            # return height

        elif volume <= 500 and volume >0:     # cone part aaa
            # volume = volume/1000
            height = -0.0000372 * (volume**2)+0.0491*volume+3.749 # y=-0.0000372x^{2}+0.0491x+3.749
            height -= 7
        if height < 0.1:
            return 0.1
        return height-0.2
    sample_in_solution_amt = protocol.params.sample_in_solution_amt    # amount of sample that goes into each solution in microlitres
    num_samples = protocol.params.num_samples
    
    # tips50 = [protocol.load_labware("opentrons_flex_96_filtertiprack_50uL", slot) for slot in ["A3"]]   # add more later
    tips1000 = [protocol.load_labware("opentrons_flex_96_filtertiprack_1000uL", slot) for slot in ["A3"]]   # add more later
    trash = protocol.load_waste_chute()

    left_pipette = protocol.load_instrument("flex_1channel_1000", "left", tip_racks=tips1000)
    # right_pipette = protocol.load_instrument("flex_8channel_50", "right", tip_racks=tips50)
    
    tube_rack = protocol.load_labware("opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap", "D2", "tube rack")
    # tube_rack["A1"].load_liquid(sample_sol, protocol.params.sample_stock_amt)
    sample_stock = tube_rack["D1"]
    amount_of_sample_remaining = protocol.params.sample_stock_amt
    left_pipette.pick_up_tip()
    for i in range (0, num_samples):
        amount_of_sample_remaining -= sample_in_solution_amt
        # protocol.comment("AAAAAAAAAA: " + str(get_height(amount_of_sample_remaining)))
        # print("AAAAAAAAAA: " + str(get_height(amount_of_sample_remaining)))
        protocol.comment("VOLUME: " + str(amount_of_sample_remaining))
        left_pipette.aspirate(sample_in_solution_amt, sample_stock.bottom(get_height(amount_of_sample_remaining)))
        # right_pipette.aspirate(sample_in_solution_amt, sample_stock.bottom(10))
        left_pipette.dispense(sample_in_solution_amt, tube_rack["D2"].top())
        left_pipette.blow_out(tube_rack["D2"].top())
    # send_command_to_raspberry_pi('start_experiment')

    left_pipette.return_tip()

