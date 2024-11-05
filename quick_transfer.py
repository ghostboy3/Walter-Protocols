# D2 -> Reagent Rack, falcon tube in

from opentrons import protocol_api
import math

metadata = {
    "protocolName": "The Better Quick Transfer 😎",
    "author": "Nico To",
    "description": "Replica of the quick transfer function that actually works",
}
requirements = {"robotType": "Flex", "apiLevel": "2.19"}


def get_height_falcon(volume):
    """
    Get's the height of the liquid in the tube
    Volume: volume of liquid in tube in ml
    Return: hieght in millimeters
    """
    volume = volume / 1000
    if volume <= 1:  # cone part aaa
        # print(-3.33*(volume**2)+15.45*volume+9.50)
        return -3.33 * (volume**2) + 15.45 * volume + 9.50 - 1  # −3.33x2+15.45x+9.50
    else:
        return 6.41667 * volume + 15.1667 - 5


def get_height_smalltube(volume):
    """
    Volume: amount of liquid in 1.5ml tube in µL
    Returns height in mm from the bottom of tube that pipette should go to
    """
    return 0.5
    # volume = volume/1000
    if volume <= 500:  # cone part aaa
        volume = volume / 1000
        return -26.8 * (volume**2) + 45.1 * volume + 3.98 - 4  # −26.80x2 +45.10x+3.98

    elif volume > 500:
        return 0.015 * volume + 11.5 - 1


def add_parameters(parameters: protocol_api.Parameters):

    parameters.add_str(
        variable_name="start_tube_type",
        display_name="Start Tube Type",
        description="1.5ml tube, 15ml falcon, or 50ml falcon",
        default="onefive_tube",
        choices=[
            {"display_name": "1.5 ml ", "value": "onefive_tube"},
            {"display_name": "15 ml", "value": "fifteen_falcon"},
            {"display_name": "50 ml", "value": "fifty_falcon"},
        ],
    )
    parameters.add_str(
        variable_name="finalsample_tube_type",
        display_name="Final Sample Tube Type",
        description="PCR or 1.5ml tube",
        default="onefive_tube",
        choices=[
            {"display_name": "1.5 ml ", "value": "onefive_tube"},
            {"display_name": "PCR", "value": "pcr"},
        ],
    )

    parameters.add_float(
        variable_name="start_tube_volume",
        display_name="Start Tube Volume",
        description="Amount of liquid in the start tube",
        default=5,
        minimum=0,
        maximum=50,
        unit="ml",
    )
    parameters.add_float(
        variable_name="end_tube_volume",
        display_name="End Tube Volume",
        description="amount in the final tubes",
        default=5,
        minimum=1,
        maximum=1500,
        unit="µl",
    )
    parameters.add_int(
        variable_name="num_samples",
        display_name="number of samples",
        description="total number of samples",
        default=5,
        minimum=1,
        maximum=96,  # change to 24 later (100 is for testing purposes)
        unit="samples",
    )
    parameters.add_bool(
        variable_name="dry_run",
        display_name="Dry Run",
        description="Skip incubation delays and return tips.",
        default=True,
    )



# print(get_height(5))
def run(protocol: protocol_api.ProtocolContext):
    start_tube_volume = (
        protocol.params.start_tube_volume
    )  # amount of the buffer stock in ml
    end_tube_volume = (
        protocol.params.end_tube_volume
    )  # amount of buffer that goes into each solution in microlitres
    num_samples = protocol.params.num_samples  # total number of samples

    start_tube_type  = protocol.params.start_tube_type
    finalsample_tube_type = protocol.params.finalsample_tube_type
    transfer_vol = protocol.params.end_tube_volume

    # loading stuff
    tips1000 = [
        protocol.load_labware("opentrons_flex_96_filtertiprack_1000uL", slot)
        for slot in ["A3"]
    ]  # add more later
    tips50 = [
        protocol.load_labware("opentrons_flex_96_filtertiprack_50uL", slot)
        for slot in ["B3"]
    ]  # add more later
    
    if start_tube_type == "fifteen_falcon" or start_tube_type =="fifty_falcon":
        reagent_rack = protocol.load_labware(
            "opentrons_10_tuberack_falcon_4x50ml_6x15ml_conical", "D2", "reagent stock rack"
        )
        reagent_stock_storage = reagent_rack["A1"]      # change for 50 ml falcon later
    else:
        reagent_rack = protocol.load_labware(
            "opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap", "D2", "reagent stock rack"
        )
        reagent_stock_storage = reagent_rack["A1"]
    
    if finalsample_tube_type == "onefive_tube":
        sample_rack = protocol.load_labware(
            "opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap",
            "C1",
            "peptide sample rack",
        )
    else:
        sample_rack = protocol.load_labware(
            "opentrons_96_wellplate_200ul_pcr_full_skirt",
            "C1",
            "peptide sample rack",
        )
    if protocol.params.finalsample_tube_type == "onefive_tube":
        solution_rack = protocol.load_labware(
            "opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap",
            "C2",
            "final solution rack",
        )
    else:
        solution_rack = protocol.load_labware(
            "opentrons_96_wellplate_200ul_pcr_full_skirt",
            "C2",
            "final solution rack",
        )
    # left_pipette = protocol.load_instrument("flex_1channel_1000", "left", tip_racks=tips1000)
    left_pipette = protocol.load_instrument(
        "flex_1channel_1000", "left", tip_racks=tips1000
    )
    right_pipette = protocol.load_instrument(
        "flex_1channel_50", "right", tip_racks=tips50
    )
    chute = protocol.load_waste_chute()

    def get_pipette(volume):
        if volume <= 5:
            return right_pipette
        else:
            return left_pipette

    def remove_tip(pipette, is_dry_run):
        if is_dry_run:
            pipette.return_tip()
        else:
            pipette.drop_tip(chute)

    amount_of_reagant_remaining = protocol.params.start_tube_volume * 1000
    for i in range (0, num_samples):
        pipette = get_pipette(transfer_vol)
        pipette.pick_up_tip()
        pipette.aspirate(transfer_vol, reagent_stock_storage.bottom(get_height_falcon(amount_of_reagant_remaining)))
        pipette.dispense(transfer_vol, sample_rack.wells()[i].bottom(0.1))
        pipette.blow_out(sample_rack.wells()[i].top())
        pipette.touch_tip()
        remove_tip(pipette, protocol.params.dry_run)