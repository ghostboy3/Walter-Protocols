from opentrons import protocol_api
import math
import urllib.request
import urllib.parse
import json
from opentrons import types
# from datetime import datetime, timedelta
import time
from datetime import datetime
# z = input(" 600l  ")
# if z =="doodl":
#     y = input("do u love skbidi")
#     if y == "yessir":
#         print("ur the alpha, so sigma")
#         x = input("complete the lyrics: sigma sigma on the wall who")
#         if x == "is the skibidiest of them all":
#             print("bro u r litterally the GOAT like fr fr")
#         else:
#             print("are you google? because you have everything i've been searching for")
#     else:
#         print("people call me doodl, but you can call me anytime")
metadata = {
    "protocolName": "SP3 HILIC protocol",
    "author": "Nico To",
    "description": "HILIC sp3 protocol",
}

requirements = {"robotType": "Flex", "apiLevel": "2.20"}

def add_parameters(parameters: protocol_api.Parameters):

    parameters.add_int(
        variable_name="numSamples",
        display_name="Number of Samples",
        description="Number of samples",
        default=10,
        minimum=1,
        maximum=96,
        unit="samples"
    )

    # Default true
    parameters.add_bool(
        variable_name="manual_load_beads",
        display_name="Load beads with walt",
        description="Use walt to load beads",
        default=True
    )
    # Default true
    parameters.add_bool(
        variable_name="reduction_alkylation",
        display_name="Reduction and Alkylation",
        description="Use Walter to reduce and alkylate",
        default=True
    )
    parameters.add_int(
        variable_name="dtt_conc",
        display_name="Concentration DTT Stock",
        description="_______ mM DTT (only required of reduction and alkylation is done with Walt)",
        default=360,
        minimum=100,
        maximum=1000,
        unit="mM"
    )
    parameters.add_int(
        variable_name="iaa_conc",
        display_name="Concentration IAA Stock",
        description="_______ mM IAA (only required of reduction and alkylation is done with Walt)",
        default=540,
        minimum=100,
        maximum=1000,
        unit="mM"
    )
    parameters.add_int(
        variable_name="protein_stock_conc",
        display_name="Concentration of Protien Stock",
        description="_______ ug/ul protien.",
        default=50,
        minimum= 0,
        maximum=1000,
        unit="ug/ul"
    )
    
    # CONCENTRATION OF PROTEIN SAMPLE
    
    # OPTION TO DILUTE PROTEIN SAMPLE BASED ON CONCENTRATION
    
    parameters.add_bool(
        variable_name="dry_run",
        display_name="Dry Run",
        description="Skip incubation delays and return tips. Don't modify this value unless you're testing stuff.",
        default=False
    )
def send_email(msg):
    url = "http://NicoTo.pythonanywhere.com/send-email"
    data = {
        # "subject": "Test Subject",
        "body": msg,
        "to_email": "nico.luu.to@gmail.com"
    }
    data_encoded = json.dumps(data).encode('utf-8')
    
    req = urllib.request.Request(url, data=data_encoded, headers={'Content-Type': 'application/json'})
    
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                print(" command sent successfully")
            else:
                print(f"Failed to send command")
    except urllib.error.URLError as e:
        print(f"Failed to send  command. Error: {e.reason}")
def get_height_smalltube(volume):
    '''
    Get's the height of the liquid in the tube
    Volume: volume of liquid in tube in µl
    Return: hieght from bottom of tube in millimeters
    '''
    height = 1
    # volume = volume/1000
    if volume <= 500 and volume >= 250:     # cone part aaa
        volume = volume/1000
        height = -26.8*(volume**2)+45.1*volume+3.98-5 #−26.80x2 +45.10x+3.98
    elif volume <= 250 and volume >= 35:     # cone part aaa
        volume = volume/1000
        height = -26.8*(volume**2)+45.1*volume+3.9-3.5 #−26.80x2 +45.10x+3.98
    elif volume <= 35 and volume >= 15:     # cone part aaa
        volume = volume/1000
        height = -26.8*(volume**2)+45.1*volume+3.9-4.5 #−26.80x2 +45.10x+3.98
    elif volume <= 15 and volume >= 0:     # cone part aaa
        volume = volume/1000
        height = -26.8*(volume**2)+45.1*volume+3.9-5.5 #−26.80x2 +45.10x+3.98

    elif volume > 500 and volume < 750:
        height= 0.015*volume+11.5-5
    elif volume > 750:
        height= 0.015*volume+11.5-4

    if height < 0.1 or volume <=7: 
        return 0.1
    else:
        return height

def get_height_15ml_falcon(volume):
    '''
    Get's the height of the liquid in the tube
    Volume: volume of liquid in tube in ul
    Return: height in mm from the bottom of tube that pipette should go to
    '''
    volume = volume/1000
    if volume <= 1:     # cone part aaa
        # print(-3.33*(volume**2)+15.45*volume+9.50)
        height = -3.33*(volume**2)+15.45*volume+9.50 - 1   #−3.33x2+15.45x+9.50
    else:
        height = 6.41667*volume +15.1667 -5
    if height < 0.1:
        height =  0.1
    return height
  
def get_height_50ml_falcon(volume):
    '''
    Get's the height of the liquid in the tube
    Volume: volume of liquid in tube in µl
    Return: hieght from bottom of tube in millimeters
    '''
    height = (1.8*(volume/1000))+12-3
    if height < 0.1:
        height =  0.1
    return height
def get_vol_15ml_falcon(height):
    """
    Get's the volume of the liquid in the tube
    Height: height in mm from the bottom of tube that pipette should go to
    Return: volume of liquid in tube in ul
    """
    if height <= 20.62:  # cone part
        volume = (((15.45 + math.sqrt(351.9225 - (13.32 * height)))) / 6.66) * 1000
        return volume
    else:
        volume = ((height - 10.1667) / 6.41667) * 1000
        return volume
