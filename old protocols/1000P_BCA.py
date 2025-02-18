# CHANGE TITLE IF NEEDED IN PROTOCOL NAME
metadata = {
    "protocolName": "BCA protocol",
    "author": "Sasha and Nico",
    "description": "First Used Tip box is in position A3; Place Empty 1.5 mL Tubes in slots B1-C1 for standards, BSA Standard (2mg/mL) should be added to a 1.5 mL tube, need 550µL; 100µL of each unknown sample should be aliquoted to the sample stock plate going down a column starting at A1 "
    "calculate volumes needed of reagent A and B before hand to fill falcon tube and microcentrifuge tube with the appropriate volumes, reagent A should not exceed 20 mL, Reagent A Loading should be 200µL * ((number of columns +1) * 8)+8), Reagent B should be Reagent A Volume / 50 ",
}
requirements = {"robotType": "Flex", "apiLevel": "2.20"}

start_pos = 24  # where the samples will be loaded on the 96-well plate going down a column (after 3 reps of 8 standards )

import math
from opentrons import protocol_api

def get_vol_50ml_falcon(height):
    '''
    Get's the volume of the liquid in the tube
    Height: height of liquid in tube in mm (start from tube bottom)
    Return: volume of liquid in tube in µl
    '''
    volume = (1000*(height-9))/1.8
    return volume
def get_height_50ml_falcon(volume):
    '''
    Get's the height of the liquid in the tube
    Volume: volume of liquid in tube in µl
    Return: hieght from bottom of tube in millimeters
    '''
    height = (1.8*(volume/1000))+9
    return height

def get_height_15ml_falcon(volume):
    '''
    Get's the height of the liquid in the tube
    Volume: volume of liquid in tube in ul
    Return: height in mm from the bottom of tube that pipette should go to
    '''
    volume = volume /1000
    if volume <= 1:     # cone part
        # print(-3.33*(volume**2)+15.45*volume+9.50)
        return -3.33*(volume**2)+15.45*volume+9.50 - 1   #−3.33x2+15.45x+9.50
    else:
        return 6.41667*volume +15.1667 -5
def get_vol_15ml_falcon(height):
    '''
    Get's the volume of the liquid in the tube
    Height: height in mm from the bottom of tube that pipette should go to
    Return: volume of liquid in tube in ul
    '''
    if height <= 20.62:     # cone part
        volume = (((15.45+math.sqrt(351.9225-(13.32*height))))/6.66)*1000
        return volume
    else:
        volume = ((height-10.1667)/6.41667)*1000
        return volume



def add_parameters(parameters):

    parameters.add_int(
        variable_name="number_samples",
        display_name="number_samples",
        description="Number of input samples.",
        default=21,
        minimum=1,
        maximum=24,
        unit="samples",
    )
    parameters.add_bool(
        variable_name="add_lid",
        display_name="Add a lid",
        description="Add a lid during incubation",
        default=True
    )
    parameters.add_bool(
        variable_name="dry_run",
        display_name="Dry Run",
        description="Return tips",
        default=False
    )

