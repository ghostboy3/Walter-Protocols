# CHANGE TITLE IF NEEDED IN PROTOCOL NAME
metadata = {
    "protocolName": "BCA protocol",
    "author": "Sasha",
    "description": "First Used Tip box is in position A3; Place Empty 1.5 mL Tubes in slots B1-C1 for standards, BSA Standard (2mg/mL) should be added to a 1.5 mL tube, need 550µL; 100µL of each unknown sample should be aliquoted to the sample stock plate going down a column starting at A1 "
    "calculate volumes needed of reagent A and B before hand to fill falcon tube and microcentrifuge tube with the appropriate volumes, reagent A should not exceed 20 mL, Reagent A Loading should be 200µL * ((number of columns +1) * 8)+8), Reagent B should be Reagent A Volume / 50 ",
}
requirements = {"robotType": "Flex", "apiLevel": "2.18"}

start_pos = 24  # where the samples will be loaded on the 96-well plate going down a column (after 3 reps of 8 standards )

import math
from opentrons import protocol_api
from opentrons import protocol_engine
from opentrons import types

####CHANGE NUMBER OF SAMPLES HERE####

# def mixing(volume, location):
# right_pipette.pick_up_tip()
# right_pipette.mix(5, volume, location)
# right_pipette.drop_tip(chute)


def add_parameters(parameters):

    parameters.add_int(
        variable_name="number_samples",
        display_name="number_samples",
        description="Number of input samples.",
        default=1,
        minimum=1,
        maximum=24,
        unit="samples",
    )