def get_vol_50ml_falcon(height):
    """
    Get's the volume of the liquid in the tube
    Height: height of liquid in tube in mm (start from tube bottom)
    Return: volume of liquid in tube in µl
    """
    volume = (1000 * (height - 9)) / 1.8
    return volume



def run(protocol: protocol_api.ProtocolContext):
    #defining variables
    wash_volume = 100#protocol.params.wash_volume   #µl
    shake_speed = 1400#protocol.params.shake_speed   #rpm
    num_washes = 2
    num_samples = protocol.params.numSamples
    bead_settle_time = 10 #seconds
    dtt_conc = protocol.params.dtt_conc
    iaa_conc = protocol.params.iaa_conc
    
    bead_amt = max(protocol.params.protein_stock_conc/4, 5)      #µl
    protein_sample_amt = 60         # Includes DTT + IAA + protien + buffer
    protein_added_to_beads =protein_sample_amt*2      #ul
    equilibartion_buffer_amt = (300*8*(math.ceil(num_samples/8)) + 1000)/1000       #ml
    binding_buffer_amt = (40*8*(math.ceil(num_samples/8)) + 500)/1000       #ml
    wash_buffer_amt = (300*8*(math.ceil(num_samples/8)) + 1000)/1000       #ml
    digestion_buffer_per_sample_amt = 100#protocol.params.digestion_buffer_per_sample_amt       #100-150µl
    
    #Random variables for testing
    amt_extra_in_2ml_reservoir = 50
    
    #loading tips
    # if protocol.params.create_buffers == True:      # A3 has p1000 tips
    #     tips200 = [protocol.load_labware("opentrons_flex_96_filtertiprack_1000uL", "A3"), protocol.load_labware("opentrons_flex_96_filtertiprack_200uL", "B3"), protocol.load_labware("opentrons_flex_96_filtertiprack_200uL", "C3")]
    tips200 = [protocol.load_labware("opentrons_flex_96_filtertiprack_200uL", "A3"), protocol.load_labware("opentrons_flex_96_filtertiprack_200uL", "B3"), protocol.load_labware("opentrons_flex_96_filtertiprack_200uL", "C3")]

    chute = protocol.load_waste_chute()
    left_pipette = protocol.load_instrument("flex_1channel_1000", "left", tip_racks=tips200)
    right_pipette = protocol.load_instrument("flex_8channel_1000", "right", tip_racks=tips200)
    magnetic_block = protocol.load_module(module_name="magneticBlockV1", location="C1")
    hs_mod = protocol.load_module(module_name="heaterShakerModuleV1", location="D1")    #heat shaker module
    # red_alk_plate = protocol.load_labware("opentrons_96_wellplate_200ul_pcr_full_skirt", "A2", "reduction and alkylation plate")
    # tube_rack = protocol.load_labware("opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap", "A2", "bead + final solution rack")
    sample_plate = protocol.load_labware("opentrons_96_wellplate_200ul_pcr_full_skirt", "A1", "sample stock plate")
    # reagent_plate = hs_mod.load_labware("opentrons_96_wellplate_200ul_pcr_full_skirt","reagent plate")
    reagent_plate = protocol.load_labware("opentrons_96_wellplate_200ul_pcr_full_skirt","A2","reagent plate")
    digestion_buffer_reservoir = protocol.load_labware("nest_96_wellplate_2ml_deep", location= "B2")        ## change deck location
    # final_sample_plate = protocol.load_labware("opentrons_96_wellplate_200ul_pcr_full_skirt", "B1", "reagent plate")
    # buffer_rack = protocol.load_labware("opentrons_10_tuberack_falcon_4x50ml_6x15ml_conical", "B1", "reagent stock rack")   # equilibration, binding, and wash buffer
    working_reagent_reservoir = protocol.load_labware("nest_12_reservoir_15ml", "D2")
    final_tube_rack = protocol.load_labware("opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap", "B1", "final solution rack")
    falcon_tube_rack = protocol.load_labware("opentrons_15_tuberack_falcon_15ml_conical", "C2", "falcon rack")

    # dtt_plate = protocol.load_labware("opentrons_96_wellplate_200ul_pcr_full_skirt", "C3", "DTT plate")
    
    # trash_reservoir = protocol.load_labware("nest_1_reservoir_195ml", "C2", "trash reservoir")
    
    #defining liquids
    bead_sol = protocol.define_liquid("HILIC Bead Solution", "An alloquat of the HILIC bead solution", "#000000")
    dtt_stock = protocol.define_liquid("DTT Stock", "Dtt Stock", "#fcba03")
    iaa_stock = protocol.define_liquid("IAA Stock", "IAA Stock", "#df02f7")
    empty_tube = protocol.define_liquid("Empty Tube", "Empty 1.5ml snapcap", "#8a8a8a")
    equilibration_buffer = protocol.define_liquid("Equilibration Buffer", "100mM ammonium acetate, pH 4.5, 15%% acetonitrile", "#32a852")
    binding_buffer = protocol.define_liquid("Binding Buffer", "200mM ammonium acetate, pH 4.5, 30%% acetonitrile", "#8d32a8")
    wash_buffer = protocol.define_liquid("Wash Buffer", "95%% acetonitrile (5% water)", "#05a1f5")
    digestion_buffer = protocol.define_liquid("Digestion Buffer", "", "#fafa02")          # CHANGE THIS AFTER ASKING LAURA
    protien_buffer = protocol.define_liquid("Protien Buffer", "", "#ff59f7")
    formic_acid = protocol.define_liquid("Formic Acid", "", "#00b7ff")
    # water = protocol.define_liquid("water", "water", "#00b7ff")
    # acetonitrile = protocol.define_liquid("acn", "acn", "#03fc31")
    # ammoniumAcetate = protocol.define_liquid("ammonium acetate", "ammonium acetate", "#fa05ee")
    # Loading Liquids
    falcon_tube_rack["A2"].load_liquid(bead_sol, bead_amt)
    falcon_tube_rack["B1"].load_liquid(dtt_stock, 200)
    falcon_tube_rack["C1"].load_liquid(iaa_stock, 200)
    falcon_tube_rack["B2"].load_liquid(empty_tube, 200)
    falcon_tube_rack["C2"].load_liquid(empty_tube, 200)
    falcon_tube_rack["A3"].load_liquid(protien_buffer, 200)
    falcon_tube_rack["B3"].load_liquid(formic_acid, 200)
    bead_storage = falcon_tube_rack["A2"]
    dtt_stock_storage = falcon_tube_rack["B1"]
    dtt_working_storage = falcon_tube_rack["B2"]
    iaa_stock_storage = falcon_tube_rack["C1"]
    iaa_working_storage = falcon_tube_rack["C2"]
    protien_buffer_storage = falcon_tube_rack["A3"]
    formic_acid_storage = falcon_tube_rack["B3"]
    # tube_rack["B1"].load_liquid(digestion_buffer, digestion_buffer_stock_amt)
    # digestion_buffer_storage = tube_rack["B1"]
    # digestion_buffer_storage = reservoir.columns_by_name()['1']
    # digestion_buffer_storage.load_liquid(digestion_buffer, digestion_buffer_stock_amt)
    falcon_tube_rack["A1"].load_liquid(digestion_buffer, digestion_buffer_per_sample_amt*num_samples)
    dig_buffer_location = falcon_tube_rack["A1"]
    
    # falcon_tube_rack["A3"].load_liquid(water, 100)
    # water_location = falcon_tube_rack["A3"]
    # falcon_tube_rack["A4"].load_liquid(acetonitrile, 100)
    # acn_location = falcon_tube_rack["A4"]
    # falcon_tube_rack["B3"].load_liquid(ammoniumAcetate, 100)
    # ammoniumAcetate_location = falcon_tube_rack["B3"]

    working_reagent_reservoir["A1"].load_liquid(equilibration_buffer, equilibartion_buffer_amt)
    working_reagent_reservoir["A2"].load_liquid(equilibration_buffer, equilibartion_buffer_amt)
    working_reagent_reservoir["A3"].load_liquid(equilibration_buffer, equilibartion_buffer_amt)
    equilibration_buffer_storage = [working_reagent_reservoir["A1"], working_reagent_reservoir["A2"], working_reagent_reservoir["A3"]]
    
    working_reagent_reservoir["A4"].load_liquid(binding_buffer, binding_buffer_amt)
    working_reagent_reservoir["A5"].load_liquid(binding_buffer, binding_buffer_amt)
    working_reagent_reservoir["A6"].load_liquid(binding_buffer, binding_buffer_amt)
    binding_buffer_storage = [working_reagent_reservoir["A4"], working_reagent_reservoir["A5"], working_reagent_reservoir["A6"]]

    working_reagent_reservoir["A7"].load_liquid(wash_buffer, wash_buffer_amt)
    working_reagent_reservoir["A8"].load_liquid(wash_buffer, wash_buffer_amt)
    working_reagent_reservoir["A9"].load_liquid(wash_buffer, wash_buffer_amt)
    wash_buffer_storage = [working_reagent_reservoir["A7"], working_reagent_reservoir["A8"], working_reagent_reservoir["A9"]]
    # trash1=trash_reservoir.wells()[0].bottom(7)
    staging_slots = ['A4', 'B4', 'C4', 'D4']
    staging_racks = [protocol.load_labware('opentrons_flex_96_filtertiprack_200uL',
                                      slot) for slot in staging_slots]

    pipette_max = 200-5
    #REPLENISHING TIPS
    count = 0
    #Functions
    def remove_tip(pipette, is_dry_run = protocol.params.dry_run):
        if is_dry_run:
            pipette.return_tip()
        else:
            pipette.drop_tip(chute)         
    def aspirate_spuernatent_to_trash(pipette, amt, speed, discard_tip = True, height = 0.3):
        '''amt: amount ot aspirirate out'''
        protocol.comment("\nAspriating supernatant to trash")
        for i in range (0, math.ceil(num_samples/8)):
            if pipette.has_tip == False:
                pick_up(pipette)
                # print("hi")
                # pipette.pick_up_tip()
            pipette.aspirate(amt, reagent_plate['A' + str(i+1)].bottom(height), rate=speed)
            # pipette.air_gap(volume=10)
            pipette.dispense(amt, chute,5)
            if discard_tip:
                remove_tip(pipette, protocol.params.dry_run)
        if pipette.has_tip == True:
            remove_tip(pipette, protocol.params.dry_run)
    def pick_up(pip):
        nonlocal tips200
        nonlocal staging_racks
        nonlocal count

        try:
            # print(tips200)
            pip.tip_racks = tips200
            # print(pip.tip_racks)
            pip.pick_up_tip()

        except protocol_api.labware.OutOfTipsError:
            check_tips()
            pick_up(pip)    
    def check_tips():
        nonlocal tips200
        nonlocal staging_racks
        nonlocal count
        # tip_box = protocol.load_labware('opentrons_flex_96_filtertiprack_1000uL', 'A3')
        for i in range (0,3):
            tip_box_slots = ['A3', 'B3', 'C3']
            # aaaaaaaaaaaaaaaaa
            try:
                bottom_right_well = tips200[i].wells_by_name()['H12']
            except:
                bottom_right_well = tips200[0].wells_by_name()['A1']
            if bottom_right_well.has_tip or protocol.deck['D4'] == None:
                protocol.comment("A tip is present in the bottom-right corner (H12). or all staging slots are empty")
                if protocol.deck['D4'] == None:
                    protocol.comment("No tip box detected in slot D4.")
                    staging_slots = ['A4', 'B4', 'C4', 'D4']
                    staging_racks = [protocol.load_labware('opentrons_flex_96_filtertiprack_200uL',
                                      slot) for slot in staging_slots]
                pass
            else:
                protocol.comment("\n\n\n Starting moving phase")
                protocol.move_labware(
                        labware=tips200[i],
                        new_location=chute,
                        use_gripper=True
                    )
                rack_num = 0
                for slot in ['A4', 'B4', 'C4', 'D4']:
                    labware = protocol.deck[slot]
                    if labware and labware.is_tiprack:
                        tips200[i] = staging_racks[rack_num]
                        # print(tips200[i])
                        print(tip_box_slots[i])
                        protocol.move_labware(
                            labware=staging_racks[rack_num],
                            new_location=tip_box_slots[i],
                            use_gripper=True
                        )
                        break
                        # protocol.comment(f"A tip box is present in slot {slot}.")
                    else:
                        protocol.comment(f"No tip box detected in slot {slot}.")
                        rack_num+=1
                        pass
    def find_aspirate_height(pip, source_well):
        '''
        returns: aspirate height from bottom in mm
        '''
        lld_height = (
            pip.measure_liquid_height(source_well) - source_well.bottom().point.z
        )
        aspirate_height = max(lld_height - 5, 1)
        return aspirate_height

    def mix_sides(pipette, num_mixes, vol, plate, rate):
        pipette.mix(num_mixes, vol, plate.bottom().move(types.Point(x=0, y=1, z=3.5)),rate= rate)
        pipette.mix(num_mixes, vol, plate.bottom().move(types.Point(x=0, y=-1, z=3.5)),rate= rate)
        pipette.mix(num_mixes, vol, plate.bottom().move(types.Point(x=1, y=0, z=3.5)),rate= rate)
        pipette.mix(num_mixes, vol, plate.bottom().move(types.Point(x=-1, y=0, z=3.5)),rate= rate)
        pipette.mix(1, vol, plate.bottom(0.1),rate= 0.1)
    
    def delay(seconds, msg = ""):
        if protocol.params.dry_run:
            return
        # start_time = datetime.now()
        # protocol.comment(f"Delaying for {seconds} seconds")
        check_tips()
        protocol.delay(seconds=seconds, msg = msg)
        # while True:
        #     if (datetime.now() - start_time).seconds > seconds:
        #         break
    
    def transfer_large_amt(vol, start_loc, end_loc, pipette, rate, aspirate_height = 0, dispense_height = 0):
        '''
        vol: volume to transfer
        start_loc: location to aspirate from
        end_loc: location to dispense to
        pipette: pipette to use
        rate: rate to aspirate and dispense
        '''
        for i in range (0, math.ceil(vol/pipette_max)):
            if i != math.ceil(vol/pipette_max)-1:
                print(aspirate_height)
                pipette.aspirate(pipette_max, start_loc.bottom(aspirate_height), rate=rate)
                pipette.dispense(pipette_max, end_loc.bottom(dispense_height), rate=rate)
            else:
                pipette.aspirate(vol-(pipette_max*i), start_loc.bottom(aspirate_height), rate=rate)
                pipette.dispense(vol-(pipette_max*i), end_loc.bottom(dispense_height), rate=rate)
    
    if protocol.params.reduction_alkylation:
        dtt_final_conc = 20     #20 mM
        iaa_final_conc = 30     #30 mM
        pipette_min = 5     # 5ul is the minimum volume for the pipette
        protocol.comment("-------------Reduction and Alkylation ---------------")
        print("reduction and alkylation")
        # Creating DTT Dilution
        dtt_working_stock_conc = (dtt_final_conc*protein_sample_amt)/pipette_min   # DTT working stock concentration so that 5ul is 20 mM
        dtt_working_vol = pipette_min * num_samples + 8*amt_extra_in_2ml_reservoir +50
        dtt_stock_vol = (dtt_working_stock_conc*dtt_working_vol)/dtt_conc       # amt of stock that needs to be transfered to create working dtt solution
        # LOADING THE DTT
        pick_up(left_pipette)
        volume_of_dtt_stock_storage_tube = get_vol_15ml_falcon(find_aspirate_height(left_pipette, dtt_stock_storage))
        volume_of_dtt_stock_storage_tube -= dtt_stock_vol
        # print(volume_of_dtt_stock_storage_tube)
        transfer_large_amt(dtt_stock_vol, dtt_stock_storage, dtt_working_storage, left_pipette, 0.5, aspirate_height=0.1, dispense_height=50)
        print(dtt_stock_vol)
        remove_tip(left_pipette, protocol.params.dry_run)
        pick_up(left_pipette)
        pick_up(left_pipette)
        volume_of_protein_buffer_storate = get_vol_15ml_falcon(find_aspirate_height(left_pipette, protien_buffer_storage))
        volume_of_protein_buffer_storate-= dtt_working_vol-dtt_stock_vol
        transfer_large_amt(dtt_working_vol-dtt_stock_vol, protien_buffer_storage, dtt_working_storage, left_pipette, 0.5, aspirate_height=get_height_15ml_falcon(volume_of_protein_buffer_storate),dispense_height=50)
        left_pipette.mix(10, pipette_max, dtt_working_storage.bottom(1))
        remove_tip(left_pipette, protocol.params.dry_run)
        pick_up(left_pipette)
        for i in range (0, 8):
            if i <num_samples%8:
                amt_in_well = 5* math.ceil(num_samples/8)+amt_extra_in_2ml_reservoir
            else:
                amt_in_well = 5* math.floor(num_samples/8)+amt_extra_in_2ml_reservoir
            # print(amt_in_well)
            transfer_large_amt(amt_in_well, dtt_working_storage, digestion_buffer_reservoir.wells()[i+8], left_pipette, 0.5,dispense_height=1)
        remove_tip(left_pipette, protocol.params.dry_run)
        # ADDING DTT TO PLATE
        for i in range (0, math.ceil(num_samples/8)):
            pick_up(right_pipette)
            right_pipette.aspirate(5, digestion_buffer_reservoir['A2'].bottom(0.1), 0.5)
            right_pipette.dispense(5, sample_plate['A' + str(i+1)].bottom(1), 0.5)
            right_pipette.mix(3,protein_sample_amt-10, sample_plate['A' + str(i+1)].bottom(1), 0.2)
            right_pipette.blow_out(sample_plate['A' + str(i+1)].top())
            remove_tip(right_pipette, protocol.params.dry_run)
        hs_mod.open_labware_latch()
        # 56 C for 30 minutes
        protocol.move_labware(sample_plate, hs_mod, use_gripper=True)
        hs_mod.close_labware_latch()
        # hs_mod.set_and_wait_for_shake_speed(1450)       #1000 rpm
        hs_mod.set_and_wait_for_temperature(56)
        start_time = datetime.now()
        
        # PREPARING IAA
        iaa_working_stock_conc = (iaa_final_conc*protein_sample_amt)/pipette_min   # IAA working stock concentration so that 5ul is 20 mM
        iaa_working_vol = pipette_min * num_samples + 8*amt_extra_in_2ml_reservoir +50
        iaa_stock_vol = (iaa_working_stock_conc*iaa_working_vol)/iaa_conc       # amt of stock that needs to be transfered to create working dtt solution
        pick_up(left_pipette)
        volume_of_iaa_stock_storage_tube = get_vol_15ml_falcon(find_aspirate_height(left_pipette, iaa_stock_storage))
        volume_of_iaa_stock_storage_tube -= iaa_stock_vol
        transfer_large_amt(iaa_stock_vol, iaa_stock_storage, iaa_working_storage, left_pipette, 0.5,aspirate_height=0.1, dispense_height=50)
        remove_tip(left_pipette, protocol.params.dry_run)
        pick_up(left_pipette)
        volume_of_protein_buffer_storate -= iaa_working_vol-iaa_stock_vol
        transfer_large_amt(iaa_working_vol-iaa_stock_vol, protien_buffer_storage, iaa_working_storage, left_pipette, 0.5,aspirate_height=get_height_15ml_falcon(volume_of_protein_buffer_storate), dispense_height=50)
        left_pipette.mix(10, pipette_max, iaa_working_storage.bottom(1))
        remove_tip(left_pipette, protocol.params.dry_run)
        
        pick_up(left_pipette)
        for i in range (0, 8):
            if i <num_samples%8:
                amt_in_well = 5* math.ceil(num_samples/8)+amt_extra_in_2ml_reservoir
            else:
                amt_in_well = 5* math.floor(num_samples/8)+amt_extra_in_2ml_reservoir
            # print(amt_in_well)
            transfer_large_amt(amt_in_well, iaa_working_storage, digestion_buffer_reservoir.wells()[i+16], left_pipette, 0.5, dispense_height=1)
        remove_tip(left_pipette, protocol.params.dry_run)
        
        # 30 min incubation
        time_elasped = (datetime.now() - start_time).seconds
        delay(seconds = 1800-time_elasped, msg = "30 minute DTT incubation at 56 C")
        # moving plate and adding IAA to plate
        hs_mod.deactivate_shaker()
        hs_mod.deactivate_heater()
        hs_mod.open_labware_latch()
        protocol.move_labware(sample_plate, "A1", use_gripper=True)

        for i in range (0, math.ceil(num_samples/8)):
            pick_up(right_pipette)
            right_pipette.aspirate(5, digestion_buffer_reservoir['A3'].bottom(0.1), 0.5)
            right_pipette.dispense(5, sample_plate['A' + str(i+1)].bottom(1), 0.5)
            right_pipette.mix(3,protein_sample_amt-10, sample_plate['A' + str(i+1)].bottom(1), 0.2)
            right_pipette.blow_out(sample_plate['A' + str(i+1)].top())
            remove_tip(right_pipette, protocol.params.dry_run)
        # 45 minute IAA incubation at RT
        hs_mod.open_labware_latch()
        protocol.pause('''IAA incubation for 45 minutes at room temperature''')
        # protocol.move_labware(sample_plate, hs_mod, use_gripper=True)
        # hs_mod.close_labware_latch()
        # hs_mod.set_and_wait_for_shake_speed(1450)
        # delay(seconds=45*60, msg="45 minute IAA incubation at room temperature")
        # # protocol.delay(minutes=45, msg="45 minute IAA incubation at room temperature")
        # hs_mod.deactivate_shaker()
        # hs_mod.open_labware_latch()
        # protocol.move_labware(sample_plate, "A1", use_gripper=True)
        # protocol.move_labware(reagent_plate, hs_mod, use_gripper=True)
        # hs_mod.close_labware_latch()
        
    hs_mod.open_labware_latch()
    hs_mod.close_labware_latch()
    protocol.comment("-------------Equilibration ---------------")
    if protocol.params.manual_load_beads:

        pipette_max = 195
        num_transfers = math.ceil((bead_amt*num_samples)/(pipette_max))
        well_counter = 0
        change_tip_after = 3
        protocol.comment("\nTransfering 25µl HILIC beads into well plate")
        # pick_up(left_pipette)
        total_bead_amt = num_samples*bead_amt
        num_transfers = math.ceil(total_bead_amt/(change_tip_after * bead_amt)) #math.ceil(total_bead_amt / (math.floor((pipette_max-10)/bead_amt)*bead_amt))
        for i in range (0, num_transfers):
            if i == num_transfers - 1:      # on last iteration
                aspirate_amt = num_transfers*bead_amt - bead_amt*(num_transfers-1)+3
                pick_up(left_pipette)
                left_pipette.mix(3, total_bead_amt-bead_amt*well_counter, bead_storage)
                left_pipette.aspirate(aspirate_amt, bead_storage.bottom(0.5))
                for x in range (0, math.floor(aspirate_amt/bead_amt)):
                    left_pipette.dispense(bead_amt, reagent_plate.wells()[well_counter])
                    well_counter += 1
                left_pipette.blow_out(bead_storage.top())
                remove_tip(left_pipette, protocol.params.dry_run)

            else:
                aspirate_amt = change_tip_after * bead_amt+5
                pick_up(left_pipette)
                left_pipette.mix(3, total_bead_amt-bead_amt*well_counter, bead_storage)
                left_pipette.aspirate(aspirate_amt, bead_storage.bottom(0.5))
                for x in range (0, change_tip_after):
                    left_pipette.dispense(bead_amt, reagent_plate.wells()[well_counter])
                    well_counter += 1
                left_pipette.blow_out(bead_storage.top())
                remove_tip(left_pipette, protocol.params.dry_run)

    protocol.comment("\nPlacing tube on magnetic separator and allowing 10s for microparticles to clear")
    hs_mod.open_labware_latch()
    protocol.move_labware(reagent_plate, magnetic_block, use_gripper=True)
    protocol.delay(seconds=bead_settle_time+5, msg="waiting 7 seconds for microparticles to clear")
    aspirate_spuernatent_to_trash(right_pipette, bead_amt - (bead_amt-5), 0.1, discard_tip=False)


    protocol.comment("\nWashing and equilibrating the microparticles in "+str(wash_volume) + "µl Equilibration Buffer (2 times)")
    for wash_num in range (0,num_washes):     # all washes before the last wash with EQ buffer
        protocol.comment("Wash number: "+  str(wash_num+1))
        hs_mod.open_labware_latch()
        protocol.move_labware(reagent_plate, new_location=hs_mod, use_gripper=True)
        hs_mod.close_labware_latch()

        pick_up(right_pipette)
        for i in range (0, math.ceil(num_samples/8)):
            # right_pipette.pick_up_tip()
            equilibartion_buffer_amt -= wash_volume/1000 * 8#0.18*8
            right_pipette.aspirate(wash_volume, equilibration_buffer_storage[math.ceil(equilibartion_buffer_amt/10.5)-1].bottom(1),0.4)
            right_pipette.dispense(wash_volume, reagent_plate['A' + str(i+1)].bottom(2),0.3)
            if wash_num == 0:      # first run
                mix_sides(right_pipette, 2, wash_volume-10, reagent_plate['A' + str(i+1)], 0.7)
            else:
                mix_sides(right_pipette, 1, wash_volume-10, reagent_plate['A' + str(i+1)], 0.7)

            right_pipette.blow_out(reagent_plate['A' + str(i+1)].top())
            right_pipette.blow_out(reagent_plate['A' + str(i+1)].top())
            right_pipette.touch_tip()
            right_pipette.blow_out(reagent_plate['A' + str(i+1)].top())
        remove_tip(right_pipette, protocol.params.dry_run)

        protocol.comment("Gentil agitation for 1 minute ("+str(shake_speed)+"rpm)")
        hs_mod.set_and_wait_for_shake_speed(shake_speed)       #1000 rpm
        delay(60)
        hs_mod.deactivate_shaker()
        hs_mod.open_labware_latch()
        
        if wash_num == 0:   # first wash
            hs_mod.open_labware_latch()
            protocol.move_labware(reagent_plate, magnetic_block, use_gripper=True)
            protocol.delay(seconds=bead_settle_time+5, msg="waiting for beads to settle (20 sec)")
            aspirate_spuernatent_to_trash(right_pipette, wash_volume-15, 0.25, discard_tip=False)       # leave the last 5ul in the well plate
        elif wash_num != num_washes-1:      # Not on the last wash yet
            hs_mod.open_labware_latch()
            protocol.move_labware(reagent_plate, magnetic_block, use_gripper=True)
            protocol.delay(seconds=bead_settle_time+5, msg="waiting for beads to settle (20 sec)")
            aspirate_spuernatent_to_trash(right_pipette, wash_volume, 0.25, discard_tip=False)       # leave the last 5ul in the well plate
        # protocol.move_labware(reagent_plate, new_location="B2", use_gripper=True)

    # protocol.move_labware(reagent_plate, new_location="B2", use_gripper=True)

    protocol.comment("\n\n---------------Protein Binding Procedure------------------\n\n\n\n")
    protocol.comment("\nAdding "+str(protein_sample_amt)+"µl binding buffer to "+str(protein_sample_amt)+"µl protein sample")
    for i in range (0, math.ceil(num_samples/8)):
        # right_pipette.pick_up_tip()
        pick_up(right_pipette)
        binding_buffer_amt -= (protein_sample_amt/1000)*8
        right_pipette.aspirate(protein_sample_amt, binding_buffer_storage[math.ceil(binding_buffer_amt/10.5)-1].bottom(1), 0.4)
        right_pipette.dispense(protein_sample_amt, sample_plate['A' + str(i+1)].bottom(1),0.5)
        right_pipette.mix(4, protein_sample_amt-15,sample_plate['A' + str(i+1)].bottom(1),rate=0.1)
        remove_tip(right_pipette, protocol.params.dry_run)
    
    hs_mod.open_labware_latch()
    protocol.move_labware(reagent_plate, magnetic_block, use_gripper=True)
    aspirate_spuernatent_to_trash(right_pipette, wash_volume+25, 0.5,discard_tip=False)

    hs_mod.open_labware_latch()
    protocol.move_labware(reagent_plate, hs_mod, use_gripper=True)
    hs_mod.close_labware_latch()
    
    protocol.comment("\nAdding binding buffer and protein sample to well plate")
    for i in range (0, math.ceil(num_samples/8)):
        # right_pipette.pick_up_tip()
        pick_up(right_pipette)
        right_pipette.aspirate(protein_added_to_beads+10, sample_plate['A' + str(i+1)], rate=0.1)
        right_pipette.dispense(protein_added_to_beads, reagent_plate['A' + str(i+1)].bottom(1), rate=0.1)
        mix_sides(right_pipette, 2, 50, reagent_plate['A' + str(i+1)], 2)
        # right_pipette.mix(3, 30, reagent_plate['A' + str(i+1)].bottom(0.5), rate=0.1)
        right_pipette.dispense(10, reagent_plate['A' + str(i+1)].top(1), rate=0.1)
        right_pipette.blow_out(reagent_plate['A' + str(i+1)].top())
        right_pipette.blow_out(reagent_plate['A' + str(i+1)].top())
        right_pipette.touch_tip()
        remove_tip(right_pipette, protocol.params.dry_run)

    protocol.comment("\nAllow proteins to bind to microparticles for 30 min. Mix gently and continuously")
    start_time = time.time()
    protocol.comment("\n\n\n\n\n"+str(start_time))
    hs_mod.open_labware_latch()
    hs_mod.close_labware_latch()
    # protocol.pause('''"Put the lid on!!!" -O____________O''')
    hs_mod.set_and_wait_for_shake_speed(1550)       #1100 rpm
    # protocol.pause('''"Tell me when to stop!! (30 min incubation time)''')
    protocol.comment("\n\n"*20)
    
    start_time = datetime.now()
    transfer_vol = (math.ceil(num_samples/8))*100 +50       # transfer into each well
    total_dig_buffer = transfer_vol*8
    pipette_max = 200
    num_transfers = math.ceil((total_dig_buffer)/(pipette_max))
    well_counter = 0
    left_pipette.pick_up_tip()
    for well_counter in range (0,8):
        if i == 0 or i == 1:
            transfer_large_amt(250, dig_buffer_location, digestion_buffer_reservoir.wells()[well_counter], left_pipette, 0.25)
            well_counter += 1
        else:
            transfer_large_amt(150, dig_buffer_location, digestion_buffer_reservoir.wells()[well_counter], left_pipette, 0.25)
            well_counter+=1
        # left_pipette.aspirate(aspirate_vol, dig_buffer_location, 0.25)
    #     for i in range (0, math.ceil(transfer_vol/pipette_max)):
    #         if i != math.ceil(transfer_vol/pipette_max):    # not on last iteration
    #             aspirate_vol = pipette_max
    #         else:
    #             aspirate_vol = transfer_vol - (pipette_max*i)
    #         left_pipette.aspirate(aspirate_vol, dig_buffer_location, 0.25)    
    #         print(aspirate_vol)
    #         left_pipette.dispense(aspirate_vol, digestion_buffer_reservoir.wells()[well_counter].bottom(), 0.1)
    remove_tip(left_pipette, protocol.params.dry_run)
    # left_pipette.pick_up_tip()
    # left_pipette.pick_up_tip()
    time_elasped = (datetime.now() - start_time).seconds
    # 30 minute incubation
    delay(1800-time_elasped)
    
    hs_mod.deactivate_shaker()
    hs_mod.open_labware_latch()
    protocol.move_labware(reagent_plate, magnetic_block, use_gripper=True)
    protocol.delay(seconds=bead_settle_time, msg="waiting for beads to settle (20 sec)")
    aspirate_spuernatent_to_trash(right_pipette, wash_volume - 15, 0.2)

    protocol.comment("\nResuspend beads in " + str(wash_volume) + "µl wash buffer and mix thoroughly for 1 minute. times: " + str(num_washes))     # TO-DO: PUT THIS INTO A FRICKEN FUNCTION!
    # protocol.move_labware(reagent_plate, new_location="B2", use_gripper=True)
    wash_buffer_resuspend_amt = wash_volume
    for wash_num in range (0,num_washes):
        protocol.comment("Resuspend number: "+  str(i+1))
        hs_mod.open_labware_latch()
        protocol.move_labware(reagent_plate, new_location=hs_mod, use_gripper=True)
        hs_mod.close_labware_latch()
        for i in range (0, math.ceil(num_samples/8)):
            # right_pipette.pick_up_tip()
            pick_up(right_pipette)
            wash_buffer_amt -= wash_buffer_resuspend_amt/1000*8
            # wet_tip(right_pipette,wash_buffer_storage[math.ceil(wash_buffer_amt/11)-1].bottom(2))
            right_pipette.aspirate(wash_buffer_resuspend_amt, wash_buffer_storage[math.ceil(wash_buffer_amt/10.5)-1].bottom(2), 0.4)

            right_pipette.dispense(wash_buffer_resuspend_amt, reagent_plate['A' + str(i+1)].bottom(2), rate= 0.5)
            if wash_num == num_washes-1:        # last wass
                mix_sides(right_pipette,5, wash_buffer_resuspend_amt,reagent_plate['A' + str(i+1)], 0.7)
            else:
                mix_sides(right_pipette,4, wash_buffer_resuspend_amt,reagent_plate['A' + str(i+1)], 0.7)
            # right_pipette.mix(4, wash_buffer_resuspend_amt-10, reagent_plate['A' + str(i+1)].bottom(2),rate= 3)
            right_pipette.blow_out(reagent_plate['A' + str(i+1)].top())
            right_pipette.blow_out(reagent_plate['A' + str(i+1)].top())
            right_pipette.touch_tip()
            remove_tip(right_pipette, protocol.params.dry_run)

        protocol.comment("Gentil agitation for 1 minute ("+str(shake_speed)+"rpm)")
        # hs_mod.open_labware_latch()
        # protocol.move_labware(reagent_plate, hs_mod, use_gripper=True)
        # hs_mod.close_labware_latch()
        hs_mod.set_and_wait_for_shake_speed(shake_speed)       #1300 rpm
        delay(60)
        hs_mod.deactivate_shaker()
        hs_mod.open_labware_latch()
        protocol.move_labware(reagent_plate, magnetic_block, use_gripper=True)
        protocol.delay(seconds=bead_settle_time, msg="waiting for beads to settle (20 sec)")
        if wash_num == num_washes-1:       # last wash
            aspirate_spuernatent_to_trash(right_pipette, wash_buffer_resuspend_amt+35, 0.2)
        elif wash_num == 0:      # first wash
            aspirate_spuernatent_to_trash(right_pipette, wash_buffer_resuspend_amt-10, 0.2)
        else:
            aspirate_spuernatent_to_trash(right_pipette, wash_buffer_resuspend_amt, 0.2)
    hs_mod.open_labware_latch()
    protocol.move_labware(reagent_plate, new_location=hs_mod, use_gripper=True)
    hs_mod.close_labware_latch()

    protocol.comment("\n\n--------------------Protein Digestion Procedure-----------------------")
    protocol.comment("Resuspending microparticles with absorbed protein mix in 100-200µl digestion buffer")
    
    #DO THE MATH AND FIX THIS PART LATER
    for i in range (0, math.ceil(num_samples/8)):
        pick_up(right_pipette)
        right_pipette.aspirate(digestion_buffer_per_sample_amt, digestion_buffer_reservoir['A1'], 0.1)
        right_pipette.dispense(digestion_buffer_per_sample_amt, reagent_plate['A' + str(i+1)].bottom(1), 0.25)
        right_pipette.blow_out(reagent_plate['A' + str(i+1)].top(1))
        right_pipette.blow_out(reagent_plate['A' + str(i+1)].top(1))
        remove_tip(right_pipette, protocol.params.dry_run)
    
    #MIXING DIGESTION BUFFER
    for i in range (0, math.ceil(num_samples/8)):
        pick_up(right_pipette)
        mix_sides(right_pipette, 3, digestion_buffer_per_sample_amt-15, reagent_plate['A' + str(i+1)],0.5)
        # mix_sides_no_bubbles(right_pipette, 3, digestion_buffer_per_sample_amt-15, reagent_plate['A' + str(i+1)],1.5)
        right_pipette.blow_out(reagent_plate['A' + str(i+1)].top())
        right_pipette.blow_out(reagent_plate['A' + str(i+1)].top())
        # right_pipette.blow_out(reagent_plate['A' + str(i+1)].top(1))
        remove_tip(right_pipette, protocol.params.dry_run)
        
    protocol.comment("\nIncubating sample at 47°C for ___ hours. Mix continuously at "+str(shake_speed)+" rpm")
    hs_mod.open_labware_latch()
    protocol.pause('''Put the lid on!!!''')
    hs_mod.close_labware_latch()
    hs_mod.set_and_wait_for_shake_speed(1450)       #1000 rpm
    hs_mod.set_and_wait_for_temperature(47)         #37°C
    protocol.pause('''Tell me when to stop!! (4hr or overnight incubation time)''')
    # protocol.delay(minutes=1/6 if protocol.params.dry_run else 240, msg="4 hour incubation at 37°C (10 seconds for dry run)")
    hs_mod.deactivate_shaker()
    hs_mod.deactivate_heater()
    hs_mod.open_labware_latch()
    protocol.pause('''Remove the lid and place on magnetic block''')

    protocol.comment("\nRecovering the microparticles on magnetic separator and aspirating the supernatant containing peptides with a pipette")
    protocol.move_labware(reagent_plate, magnetic_block, use_gripper=False)
    # left_pipette.pick_up_tip()
    # left_pipette.pick_up_tip()
    # pick_up(left_pipette)
    # protocol.delay(seconds=bead_settle_time, msg=
    # "waiting for beads to settle (20 sec)")
    for i in range (0, num_samples):
        # left_pipette.pick_up_tip()
        pick_up(left_pipette)
        left_pipette.aspirate(digestion_buffer_per_sample_amt+10, reagent_plate.wells()[i].bottom(0.15), 0.2)
        left_pipette.dispense(digestion_buffer_per_sample_amt+10, final_tube_rack.wells()[i].bottom(0.25), 0.2)
        left_pipette.blow_out(final_tube_rack.wells()[i].bottom(7))
        left_pipette.touch_tip()
        # left_pipette.return_tip()
        remove_tip(left_pipette, protocol.params.dry_run)
    for i in range (0,num_samples):
        pick_up(left_pipette)
        left_pipette.aspirate(5, formic_acid_storage.bottom(0.1), 0.2)
        left_pipette.dispense(5, final_tube_rack.wells()[i].bottom(0.25), 0.2)
        remove_tip(left_pipette, protocol.params.dry_run)