def run(protocol: protocol_api.ProtocolContext):
    number_samples = protocol.params.number_samples
    is_dry_run = protocol.params.dry_run
     
    # LOADING TIPS
    tips200 = [
        protocol.load_labware("opentrons_flex_96_filtertiprack_1000uL", slot)
        for slot in ["A3", "B3", "C3"]
    ]
    chute = protocol.load_waste_chute()
    def remove_tip(pipette):
        if is_dry_run:
            pipette.return_tip()
        else:
            pipette.drop_tip(chute) 
    def find_aspirate_height(pip, source_well):
        lld_height = pip.measure_liquid_height(source_well) - source_well.bottom().point.z
        aspirate_height = max(lld_height - 5, 1)
        return aspirate_height

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
    if protocol.params.add_lid:
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
    bsa_plate["D6"].load_liquid(sample, 1)

    dye_location = reagent_stock["A3"]
    dilutent_location = reagent_stock["A1"]
    sample_location = bsa_plate["D6"]
    bsa_stock_location = bsa_plate["A1"]
    # LOADING SAMPLE INTO SAMPLE_STOCK WELL PLATE       FINISH LATER
    protocol.comment("------------LOADING SAMPLE INTO SAMPLE_STOCK WELL PLATE-------------")
    #Loading 90ul dilutent
    pipette_max = 1000
    transfer_vol = 90
    left_pipette.pick_up_tip()
    vol_in_15_facon = get_vol_15ml_falcon(find_aspirate_height(left_pipette, dilutent_location))
    num_transfers = math.ceil((number_samples*transfer_vol)/pipette_max)
    well_counter = 0
    for i in range (0, num_transfers):
        if i != num_transfers-1:    # not on last iteration
            aspirate_vol = pipette_max - pipette_max%transfer_vol
        else:
            aspirate_vol = (number_samples*transfer_vol)-(pipette_max - pipette_max%transfer_vol)*(num_transfers-1)
        if left_pipette.has_tip == False:
            left_pipette.pick_up_tip()
        left_pipette.aspirate(aspirate_vol+5, dilutent_location.bottom(get_height_15ml_falcon(vol_in_15_facon)), 0.25)
        for x in range (0, math.floor(aspirate_vol/transfer_vol)):
            left_pipette.dispense(transfer_vol, sample_stock.wells()[well_counter], 0.25)
            well_counter += 1
        remove_tip(left_pipette)
        vol_in_15_facon-=aspirate_vol+5
    #loading 10ul sample
    left_pipette.pick_up_tip()
    for i in range (0, number_samples):
        left_pipette.aspirate(10, sample_location)
        left_pipette.dispense(10, sample_stock.wells()[i].bottom(1), 0.5)
        left_pipette.mix(4, 70, sample_stock.wells()[i].bottom(1), 0.3)
        left_pipette.blow_out(sample_stock.wells()[i].top(-1))
    remove_tip(left_pipette)
    
    
    # LOADING SAMPLES AND TRANSFERING TO SAMPLE PLATE
    drop_off = start_pos
    pick_up = 0

    while pick_up < number_samples:
        well = sample_stock.wells()[pick_up]
        left_pipette.pick_up_tip()
        left_pipette.aspirate(85, well.bottom(1), 0.5)      # Changed to 85

        for i in range(0, 3):
            left_pipette.dispense(
                25, sample_plate.wells()[drop_off + i].bottom(0.1), rate=0.25
            )

        remove_tip(left_pipette)

        drop_off += 3
        pick_up += 1

    # Standard Preparation  FINISH LATER
    standard_vol_per_tube = 500
    dilutent_percentages = [0.25, 0.5,0.625,0.75,0.875,0.9375,0.9875]
    dilutent_pipette_vols = []
    total_dilutent= 0
    for i in range (0, 7):
        if total_dilutent + standard_vol_per_tube*dilutent_percentages[i] < (1000-10):
            total_dilutent += standard_vol_per_tube*dilutent_percentages[i]
        else:
            dilutent_pipette_vols.append(total_dilutent)
            total_dilutent=0
    dilutent_pipette_vols.append(total_dilutent)
    tube_spots = ["B1", "B2", "B3", "B4", "B5", "B6", "C1"]
    well_num = 0
    left_pipette.pick_up_tip()
    for i in range (0,len(dilutent_pipette_vols)):
        left_pipette.aspirate(dilutent_pipette_vols[i]+10, dilutent_location.bottom(), 0.5)     #FIX LATER
        amt_in_tip = dilutent_pipette_vols[i]+10
        while amt_in_tip>10:
            left_pipette.dispense(dilutent_percentages[well_num]*standard_vol_per_tube, bsa_plate[tube_spots[well_num]],0.5)
            well_num+=1
            amt_in_tip-=dilutent_percentages[well_num]*standard_vol_per_tube
    remove_tip(left_pipette)
    for i in range (0, len(tube_spots)):
        left_pipette.pick_up_tip()
        left_pipette.aspirate(standard_vol_per_tube*(1-dilutent_percentages[i]), bsa_stock_location,0.5)
        left_pipette.dispense(standard_vol_per_tube*(1-dilutent_percentages[i]), bsa_plate[tube_spots[i]],0.5)
        left_pipette.mix(3, standard_vol_per_tube-10, bsa_plate[tube_spots[i]], 0.3)
        left_pipette.blow_out(bsa_plate[tube_spots[i]])
        remove_tip(left_pipette)
            
    def standard_loading(old, new):
        '''
        old: well from sample stock
        new: row letter from sample plate
        '''
        left_pipette.pick_up_tip()
        left_pipette.aspirate(80, bsa_plate[old].bottom(1.5), 0.25)
        
        for i in range(1, 4):  # A1,A2,A3
            left_pipette.dispense(25, sample_plate[new + str(i)].bottom(0.1), 0.25)
        remove_tip(left_pipette)

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
        left_pipette.dispense(25, sample_plate["H" + str(i)].bottom(0.1), 0.25)
    remove_tip(left_pipette)

    # Working Reagent Solution Prep
    num_columns = math.ceil(((math.ceil(number_samples / 8) * 8) * 3) / 8)+3
    working_reagent_volume = 200    #What does this number mean? Amt of dye?
    # Loading dye into 12-channel
    channel_max_vol = 13000
    working_reagent_amt = num_columns*8*working_reagent_volume     #ul
    total_vol = []
    for i in range (0, math.ceil(working_reagent_amt/channel_max_vol)):
        if i !=math.ceil(working_reagent_amt/channel_max_vol)-1:
            volumes = channel_max_vol
            total_vol.append(volumes)
        else:
            volumes = working_reagent_amt-((channel_max_vol-1800)*i)+1800
            total_vol.append(volumes)
    left_pipette.pick_up_tip()
    vol_in_dye_falcon = get_vol_50ml_falcon(find_aspirate_height(left_pipette, dye_location))
    for i in range (0, len(total_vol)):
        vol = total_vol[i]
        for x in range (0, math.ceil(vol/1000)):
            if x != math.ceil(vol/1000)-1:  #not last one yet
                left_pipette.aspirate(1000, dye_location.bottom(get_height_50ml_falcon(vol_in_dye_falcon)))
                left_pipette.dispense(1000, working_reagent_reservoir["A" +str(i+1)].top(-5))
                vol_in_dye_falcon-=1000
            else:
                left_pipette.aspirate(vol-(1000*x), dye_location.bottom(get_height_50ml_falcon(vol_in_dye_falcon)))
                left_pipette.dispense(vol-(1000*x),working_reagent_reservoir["A" +str(i+1)].top(-5))
                vol_in_dye_falcon-=1000*x
            left_pipette.blow_out(working_reagent_reservoir["A" +str(i+1)].top(-5))
    remove_tip(left_pipette)
    
    # Adding Working Reagent to Plate
    right_pipette.pick_up_tip()
    channel_num = 1
    for i in range (0, num_columns):
        if (total_vol[channel_num-1]-(working_reagent_volume*8)) <1000:
            channel_num+=1
        right_pipette.aspirate(working_reagent_volume, working_reagent_reservoir["A" + str(channel_num)])
        right_pipette.dispense(working_reagent_volume, sample_plate["A"+str(i+1)].top(-1), rate=0.1)
        right_pipette.blow_out(sample_plate["A"+str(i+1)].top(-1))
        total_vol[channel_num-1] -= working_reagent_volume*8
    remove_tip(right_pipette)
    
    # Prep HeaterShaker
    heatshaker.open_labware_latch()
    
    #move labware with lid onto hs_mod
    if protocol.params.add_lid:
        protocol.deck.__delitem__('C2')
        new_sample_plate = protocol.load_labware('opentrons_96_wellplate_200ul_pcr_full_skirt', 'C2')
        protocol.move_labware(new_sample_plate, new_location=heatshaker, use_gripper=True)
        heatshaker.close_labware_latch()
        heatshaker.open_labware_latch()
        new_sample_plate.set_offset(x=0.00, y=0.00, z=30)
        protocol.move_labware(labware = lid, new_location=new_sample_plate, use_gripper=True)
    else:
        protocol.move_labware(labware = sample_plate, new_location=heatshaker, use_gripper=True)
    # protocol.pause("Place lid on well plate")
    heatshaker.close_labware_latch()
    heatshaker.set_and_wait_for_temperature(37)
    heatshaker.set_and_wait_for_shake_speed(400)

    # Shake For 30 Seconds
    protocol.delay(minutes=0.5)
    heatshaker.deactivate_shaker()

    protocol.comment("\n---------------25 Minute Incubation----------------\n\n")
    protocol.delay(minutes=25)      #SEND EMAIL AT 10 MINUTES

    # Deactivating Heatshaker
    heatshaker.deactivate_heater()
    heatshaker.open_labware_latch()
    if protocol.params.add_lid:
        protocol.move_labware(lid, "C1", use_gripper=True)
        protocol.move_labware(new_sample_plate, "C2", use_gripper=True)
        heatshaker.close_labware_latch()
    else:
        protocol.move_labware(sample_plate, "C2", use_gripper=True)
        heatshaker.close_labware_latch()
    protocol.comment(str(channel_num))
    protocol.comment(str(total_vol))
    protocol.comment(str(num_columns))