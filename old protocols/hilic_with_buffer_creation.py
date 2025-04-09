from opentrons import protocol_api
import math
import urllib.request
import urllib.parse
import json
from opentrons import types
# from datetime import datetime, timedelta
import time
from datetime import datetime

metadata = {
    "protocolName": "AAAA SP3 HILIC protocol (creates buffers)",
    "author": "Nico To",
    "description": "HILIC sp3 protocol",
}

requirements = {"robotType": "Flex", "apiLevel": "2.19"}

def add_parameters(parameters: protocol_api.Parameters):

    parameters.add_int(
        variable_name="numSamples",
        display_name="Number of Samples",
        description="Number of samples",
        default=8,
        minimum=1,
        maximum=100,
        unit="samples"
    )
    # Keep 300 as default
    parameters.add_int(
        variable_name="ammoniumAcetate_conc",
        display_name="Concentration Ammonium Acetate",
        description="_______ mM Ammonium Acetate (4.5pH)",
        default=300,
        minimum=100,
        maximum=1000,
        unit="mM"
    )
    # Default true
    parameters.add_bool(
        variable_name="manual_load_beads",
        display_name="Load beads with walt",
        description="Use walt to load beads",
        default=True
    )
    #Default true
    parameters.add_bool(
        variable_name="create_buffers",
        display_name="Create buffers with Walt",
        description="Use walt to create/mix binding, wash, and equilibration buffers",
        default=False
    )
    # ADD REDUCTION AND ALKYLATION AS A PARAMETER 
    
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
    Volume: volume of liquid in tube in ml
    Return: height in mm from the bottom of tube that pipette should go to
    '''
    if volume <= 1:     # cone part aaa
        # print(-3.33*(volume**2)+15.45*volume+9.50)
        return -3.33*(volume**2)+15.45*volume+9.50 - 1   #−3.33x2+15.45x+9.50
    else:
        return 6.41667*volume +15.1667 -5    
def get_height_50ml_falcon(volume):
    '''
    Get's the height of the liquid in the tube
    Volume: volume of liquid in tube in µl
    Return: hieght from bottom of tube in millimeters
    '''
    height = (1.8*(volume/1000))+12-3
    return height
def get_eq_buffer_vols(total_buffer_amt, ammonium_acetate_concentration):
    '''
    total_buffer_amt: amount of buffer being created in ul
    ammonium_acetate_concentration: Concentration of Ammonium acetate 
    Returns: A dictionary with all the volumes in ul
    '''
    acn = total_buffer_amt*0.15     #amount of acetonitrle
    ammonium_acetate = (total_buffer_amt-acn)*(100/ammonium_acetate_concentration)
    water = total_buffer_amt-acn-ammonium_acetate
    final_vols = {"acn": acn,
                  "ammonium_acetate": ammonium_acetate,
                  "water": water}
    return final_vols

def get_binding_buffer_vols(total_buffer_amt, ammonium_acetate_concentration):
    '''
    total_buffer_amt: amount of buffer being created in ul
    ammonium_acetate_concentration: Concentration of Ammonium acetate 
    Returns: A dictionary with all the volumes in ul
    '''
    acn = total_buffer_amt*0.30     #amount of acetonitrle
    ammonium_acetate = (total_buffer_amt-acn)*(200/ammonium_acetate_concentration)
    water = total_buffer_amt-acn-ammonium_acetate
    final_vols = {"acn": acn,
                  "ammonium_acetate": ammonium_acetate,
                  "water": water}
    return final_vols
def get_wash_buffer_vols(total_buffer_amt):
    '''
    total_buffer_amt: amount of buffer being created in ul
    ammonium_acetate_concentration: Concentration of Ammonium acetate 
    Returns: A dictionary with all the volumes in ul
    '''
    acn = total_buffer_amt*0.95     #amount of acetonitrle
    water = total_buffer_amt-acn
    final_vols = {"acn": acn,
                  "water": water}
    return final_vols

def run(protocol: protocol_api.ProtocolContext):
    #defining variables
    wash_volume = 100#protocol.params.wash_volume   #µl
    shake_speed = 1400#protocol.params.shake_speed   #rpm
    num_washes = 2
    num_samples = protocol.params.numSamples
    bead_settle_time = 10 #seconds
    
    bead_amt = 12.5#(num_samples)*25     #µl
    protein_sample_amt = 60#protocol.params.protein_sample_amt     # amount of protein per sample (µl)
    equilibartion_buffer_amt = (300*8*(math.ceil(num_samples/8)) + 1000)/1000       #ml
    binding_buffer_amt = (40*8*(math.ceil(num_samples/8)) + 500)/1000       #ml
    wash_buffer_amt = (300*8*(math.ceil(num_samples/8)) + 1000)/1000       #ml
    digestion_buffer_per_sample_amt = 100#protocol.params.digestion_buffer_per_sample_amt       #100-150µl
    
    #loading
    tips1000 = [protocol.load_labware("opentrons_flex_96_filtertiprack_200uL", slot) for slot in ["A3","B3","C3"]]
    chute = protocol.load_waste_chute()
    left_pipette = protocol.load_instrument("flex_1channel_1000", "left", tip_racks=tips1000)
    right_pipette = protocol.load_instrument("flex_8channel_1000", "right", tip_racks=tips1000)
    magnetic_block = protocol.load_module(module_name="magneticBlockV1", location="C1")
    hs_mod = protocol.load_module(module_name="heaterShakerModuleV1", location="D1")    #heat shaker module
    tube_rack = protocol.load_labware("opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap", "A2", "bead + final solution rack")
    sample_plate = protocol.load_labware("opentrons_96_wellplate_200ul_pcr_full_skirt", "A1", "sample stock plate")
    reagent_plate = hs_mod.load_labware("opentrons_96_wellplate_200ul_pcr_full_skirt","reagent plate")
    digestion_buffer_reservoir = protocol.load_labware("nest_96_wellplate_2ml_deep", location= "B2")        ## change deck location
    # final_sample_plate = protocol.load_labware("opentrons_96_wellplate_200ul_pcr_full_skirt", "B1", "reagent plate")
    # buffer_rack = protocol.load_labware("opentrons_10_tuberack_falcon_4x50ml_6x15ml_conical", "B1", "reagent stock rack")   # equilibration, binding, and wash buffer
    working_reagent_reservoir = protocol.load_labware("nest_12_reservoir_15ml", "D2")
    final_tube_rack = protocol.load_labware("opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap", "B1", "final solution rack")
    # trash_reservoir = protocol.load_labware("nest_1_reservoir_195ml", "C2", "trash reservoir")
    
    #defining liquids
    bead_sol = protocol.define_liquid("HILIC Bead Solution", "An alloquat of the HILIC bead solution", "#000000")
    equilibration_buffer = protocol.define_liquid("Equilibration Buffer", "100mM ammonium acetate, pH 4.5, 15%% acetonitrile", "#32a852")
    binding_buffer = protocol.define_liquid("Binding Buffer", "200mM ammonium acetate, pH 4.5, 30%% acetonitrile", "#8d32a8")
    wash_buffer = protocol.define_liquid("Wash Buffer", "95%% acetonitrile (5% water)", "#05a1f5")
    digestion_buffer = protocol.define_liquid("Digestion Buffer", "95%% acetonitrile (5% water)", "#fafa02")          # CHANGE THIS AFTER ASKING LAURA
    water = protocol.define_liquid("water", "water", "#00b7ff")
    acetonitrile = protocol.define_liquid("acn", "acn", "#03fc31")
    ammoniumAcetate = protocol.define_liquid("ammonium acetate", "ammonium acetate", "#fa05ee")
    # Loading Liquids
    tube_rack["A1"].load_liquid(bead_sol, bead_amt)
    bead_storage = tube_rack["A1"]
    # tube_rack["B1"].load_liquid(digestion_buffer, digestion_buffer_stock_amt)
    # digestion_buffer_storage = tube_rack["B1"]
    # digestion_buffer_storage = reservoir.columns_by_name()['1']
    # digestion_buffer_storage.load_liquid(digestion_buffer, digestion_buffer_stock_amt)
    buffer_tube_rack = protocol.load_labware("opentrons_10_tuberack_falcon_4x50ml_6x15ml_conical", "C2", "new solution rack")
    buffer_tube_rack["A1"].load_liquid(digestion_buffer, digestion_buffer_per_sample_amt*num_samples)
    dig_buffer_location = buffer_tube_rack["A1"]
    
    buffer_tube_rack["A3"].load_liquid(water, 100)
    water_location = buffer_tube_rack["A3"]
    buffer_tube_rack["A4"].load_liquid(acetonitrile, 100)
    acn_location = buffer_tube_rack["A4"]
    buffer_tube_rack["B3"].load_liquid(ammoniumAcetate, 100)
    ammoniumAcetate_location = buffer_tube_rack["B3"]

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

#REPLENISHING TIPS

    count = 0
    #Functions
    def remove_tip(pipette, is_dry_run):
        if is_dry_run:
            pipette.return_tip()
        else:
            pipette.drop_tip(chute)         
    def aspirate_spuernatent_to_trash(pipette, amt, speed, discard_tip = True, height = 0.1):
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
        nonlocal tips1000
        nonlocal staging_racks
        nonlocal count

        try:
            pip.tip_racks = tips1000
            pip.pick_up_tip()

        except protocol_api.labware.OutOfTipsError:
            check_tips()
            pick_up(pip)    
    def check_tips():
        nonlocal tips1000
        nonlocal staging_racks
        nonlocal count
        # tip_box = protocol.load_labware('opentrons_flex_96_filtertiprack_1000uL', 'A3')
        for i in range (0,3):
            tip_box_slots = ['A3', 'B3', 'C3']
            bottom_right_well = tips1000[i].wells_by_name()['H12']
            
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
                        labware=tips1000[i],
                        new_location=chute,
                        use_gripper=True
                    )
                rack_num = 0
                for slot in ['A4', 'B4', 'C4', 'D4']:
                    labware = protocol.deck[slot]
                    if labware and labware.is_tiprack:
                        tips1000[i] = staging_racks[rack_num]
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

    
    def mix_sides(pipette, num_mixes, vol, plate, rate):
        pipette.mix(num_mixes, vol, plate.bottom().move(types.Point(x=0, y=2, z=3.5)),rate= rate)
        pipette.mix(num_mixes, vol, plate.bottom().move(types.Point(x=0, y=-2, z=3.5)),rate= rate)
        pipette.mix(num_mixes, vol, plate.bottom().move(types.Point(x=2, y=0, z=3.5)),rate= rate)
        pipette.mix(num_mixes, vol, plate.bottom().move(types.Point(x=-2, y=0, z=3.5)),rate= rate)        
    
    def mix_sides_no_bubbles(pipette, num_mixes, vol, plate, rate):
        for i in range (0, num_mixes):
            pipette.aspirate(vol, plate.bottom(0.1), rate = 0.2)
            pipette.dispense(vol, plate.bottom().move(types.Point(x=0, y=1.5, z=3)), rate = rate)
        for i in range (0, num_mixes):
            pipette.aspirate(vol, plate.bottom(0.1), rate = 0.2)
            pipette.dispense(vol, plate.bottom().move(types.Point(x=0, y=-1.5, z=3)), rate = rate)
        for i in range (0, num_mixes):
            pipette.aspirate(vol, plate.bottom(0.1), rate = 0.2)
            pipette.dispense(vol, plate.bottom().move(types.Point(x=1.5, y=0, z=3)), rate = rate)
        for i in range (0, num_mixes):
            pipette.aspirate(vol, plate.bottom(0.1), rate = 0.2)
            pipette.dispense(vol, plate.bottom().move(types.Point(x=-1.5, y=0, z=3)), rate = rate)
        pipette.aspirate(vol, plate.bottom(0.1), rate = 0.2)
        pipette.dispense(vol-3, plate.bottom(0.1), rate = 0.2)
        pipette.blow_out(plate.top())

    def create_buffers(total_vol, start_location, end_location):
        '''
        total_vol: list of transfer volumes in ul [vol1, vol2]
        start_location: location of the acn, aa, or h2o
        end_location: well number of the first slot for the buffer (1 to 12)
        '''
        protocol.comment(str(total_vol))
        for i in range (0, len(total_vol)):
            vol = total_vol[i]
            for x in range (0, math.ceil(vol/1000)):
                if x != math.ceil(vol/1000)-1:  #not last one yet
                    left_pipette.aspirate(1000, start_location)
                    left_pipette.dispense(1000, working_reagent_reservoir["A" +str(end_location+i)].top(-5))
                else:
                    left_pipette.aspirate(vol-(1000*x), start_location)
                    left_pipette.dispense(vol-(1000*x),working_reagent_reservoir["A" +str(end_location+i)].top(-5))
                left_pipette.blow_out(working_reagent_reservoir["A" +str(end_location+i)].top(-5))
    def delay(seconds):
        if protocol.params.dry_run:
            return
        start_time = datetime.now()
        protocol.comment(f"Delaying for {seconds} seconds")
        check_tips()
        while True:
            if (datetime.now() - start_time).seconds > seconds:
                break
    
    if protocol.params.create_buffers:
        protocol.comment("-------------BUFFER CREATION ---------------")
        channel_max_vol = 10000 #each channel can hold up to 10000 ul
        acn_eq_vols = []
        acn_binding_vols = []
        acn_wash_vols = []
        aa_eq_vols = []
        aa_binding_vols = []
        water_eq_vols = []
        water_binding_vols = []
        water_wash_vols = []
        #equilibartion buffer
        for i in range (0, math.ceil((equilibartion_buffer_amt*1000)/channel_max_vol)):
            #Not on last loop yet
            if i !=math.ceil((equilibartion_buffer_amt*1000)/channel_max_vol)-1:
                volumes =get_eq_buffer_vols(channel_max_vol, protocol.params.ammoniumAcetate_conc)
                acn_eq_vols.append(volumes['acn'])
                aa_eq_vols.append(volumes['ammonium_acetate'])
                water_eq_vols.append(volumes['water'])
            else:
                volumes =get_eq_buffer_vols((equilibartion_buffer_amt*1000)-(channel_max_vol*i), protocol.params.ammoniumAcetate_conc)
                acn_eq_vols.append(volumes['acn'])
                aa_eq_vols.append(volumes['ammonium_acetate'])
                water_eq_vols.append(volumes['water'])
        #Binding buffer
        for i in range (0, math.ceil((binding_buffer_amt*1000)/channel_max_vol)):
            #Not on last loop yet
            if i !=math.ceil((binding_buffer_amt*1000)/channel_max_vol)-1:
                volumes =get_binding_buffer_vols(channel_max_vol, protocol.params.ammoniumAcetate_conc)
                acn_binding_vols.append(volumes['acn'])
                aa_binding_vols.append(volumes['ammonium_acetate'])
                water_binding_vols.append(volumes['water'])
            else:
                volumes =get_binding_buffer_vols((equilibartion_buffer_amt*1000)-(channel_max_vol*i), protocol.params.ammoniumAcetate_conc)
                acn_binding_vols.append(volumes['acn'])
                aa_binding_vols.append(volumes['ammonium_acetate'])
                water_binding_vols.append(volumes['water'])
        #Wash buffer
        for i in range (0, math.ceil((wash_buffer_amt*1000)/channel_max_vol)):
            #Not on last loop yet
            if i !=math.ceil((wash_buffer_amt*1000)/channel_max_vol)-1:
                volumes =get_wash_buffer_vols(channel_max_vol)
                acn_wash_vols.append(volumes['acn'])
                water_wash_vols.append(volumes['water'])
            else:
                volumes =get_wash_buffer_vols((equilibartion_buffer_amt*1000)-(channel_max_vol*i))
                acn_wash_vols.append(volumes['acn'])
                water_wash_vols.append(volumes['water'])
        
        #Loading ACN
        left_pipette.pick_up_tip()
        create_buffers(acn_eq_vols, acn_location, 1)
        create_buffers(acn_binding_vols, acn_location, 4)
        create_buffers(acn_wash_vols, acn_location, 7)
        remove_tip(left_pipette, protocol.params.dry_run)
        
        #Loading Ammonium Acetate
        left_pipette.pick_up_tip()
        create_buffers(aa_eq_vols, ammoniumAcetate_location, 1)
        create_buffers(aa_binding_vols, ammoniumAcetate_location, 4)
        remove_tip(left_pipette, protocol.params.dry_run)
        #Loading H2O
        left_pipette.pick_up_tip()
        create_buffers(water_eq_vols, water_location, 1)
        create_buffers(water_binding_vols, water_location, 4)
        create_buffers(water_wash_vols, water_location, 7)
        remove_tip(left_pipette, protocol.params.dry_run)
        protocol.comment("\n"*10)
        protocol.comment(str(acn_eq_vols))
        protocol.comment(str(acn_binding_vols))
        protocol.comment(str(acn_wash_vols))
        protocol.comment(str(aa_eq_vols))
        protocol.comment(str(aa_binding_vols))
        protocol.comment(str(water_eq_vols))
        protocol.comment(str(water_binding_vols))
        protocol.comment(str(water_wash_vols))
        protocol.comment("\n"*10)

        for j in range (0,3):
            i = [acn_eq_vols, acn_binding_vols, acn_wash_vols][j]
            left_pipette.pick_up_tip()
            for x in range (0, len(i)):
                left_pipette.mix(3, 900, working_reagent_reservoir["A"+str(1+j*3+x)].bottom().move(types.Point(x=0, y=-20, z=3)))
                left_pipette.mix(3, 900, working_reagent_reservoir["A"+str(1+j*3+x)].bottom().move(types.Point(x=0, y=0, z=3)))
                left_pipette.mix(3, 900, working_reagent_reservoir["A"+str(1+j*3+x)].bottom().move(types.Point(x=0, y=20, z=3)))
            remove_tip(left_pipette, protocol.params.dry_run)
            
    hs_mod.open_labware_latch()
    hs_mod.close_labware_latch()
    protocol.comment("-------------Equilibration ---------------")
    if protocol.params.manual_load_beads:

        pipette_max = 195
        num_transfers = math.ceil((bead_amt*num_samples)/(pipette_max))
        well_counter = 0
        protocol.comment("\nTransfering 25µl HILIC beads into well plate")
        pick_up(left_pipette)
        total_bead_amt = num_samples*25
        num_transfers = math.ceil(total_bead_amt / (math.floor((pipette_max-10)/bead_amt)*bead_amt))
        for i in range (0, num_transfers):
            if i != num_transfers - 1:      # not on last iteration
                aspirate_amt = math.floor((pipette_max-10)/bead_amt)*bead_amt
            else:
                aspirate_amt = total_bead_amt
            #mix
            if total_bead_amt > pipette_max:
                left_pipette.mix(3, pipette_max, bead_storage, 0.5)
                left_pipette.blow_out(bead_storage.top())
            else: 
                left_pipette.mix(3, total_bead_amt-10, bead_storage, 0.5)
                left_pipette.blow_out(bead_storage.top())
            left_pipette.aspirate(aspirate_amt+5, bead_storage.bottom(0.1), rate=0.5)
            total_bead_amt -= aspirate_amt
            for x in range (0, math.floor(aspirate_amt/bead_amt)):
                left_pipette.dispense(bead_amt, reagent_plate.wells()[well_counter].bottom(1), rate=0.5)
                well_counter += 1
        remove_tip(left_pipette, protocol.params.dry_run)
        
    protocol.comment("\nPlacing tube on magnetic separator and allowing 10s for microparticles to clear")
    hs_mod.open_labware_latch()
    protocol.move_labware(reagent_plate, magnetic_block, use_gripper=True)
    protocol.delay(seconds=bead_settle_time+5, msg="waiting 7 seconds for microparticles to clear")
    aspirate_spuernatent_to_trash(right_pipette, 25-17, 0.1, discard_tip=False, height=0.3)


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
            right_pipette.touch_tip()
        remove_tip(right_pipette, protocol.params.dry_run)

        protocol.comment("Gentil agitation for 1 minute ("+str(shake_speed)+"rpm)")
        hs_mod.set_and_wait_for_shake_speed(shake_speed)       #1000 rpm
        check_tips()
        protocol.delay(60)
        # delay(60)
        hs_mod.deactivate_shaker()
        hs_mod.open_labware_latch()
        
        if wash_num == 0:   # first wash
            hs_mod.open_labware_latch()
            protocol.move_labware(reagent_plate, magnetic_block, use_gripper=True)
            protocol.delay(seconds=bead_settle_time+5, msg="waiting for beads to settle (20 sec)")
            aspirate_spuernatent_to_trash(right_pipette, wash_volume-15, 0.25, discard_tip=False, height=0.3)       # leave the last 5ul in the well plate
        elif wash_num != num_washes-1:      # Not on the last wash yet
            hs_mod.open_labware_latch()
            protocol.move_labware(reagent_plate, magnetic_block, use_gripper=True)
            protocol.delay(seconds=bead_settle_time+5, msg="waiting for beads to settle (20 sec)")
            aspirate_spuernatent_to_trash(right_pipette, wash_volume, 0.25, discard_tip=False, height=0.3)       # leave the last 5ul in the well plate
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
        right_pipette.aspirate(50, sample_plate['A' + str(i+1)].bottom(0.5), rate=0.1)
        right_pipette.dispense(40, reagent_plate['A' + str(i+1)].bottom(1), rate=0.1)
        mix_sides(right_pipette, 2, 20, reagent_plate['A' + str(i+1)], 2)
        # right_pipette.mix(3, 30, reagent_plate['A' + str(i+1)].bottom(0.5), rate=0.1)
        right_pipette.dispense(10, reagent_plate['A' + str(i+1)].top(1), rate=0.1)
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
        for i in range (0, math.ceil(transfer_vol/pipette_max)):
            if i != math.ceil(transfer_vol/pipette_max):    # not on last iteration
                aspirate_vol = pipette_max
            else: 
                aspirate_vol = transfer_vol - (pipette_max*i)
            left_pipette.aspirate(aspirate_vol, dig_buffer_location, 0.25)    
            left_pipette.dispense(aspirate_vol, digestion_buffer_reservoir.wells()[well_counter].bottom(), 0.1)
    remove_tip(left_pipette, protocol.params.dry_run)
    time_elasped = (datetime.now() - start_time).seconds
    # 30 minute incubation
    protocol.delay(1800-time_elasped)
    
    hs_mod.deactivate_shaker()
    hs_mod.open_labware_latch()
    protocol.move_labware(reagent_plate, magnetic_block, use_gripper=True)
    protocol.delay(seconds=bead_settle_time, msg="waiting for beads to settle (20 sec)")
    aspirate_spuernatent_to_trash(right_pipette, wash_volume - 15, 0.1)

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
            right_pipette.touch_tip()
            remove_tip(right_pipette, protocol.params.dry_run)

        protocol.comment("Gentil agitation for 1 minute ("+str(shake_speed)+"rpm)")
        # hs_mod.open_labware_latch()
        # protocol.move_labware(reagent_plate, hs_mod, use_gripper=True)
        # hs_mod.close_labware_latch()
        hs_mod.set_and_wait_for_shake_speed(shake_speed)       #1300 rpm
        # delay(60)
        protocol.delay(60)
        hs_mod.deactivate_shaker()
        hs_mod.open_labware_latch()
        protocol.move_labware(reagent_plate, magnetic_block, use_gripper=True)
        protocol.delay(seconds=bead_settle_time, msg="waiting for beads to settle (20 sec)")
        if wash_num == num_washes-1:       # last wash
            aspirate_spuernatent_to_trash(right_pipette, wash_buffer_resuspend_amt+35, 0.1)
        if wash_num == 0:      # first wash
            aspirate_spuernatent_to_trash(right_pipette, wash_buffer_resuspend_amt-10, 0.1)
        else:
            aspirate_spuernatent_to_trash(right_pipette, wash_buffer_resuspend_amt, 0.1)
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
        mix_sides_no_bubbles(right_pipette, 3, digestion_buffer_per_sample_amt-15, reagent_plate['A' + str(i+1)],1.5)
        right_pipette.blow_out(reagent_plate['A' + str(i+1)].top())
        # right_pipette.blow_out(reagent_plate['A' + str(i+1)].top(1))
        remove_tip(right_pipette, protocol.params.dry_run)
        
    protocol.comment("\nIncubating sample at 37°C for 4 hours. Mix continuously at "+str(shake_speed)+" rpm")
    hs_mod.open_labware_latch()
    protocol.pause('''Put the lid on!!!''')
    hs_mod.close_labware_latch()
    hs_mod.set_and_wait_for_shake_speed(1450)       #1000 rpm
    hs_mod.set_and_wait_for_temperature(37)         #37°C
    protocol.pause('''Tell me when to stop!! (4hr or overnight incubation time)''')
    # protocol.delay(minutes=1/6 if protocol.params.dry_run else 240, msg="4 hour incubation at 37°C (10 seconds for dry run)")
    hs_mod.deactivate_shaker()
    hs_mod.deactivate_heater()
    hs_mod.open_labware_latch()
    protocol.pause('''Remove the lid and place on magnetic block''')

    protocol.comment("\nRecovering the microparticles on magnetic separator and aspirating the supernatant containing peptides with a pipette")
    protocol.move_labware(reagent_plate, magnetic_block, use_gripper=False)
    # protocol.delay(seconds=bead_settle_time, msg=
    # "waiting for beads to settle (20 sec)")
    # for i in range (0, num_samples):
    #     # left_pipette.pick_up_tip()
    #     pick_up(left_pipette)
    #     left_pipette.aspirate(digestion_buffer_per_sample_amt+10, reagent_plate.wells()[i].bottom(0.15), 0.2)
    #     left_pipette.dispense(digestion_buffer_per_sample_amt+10, final_tube_rack.wells()[i].bottom(0.25), 0.2)
    #     left_pipette.blow_out(final_tube_rack.wells()[i].bottom(7))
    #     left_pipette.touch_tip()
    #     # left_pipette.return_tip()
    #     remove_tip(left_pipette, protocol.params.dry_run)
        # protocol.move_labware(reagent_plate, magnetic_block, use_gripper=False)
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