def run(protocol: protocol_api.ProtocolContext):

    number_samples = protocol.params.number_samples
    # LOADING TIPS
    tips200 = [
        protocol.load_labware("opentrons_flex_96_filtertiprack_1000uL", slot)
        for slot in ["A3", "B3", "C3"]
    ]
    chute = protocol.load_waste_chute()

    # LOADING PIPETTES
    left_pipette = protocol.load_instrument(
        "flex_1channel_1000", "left", tip_racks=tips200
    )
    right_pipette = protocol.load_instrument(
        "flex_8channel_1000", "right", tip_racks=tips200
    )

    # LOADING LABWARE
    working_reagent_reservoir = protocol.load_labware("nest_12_reservoir_15ml", "B1")
    heatshaker = protocol.load_module("heaterShakerModuleV1", "D1")
    sample_plate = protocol.load_labware("corning_96_wellplate_360ul_flat", "C2")
    reagent_stock = protocol.load_labware(
        "opentrons_10_tuberack_falcon_4x50ml_6x15ml_conical", "A1"
    )
    lid = protocol.load_labware("opentrons_tough_pcr_auto_sealing_lid", location= "C1")
    sample_stock = protocol.load_labware(
        "opentrons_96_wellplate_200ul_pcr_full_skirt", "B2"
    )
    staging_slots = ["A4", "B4", "C4"]
    staging_racks = [
        protocol.load_labware("opentrons_flex_96_filtertiprack_1000uL", slot)
        for slot in staging_slots
    ]

    # REPLENISHING TIPS

    count = 0
    # DEFINING LIQUIDS
    bsa_stock = protocol.define_liquid(
        "BSA Stock", "BSA Stock from Pierce BCA Protein protocol ; 2mg/mL", "#FF6433"
    )
    bsa_plate = protocol.load_labware(
        "opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap", "A2"
    )

    Reagent_A = protocol.define_liquid(
        "Reagent_A", "Reagent A for Working Reagent, will add 50 parts", "#FDF740"
    )
    Reagent_B = protocol.define_liquid(
        "Reagent_B", "Reagent B for Working Reagent, will add 1 part", "#408AFD"
    )

    water = protocol.define_liquid(
        "Diluent", "Diluent for standards, same as diluent in sample", "#D2E2FB"
    )

    sample = protocol.define_liquid(
        "sample",
        "Unknown Samples from CSV File",
        "#40FDF4",
    )

    empty_tube = protocol.define_liquid("empty", "Empty Tubes for Standards", "#D3D3D3")

    # LOADING LIQUIDS
    reagent_stock["A1"].load_liquid(water, 9000)
    bsa_plate["A1"].load_liquid(bsa_stock, 550)
    reagent_stock["A3"].load_liquid(Reagent_A, 22000)
    bsa_plate["D1"].load_liquid(Reagent_B, 1000)
    bsa_plate["B1"].load_liquid(empty_tube, 1)  # 1500 µg/mL
    bsa_plate["B2"].load_liquid(empty_tube, 1)  # 1000 µg/mL
    bsa_plate["B3"].load_liquid(empty_tube, 1)  # 750 µg/mL
    bsa_plate["B4"].load_liquid(empty_tube, 1)  # 500 µg/mL
    bsa_plate["B5"].load_liquid(empty_tube, 1)  # 250 µg/mL
    bsa_plate["B6"].load_liquid(empty_tube, 1)  # 125 µg/mL
    bsa_plate["C1"].load_liquid(empty_tube, 1)  # 25 µg/mL

    # LOADING SAMPLES AND TRANSFERING TO SAMPLE PLATE
    drop_off = start_pos
    pick_up = 0

    while pick_up < number_samples:
        well = sample_stock.wells()[pick_up]
        well.load_liquid(sample, 100)

        left_pipette.pick_up_tip()
        left_pipette.aspirate(80, well.bottom(2), 0.5)

        for i in range(0, 3):
            left_pipette.dispense(
                25, sample_plate.wells()[drop_off + i].bottom(0), rate=0.25
            )

        left_pipette.drop_tip(chute)

        drop_off += 3
        pick_up += 1

    # Standard Preparation

    # Vial A : 1500 µg/mL -former vial B

    left_pipette.pick_up_tip()
    left_pipette.aspirate(187.5, bsa_plate["A1"].bottom(2))
    left_pipette.dispense(187.5, bsa_plate["B1"].bottom(4), rate=0.75)
    left_pipette.touch_tip()
    left_pipette.drop_tip(chute)

    left_pipette.pick_up_tip()
    left_pipette.aspirate(62.5, reagent_stock["A1"].bottom(2))
    left_pipette.dispense(62.5, bsa_plate["B1"].bottom(4), rate=0.75)
    left_pipette.mix(3, 100, bsa_plate["B1"].bottom(4))
    left_pipette.touch_tip()
    left_pipette.drop_tip(chute)

    # Vial B : 1000 µg/mL - former vial C

    left_pipette.pick_up_tip()
    left_pipette.aspirate(162.5, bsa_plate["A1"].bottom(2))
    left_pipette.dispense(162.5, bsa_plate["B2"].bottom(4), rate=0.75)
    left_pipette.touch_tip()
    left_pipette.drop_tip(chute)

    left_pipette.pick_up_tip()
    left_pipette.aspirate(162.5, reagent_stock["A1"].bottom(25))
    left_pipette.touch_tip()
    left_pipette.dispense(162.5, bsa_plate["B2"].bottom(4), rate=0.75)
    left_pipette.mix(3, 140, bsa_plate["B2"].bottom(4))
    left_pipette.touch_tip()
    left_pipette.drop_tip(chute)

    # Vial C : 750 µg/mL - former vial D

    left_pipette.pick_up_tip()
    left_pipette.aspirate(87.5, reagent_stock["A1"].bottom(25))
    left_pipette.dispense(87.5, bsa_plate["B3"].bottom(4), rate=0.75)
    left_pipette.touch_tip()
    left_pipette.drop_tip(chute)

    left_pipette.pick_up_tip()
    left_pipette.aspirate(87.5, bsa_plate["B1"].bottom(4))  # Vial A to C (1500 to 750)
    left_pipette.touch_tip()
    left_pipette.dispense(87.5, bsa_plate["B3"].bottom(4), rate=0.75)
    left_pipette.mix(3, 50, bsa_plate["B3"].bottom(4))
    left_pipette.touch_tip()
    left_pipette.drop_tip(chute)

    # Vial D, E, F

    vials = [
        bsa_plate["B4"].bottom(4),
        bsa_plate["B5"].bottom(4),
        bsa_plate["B6"].bottom(4),
    ]

    for vial in vials:
        left_pipette.pick_up_tip()
        left_pipette.aspirate(162.5, reagent_stock["A1"].bottom(25))
        left_pipette.touch_tip()
        left_pipette.dispense(162.5, vial, rate=0.25)
        left_pipette.touch_tip()
        left_pipette.drop_tip(chute)

    # Vial D : 500 µg/mL - former vial E

    left_pipette.pick_up_tip()
    left_pipette.aspirate(162.5, bsa_plate["B2"].bottom(2))  # Vial B to D
    left_pipette.dispense(162.5, bsa_plate["B4"].bottom(4), rate=0.75)
    left_pipette.mix(3, 150, bsa_plate["B4"].bottom(4))
    left_pipette.touch_tip()
    left_pipette.drop_tip(chute)

    # Vial E: 250 µg/mL - Former vial F

    left_pipette.pick_up_tip()
    left_pipette.aspirate(162.5, bsa_plate["B4"].bottom(2))  # Vial D to E
    left_pipette.dispense(162.5, bsa_plate["B5"].bottom(4), rate=0.75)
    left_pipette.mix(3, 150, bsa_plate["B5"].bottom(4))
    left_pipette.touch_tip()
    left_pipette.drop_tip(chute)

    # Vial F : 125 µg/mL - former vial G

    left_pipette.pick_up_tip()
    left_pipette.aspirate(162.5, bsa_plate["B5"].bottom(2))
    left_pipette.dispense(162.5, bsa_plate["B6"].bottom(4), rate=0.75)
    left_pipette.mix(3, 150, bsa_plate["B6"].bottom(4))
    left_pipette.touch_tip()
    left_pipette.drop_tip(chute)

    # Vial G : 25 µg/mL - former vial F

    left_pipette.pick_up_tip()
    left_pipette.aspirate(200, reagent_stock["A1"].bottom(25))
    left_pipette.touch_tip()
    left_pipette.dispense(200, bsa_plate["C1"].bottom(4), rate=0.75)
    left_pipette.touch_tip()
    left_pipette.drop_tip(chute)

    left_pipette.pick_up_tip()
    left_pipette.aspirate(50, bsa_plate["B6"].bottom(2))
    left_pipette.dispense(50, bsa_plate["C1"].bottom(4), rate=0.75)
    left_pipette.mix(3, 100, bsa_plate["C1"].bottom(4))
    left_pipette.touch_tip()
    left_pipette.drop_tip(chute)

    # Standard Loading

    def standard_loading(old, new):
        '''
        old: well from sample stock
        new: row letter from sample plate
        '''
        left_pipette.pick_up_tip()
        left_pipette.aspirate(80, bsa_plate[old].bottom(1.5), 0.25)
        
        for i in range(1, 4):  # A1,A2,A3
            left_pipette.dispense(25, sample_plate[new + str(i)].bottom(0), 0.25)
        left_pipette.drop_tip(chute)

    # Vial A
    standard_loading("B1", "A")
    
    # Vial B
    standard_loading("B2", "B")

    # Vial C
    standard_loading("B3", "C")

    # Vial D
    standard_loading("B4", "D")

    # Vial E
    standard_loading("B5", "E")

    # Vial F
    standard_loading("B6", "F")

    # Vial G
    standard_loading("C1", "G")

    # Vial H
    # Blank
    left_pipette.pick_up_tip()
    left_pipette.aspirate(80, reagent_stock["A1"].bottom(20), 0.25)
    for i in range(1, 4):  # A1,A2,A3
        left_pipette.dispense(25, sample_plate["H" + str(i)].bottom(8), 0.25)
    left_pipette.drop_tip(chute)
    

    # Working Reagent Solution Prep
    num_columns = math.ceil(((number_samples + 8) * 3) / 8)
    working_reagent_volume = 200
    reagent_A_volume = working_reagent_volume * (((num_columns + 1) * 8) + 4)
    reagent_B_volume = reagent_A_volume / 50
    total_working_reagent_volume = reagent_A_volume + reagent_B_volume

    max_volume = 14000
    max_reservoir = 11000
    remainder = reagent_A_volume - max_reservoir
    if total_working_reagent_volume <= max_volume:
        left_pipette.transfer(
            reagent_A_volume,
            reagent_stock["A3"].bottom(5),
            working_reagent_reservoir["A1"].bottom(15),
            touch_tip=True,
            blow_out=True,
            blowout_location="destination well",
        )
        left_pipette.transfer(
            reagent_B_volume,
            bsa_plate["D1"].bottom(1),
            working_reagent_reservoir["A1"].bottom(15),
            touch_tip=True,
        )

    else:
        left_pipette.transfer(
            max_reservoir,
            reagent_stock["A3"].bottom(5),
            working_reagent_reservoir["A1"].bottom(15),
            touch_tip=True,
            blow_out=True,
            blowout_location="destination well",
        )
        left_pipette.transfer(
            (remainder),
            reagent_stock["A3"].bottom(5),
            working_reagent_reservoir["A2"].bottom(15),
            touch_tip=True,
            blow_out=True,
            blowout_location="destination well",
        )

        left_pipette.transfer(
            max_reservoir / 50,
            bsa_plate["D1"].bottom(1),
            working_reagent_reservoir["A1"].bottom(15),
            touch_tip=True,
        )
        left_pipette.transfer(
            (remainder / 50),
            bsa_plate["D1"].bottom(1),
            working_reagent_reservoir["A2"].bottom(15),
            touch_tip=True,
        )

    if max_volume >= total_working_reagent_volume >= 9000:
        right_pipette.pick_up_tip()
        right_pipette.mix(5, 1000, working_reagent_reservoir["A1"].bottom(4))
        right_pipette.drop_tip(chute)

    elif total_working_reagent_volume > max_volume:
        if remainder > 9000:
            right_pipette.pick_up_tip()
            right_pipette.mix(5, 1000, working_reagent_reservoir["A1"].bottom(4))
            right_pipette.drop_tip(chute)
            right_pipette.pick_up_tip()
            right_pipette.mix(5, 1000, working_reagent_reservoir["A2"].bottom(4))
            right_pipette.drop_tip(chute)
        else:
            if 4000 >= remainder >= 9000:
                right_pipette.pick_up_tip()
                right_pipette.mix(5, 1000, working_reagent_reservoir["A1"].bottom(4))
                right_pipette.drop_tip(chute)
                right_pipette.pick_up_tip()
                right_pipette.mix(5, 250, working_reagent_reservoir["A2"].bottom(4))
                right_pipette.drop_tip(chute)

            else:
                right_pipette.pick_up_tip()
                right_pipette.mix(5, 1000, working_reagent_reservoir["A1"].bottom(4))
                right_pipette.drop_tip(chute)
                right_pipette.pick_up_tip()
                right_pipette.mix(5, 150, working_reagent_reservoir["A2"].bottom(4))
                right_pipette.drop_tip(chute)

    else:
        right_pipette.pick_up_tip()
        right_pipette.mix(5, 500, working_reagent_reservoir["A1"].bottom(4))
        right_pipette.drop_tip(chute)

    remainder_columns = num_columns - 6

    # Adding Working Reagent to Plate       SLOW DOWN SPEED

    if total_working_reagent_volume <= max_volume:
        for i in range(num_columns):
            right_pipette.pick_up_tip()
            right_pipette.aspirate(working_reagent_volume+2, working_reagent_reservoir["A1"].bottom(1), 0.1)
            right_pipette.dispense(working_reagent_volume,sample_plate.rows()[0][i].top(1),0.1)
            right_pipette.drop_tip()

    else:
        for i in range(6):
            right_pipette.pick_up_tip()
            right_pipette.aspirate(working_reagent_volume+2, working_reagent_reservoir["A1"].bottom(1), 0.1)
            right_pipette.dispense(working_reagent_volume,sample_plate.rows()[0][i].top(1),0.1)
            right_pipette.drop_tip()
            
        j = 6
        while j < (6 + remainder_columns):
            right_pipette.pick_up_tip()
            right_pipette.aspirate(working_reagent_volume+2, working_reagent_reservoir["A2"].bottom(1), 0.1)
            right_pipette.dispense(working_reagent_volume,sample_plate.rows()[0][j].top(1),0.1)
            right_pipette.drop_tip()
            j = j + 1

        # Prep HeaterShaker

    heatshaker.open_labware_latch()
    
    #move labware with lid onto hs_mod
    protocol.deck.__delitem__('C2')
    new_sample_plate = protocol.load_labware('opentrons_96_wellplate_200ul_pcr_full_skirt', 'C2')
    protocol.move_labware(new_sample_plate, new_location=heatshaker, use_gripper=True)
    heatshaker.close_labware_latch()
    heatshaker.open_labware_latch()
    new_sample_plate.set_offset(x=0.00, y=0.00, z=30)
    protocol.move_labware(labware = lid, new_location=new_sample_plate, use_gripper=True)
    # protocol.pause("Place lid on well plate"
    heatshaker.close_labware_latch()
    heatshaker.set_and_wait_for_temperature(37)
    heatshaker.set_and_wait_for_shake_speed(400)

    # Shake For 30 Seconds
    protocol.delay(minutes=0.5)
    heatshaker.deactivate_shaker()

    protocol.comment("\n---------------25 Minute Incubation----------------\n\n")
    protocol.delay(minutes=25)

    # Deactivating Heatshaker
    heatshaker.deactivate_heater()

    heatshaker.open_labware_latch()
    protocol.move_labware(lid, "C1", use_gripper=True)
    protocol.move_labware(new_sample_plate, "C2", use_gripper=True)
    heatshaker.close_labware_latch()
