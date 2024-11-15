from opentrons import protocol_api
import math
import urllib.request
import urllib.parse
import json
from opentrons import types



metadata = {
    "protocolName": "SP3 HILIC protocol",
    "author": "Nico To",
    "description": "HILIC sp3 protocol",
}

requirements = {"robotType": "Flex", "apiLevel": "2.19"}

def add_parameters(parameters: protocol_api.Parameters):

    parameters.add_int(
        variable_name="numSamples",
        display_name="Number of Samples",
        description="Number of samples",
        default=10,
        minimum=1,
        maximum=24,
        unit="samples"
    )
    parameters.add_int(
        variable_name="protein_sample_amt",
        display_name="protein_sample_amt",
        description="amount of protein sample (needs to be mixed 1:1 with binding buffer)",
        default=40,
        minimum=1,
        maximum=1500,
        unit="ul"
    )
    parameters.add_int(
        variable_name="equilibartion_buffer_amt",
        display_name="equilibartion_buffer_amt",
        description="amount of equilibration buffer stock",
        default=6,
        minimum=1,
        maximum=30,
        unit="ml"
    )
    parameters.add_int(
        variable_name="binding_buffer_amt",
        display_name="binding_buffer_amt",
        description="amount of binding buffer stock",
        default=6,
        minimum=1,
        maximum=30,
        unit="ml"
    )
    parameters.add_int(
        variable_name="wash_buffer_amt",
        display_name="wash_buffer_amt",
        description="amount of wash buffer stock",
        default=6,
        minimum=1,
        maximum=30,
        unit="ml"
    )
    parameters.add_int(
        variable_name="digestion_buffer_stock_amt",
        display_name="digestion_buffer_stock_amt",
        description="amount of digestion buffer stock",
        default=410,
        minimum=1,
        maximum=1500,
        unit="ul"
    )
    parameters.add_int(
        variable_name="digestion_buffer_per_sample_amt",
        display_name="digestion buffer per sample",
        description="amount of digestion buffer per sample",
        default=100,
        minimum=1,
        maximum=1500,
        unit="ul"
    )
    parameters.add_int(
        variable_name="wash_volume",
        display_name="wash volume",
        description="of buffer the samples are going to be washed in",
        default=100,
        minimum=1,
        maximum=200,
        unit="ul"
    )
    parameters.add_int(
        variable_name="shake_speed",
        display_name="shake speed",
        description="speed of the heat shaker",
        default=1400,
        minimum=200,
        maximum=3000,
        unit="rpm"
    )
    parameters.add_bool(
        variable_name="dry_run",
        display_name="Dry Run",
        description="Skip incubation delays and return tips.",
        default=False
    )
    parameters.add_bool(
        variable_name="manual_load_beads",
        display_name="Load beads with walt",
        description="Use walt to load beads",
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

def get_height_falcon(volume):
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

# def send_email(msg):
    

def run(protocol: protocol_api.ProtocolContext):
    #defining variables
    wash_volume = protocol.params.wash_volume   #µl
    shake_speed = protocol.params.shake_speed   #rpm
    num_washes = 3
    num_samples = protocol.params.numSamples
    bead_settle_time = 15 #seconds
    
    bead_amt = (num_samples)*25     #µl
    protein_sample_amt = protocol.params.protein_sample_amt     # amount of protein per sample (µl)
    equilibartion_buffer_amt = protocol.params.equilibartion_buffer_amt       #ml
    binding_buffer_amt = protocol.params.binding_buffer_amt       #ml
    wash_buffer_amt = protocol.params.wash_buffer_amt       #ml
    digestion_buffer_stock_amt = protocol.params.digestion_buffer_stock_amt    #µl
    digestion_buffer_per_sample_amt = protocol.params.digestion_buffer_per_sample_amt       #100-150µl
    
    #loading
    tips1000 = [protocol.load_labware("opentrons_flex_96_filtertiprack_1000uL", slot) for slot in ["A3","B3","C3"]]
    chute = protocol.load_waste_chute()
    left_pipette = protocol.load_instrument("flex_1channel_1000", "left", tip_racks=tips1000)
    right_pipette = protocol.load_instrument("flex_8channel_1000", "right", tip_racks=tips1000)
    magnetic_block = protocol.load_module(module_name="magneticBlockV1", location="C1")
    hs_mod = protocol.load_module(module_name="heaterShakerModuleV1", location="D1")    #heat shaker module
    tube_rack = protocol.load_labware("opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap", "A2", "final solution rack")
    sample_plate = protocol.load_labware("opentrons_96_wellplate_200ul_pcr_full_skirt", "A1", "sample stock plate")
    reagent_plate = magnetic_block.load_labware("opentrons_96_wellplate_200ul_pcr_full_skirt","reagent plate")
    digestion_buffer_plate = protocol.load_labware("opentrons_96_wellplate_200ul_pcr_full_skirt", "B2", "digestion buffer plate")
    # final_sample_plate = protocol.load_labware("opentrons_96_wellplate_200ul_pcr_full_skirt", "B1", "reagent plate")
    # buffer_rack = protocol.load_labware("opentrons_10_tuberack_falcon_4x50ml_6x15ml_conical", "B1", "reagent stock rack")   # equilibration, binding, and wash buffer
    working_reagent_reservoir = protocol.load_labware("nest_12_reservoir_15ml", "D2")
    final_tube_rack = protocol.load_labware("opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap", "B1", "final solution rack")
    trash_reservoir = protocol.load_labware("nest_1_reservoir_195ml", "C2", "trash reservoir")
    
    #defining liquids
    bead_sol = protocol.define_liquid("HILIC Bead Solution", "An alloquat of the HILIC bead solution", "#000000")
    equilibration_buffer = protocol.define_liquid("Equilibration Buffer", "100mM ammonium acetate, pH 4.5, 15%% acetonitrile", "#32a852")
    binding_buffer = protocol.define_liquid("Binding Buffer", "200mM ammonium acetate, pH 4.5, 30%% acetonitrile", "#8d32a8")
    wash_buffer = protocol.define_liquid("Wash Buffer", "95%% acetonitrile (5% water)", "#05a1f5")
    digestion_buffer = protocol.define_liquid("Digestion Buffer", "95%% acetonitrile (5% water)", "#05a1f5")          # CHANGE THIS AFTER ASKING LAURA
    lysis_buffer = protocol.define_liquid("Lysis Buffer", "50MM Teab, 3.8% SDS", "#05a1f5")          # CHANGE THIS AFTER ASKING LAURA
    dtt = protocol.define_liquid("dtt", "dtt 1000mM stock", "#fcba03")
    iaa = protocol.define_liquid("iaa", "iaa 500mM stock", "#fc0303")
    
    # Loading Liquids
    tube_rack["A1"].load_liquid(bead_sol, bead_amt)
    bead_storage = tube_rack["A1"]
    tube_rack["B1"].load_liquid(digestion_buffer, digestion_buffer_stock_amt)
    digestion_buffer_storage = tube_rack["B1"]
    
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
    
    trash1=trash_reservoir.wells()[0].bottom(7)
    staging_slots = ['A4', 'B4', 'C4']
    staging_racks = [protocol.load_labware('opentrons_flex_96_filtertiprack_1000uL',
                                      slot) for slot in staging_slots]

#REPLENISHING TIPS

    count = 0
    #Functions
    def remove_tip(pipette, is_dry_run):
        if is_dry_run:
            pipette.return_tip()
        else:
            pipette.drop_tip(chute)         
    def aspirate_spuernatent_to_trash(pipette, amt, speed):
        '''amt: amount ot aspirirate out'''
        protocol.comment("\nAspriating supernatant to trash")
        for i in range (0, math.ceil(num_samples/8)):
            pipette.pick_up_tip()
            pipette.aspirate(amt, reagent_plate['A' + str(i+1)].bottom(0.1), rate=speed)
            # pipette.air_gap(volume=10)
            pipette.dispense(amt, trash1,5)
            remove_tip(pipette, protocol.params.dry_run)
    
    def pick_up(pip):
        nonlocal tips1000
        nonlocal staging_racks
        nonlocal count

        try:
            pip.tip_racks = tips1000
            pip.pick_up_tip()

        except protocol_api.labware.OutOfTipsError:
            pip.tip_racks = tips1000

            # move all tipracks to chute
            for rack in tips1000:
                protocol.move_labware(
                    labware=rack,
                    new_location=chute,
                    use_gripper=True
                )
            # check to see if we have tipracks in staging slots
            try:
                for i, (new_rack, replace_slot) in enumerate(zip(staging_racks, ["A3","B3","C3"])):
                    if protocol.deck[staging_slots[i]]:

                        protocol.move_labware(
                            labware=new_rack,
                            new_location=replace_slot,
                            use_gripper=True
                        )
                tips1000 = staging_racks
                pip.tip_racks = tips1000
                pip.reset_tipracks()
                pip.pick_up_tip()

            # if not tipracks in staging slot (second iteration), replenish
            except:
                # tips1000 = [assay.load_labware('opentrons_flex_96_tiprack_50ul', protocol_api.OFF_DECK) for _ in range(3)]
                # staging_racks = [assay.load_labware('opentrons_flex_96_tiprack_50ul', protocol_api.OFF_DECK) for _ in range(3)]
                tips1000 = [protocol.load_labware('opentrons_flex_96_filtertiprack_1000uL', slot) for slot in ["A3","B3","C3"]]
                staging_racks = [protocol.load_labware('opentrons_flex_96_filtertiprack_1000uL', slot) for slot in staging_slots]
                protocol.pause('Replace tip racks on deck and on expansion slots')
                pip.reset_tipracks()
                pip.tip_racks=tips1000
                pick_up(pip)
    
    def mix_sides(pipette, num_mixes, vol, plate, rate):
        pipette.mix(num_mixes, vol, plate.bottom().move(types.Point(x=0, y=2, z=4)),rate= rate)
        pipette.mix(num_mixes, vol, plate.bottom().move(types.Point(x=0, y=-2, z=4)),rate= rate)
        pipette.mix(num_mixes, vol, plate.bottom().move(types.Point(x=2, y=0, z=4)),rate= rate)
        pipette.mix(num_mixes, vol, plate.bottom().move(types.Point(x=-2, y=0, z=4)),rate= rate)        

    if protocol.params.manual_load_beads:
        protocol.comment("-------------Equilibration ---------------")
        protocol.comment("Vortex Mixing for 3 seconds")
        left_pipette.pick_up_tip()

        left_pipette.mix(3, bead_amt-7, bead_storage.bottom(1))
        
        protocol.comment("\nTransfering 25µl HILIC beads into well plate")
        for i in range (0, num_samples):
            if left_pipette.has_tip == False:
                left_pipette.pick_up_tip()
            if  i != 0: # mix every 6 samples
                left_pipette.mix(3, bead_amt-5, bead_storage.bottom(1), rate=0.5)
            bead_amt -= 25
            left_pipette.aspirate(25, bead_storage.bottom(0.5))
            left_pipette.dispense(25, reagent_plate.wells()[i].bottom(2))
            left_pipette.blow_out(reagent_plate.wells()[i].top())
            left_pipette.touch_tip()
            remove_tip(left_pipette, protocol.params.dry_run)
        
    protocol.comment("\nPlacing tube on magnetic separator and allowing 10s for microparticles to clear")
    # protocol.move_labware(reagent_plate, magnetic_block, use_gripper=True)
    protocol.delay(seconds=bead_settle_time+5, msg="waiting 7 seconds for microparticles to clear")
    aspirate_spuernatent_to_trash(right_pipette, 25, 0.6)
    

    protocol.comment("\nWashing and equilibrating the microparticles in "+str(wash_volume) + "µl Equilibration Buffer (2 times)")
    for wash_num in range (0,num_washes):     # all washes before the last wash with EQ buffer
        protocol.comment("Wash number: "+  str(wash_num+1))
        hs_mod.open_labware_latch()
        protocol.move_labware(reagent_plate, new_location=hs_mod, use_gripper=True)
        hs_mod.close_labware_latch()

        for i in range (0, math.ceil(num_samples/8)):
            # right_pipette.pick_up_tip()
            pick_up(right_pipette)
            equilibartion_buffer_amt -= wash_volume/1000 * 8#0.18*8
            # wet_tip(right_pipette, equilibration_buffer_storage[math.ceil(equilibartion_buffer_amt/11)-1].bottom(1))
            right_pipette.aspirate(wash_volume, equilibration_buffer_storage[math.ceil(equilibartion_buffer_amt/11)-1].bottom(1),0.4)
            right_pipette.dispense(wash_volume, reagent_plate['A' + str(i+1)].bottom(2),0.3)
            # right_pipette.mix(8, wash_volume, reagent_plate['A' + str(i+1)].bottom(2),0.3)
            mix_sides(right_pipette, 1, wash_volume, reagent_plate['A' + str(i+1)], 0.5)
            
            right_pipette.blow_out(reagent_plate['A' + str(i+1)].top())
            right_pipette.touch_tip()
            remove_tip(right_pipette, protocol.params.dry_run)

        protocol.comment("Gentil agitation for 1 minute ("+str(shake_speed)+"rpm)")
        # hs_mod.open_labware_latch()
        # protocol.move_labware(reagent_plate, hs_mod, use_gripper=True)
        # hs_mod.close_labware_latch()
        hs_mod.set_and_wait_for_shake_speed(shake_speed)       #1000 rpm
        protocol.delay(seconds=60 if protocol.params.dry_run else 60, msg="1 minute incubation (10 seconds for dry run)")
        hs_mod.deactivate_shaker()
        hs_mod.open_labware_latch()
        protocol.move_labware(reagent_plate, magnetic_block, use_gripper=True)
        # aspirate_spuernatent_to_trash(right_pipette, wash_volume, 0.1)

        if wash_num == 0:   # first wash
            protocol.delay(seconds=bead_settle_time+5, msg="waiting for beads to settle (20 sec)")
            aspirate_spuernatent_to_trash(right_pipette, wash_volume-10, 0.25)       # leave the last 5ul in the well plate
        elif wash_num != num_washes-1:      # Not on the last wash yet
            protocol.delay(seconds=bead_settle_time+5, msg="waiting for beads to settle (20 sec)")
            aspirate_spuernatent_to_trash(right_pipette, wash_volume, 0.25)       # leave the last 5ul in the well plate
        # protocol.move_labware(reagent_plate, new_location="B2", use_gripper=True)

    # protocol.move_labware(reagent_plate, new_location="B2", use_gripper=True)

    protocol.comment("\n\n---------------Protein Binding Procedure------------------\n\n\n\n")
    protocol.comment("\nAdding "+str(protein_sample_amt)+"µl binding buffer to "+str(protein_sample_amt)+"µl protein sample")
    for i in range (0, math.ceil(num_samples/8)):
        # right_pipette.pick_up_tip()
        pick_up(right_pipette)
        binding_buffer_amt -= (protein_sample_amt/1000)*8
        right_pipette.aspirate(protein_sample_amt, binding_buffer_storage[math.ceil(binding_buffer_amt/11)-1].bottom(1), 0.4)
        right_pipette.dispense(protein_sample_amt, sample_plate['A' + str(i+1)].bottom(1),0.5)
        right_pipette.mix(4, protein_sample_amt-15,sample_plate['A' + str(i+1)].bottom(1),rate=0.1)
        remove_tip(right_pipette, protocol.params.dry_run)
    
    aspirate_spuernatent_to_trash(right_pipette, wash_volume+15, 0.5)

    hs_mod.open_labware_latch()
    protocol.move_labware(reagent_plate, hs_mod, use_gripper=True)
    hs_mod.close_labware_latch()
    
    protocol.comment("\nAdding binding buffer and protein sample to well plate")
    for i in range (0, math.ceil(num_samples/8)):
        # right_pipette.pick_up_tip()
        pick_up(right_pipette)
        right_pipette.aspirate(50, sample_plate['A' + str(i+1)].bottom(0.5), rate=0.1)
        right_pipette.dispense(50, reagent_plate['A' + str(i+1)].bottom(1), rate=0.1)
        mix_sides(right_pipette, 2, 30, reagent_plate['A' + str(i+1)], 0.4)
        # right_pipette.mix(3, 30, reagent_plate['A' + str(i+1)].bottom(0.5), rate=0.1)
        right_pipette.blow_out(reagent_plate['A' + str(i+1)].top())
        right_pipette.touch_tip()
        remove_tip(right_pipette, protocol.params.dry_run)

    protocol.comment("\nAllow proteins to bind to microparticles for 30 min. Mix gently and continuously")
    # protocol.pause('''"Put the lid on!!!" -O____________O''')
    hs_mod.set_and_wait_for_shake_speed(1550)       #1100 rpm
    # Setting up digestion buffer       FIX THIS SECTION
    protocol.comment("\nSetting up the digestion buffer")
    digestion_buffer_in_well_amt = digestion_buffer_per_sample_amt + 5
    for i in range (0, math.ceil((num_samples*digestion_buffer_in_well_amt)/1000)):
        # left_pipette.pick_up_tip()
        pick_up(left_pipette)
        digestion_buffer_stock_amt -= digestion_buffer_per_sample_amt+5
        left_pipette.aspirate(digestion_buffer_per_sample_amt+5, digestion_buffer_storage.bottom(get_height_smalltube(digestion_buffer_stock_amt)), rate=0.2)
        left_pipette.dispense(digestion_buffer_per_sample_amt+5, digestion_buffer_plate.wells()[i].bottom(1), rate=0.2)
        left_pipette.blow_out(reagent_plate.wells()[i].top())
        remove_tip(left_pipette, protocol.params.dry_run)

    # protocol.pause('''"Tell me when to stop!! (30 min incubation time)''')
    protocol.delay(seconds=10 if protocol.params.dry_run else 1800, msg="30 minute incubation (10 seconds for dry run)")
    hs_mod.deactivate_shaker()
    hs_mod.open_labware_latch()
    protocol.move_labware(reagent_plate, magnetic_block, use_gripper=True)
    protocol.delay(seconds=bead_settle_time, msg="waiting for beads to settle (20 sec)")
    aspirate_spuernatent_to_trash(right_pipette, wash_volume, 0.05)

    protocol.comment("\nResuspend beads in " + str(wash_volume) + "µl wash buffer and mix thoroughly for 1 minute. times: " + str(num_washes))     # TO-DO: PUT THIS INTO A FRICKEN FUNCTION!
    # protocol.move_labware(reagent_plate, new_location="B2", use_gripper=True)
    wash_buffer_resuspend_amt = wash_volume
    for i in range (0,num_washes):
        protocol.comment("Resuspend number: "+  str(i+1))
        hs_mod.open_labware_latch()
        protocol.move_labware(reagent_plate, new_location=hs_mod, use_gripper=True)
        hs_mod.close_labware_latch()
        for i in range (0, math.ceil(num_samples/8)):
            # right_pipette.pick_up_tip()
            pick_up(right_pipette)
            wash_buffer_amt -= wash_buffer_resuspend_amt/1000*8
            # wet_tip(right_pipette,wash_buffer_storage[math.ceil(wash_buffer_amt/11)-1].bottom(2))
            right_pipette.aspirate(wash_buffer_resuspend_amt, wash_buffer_storage[math.ceil(wash_buffer_amt/11)-1].bottom(2), 0.4)

            right_pipette.dispense(wash_buffer_resuspend_amt, reagent_plate['A' + str(i+1)].bottom(2), rate= 0.5)
            
            mix_sides(right_pipette,4, wash_buffer_resuspend_amt,reagent_plate['A' + str(i+1)], 1)
            # right_pipette.mix(4, wash_buffer_resuspend_amt-10, reagent_plate['A' + str(i+1)].bottom(2),rate= 3)
            right_pipette.blow_out(reagent_plate['A' + str(i+1)].top())
            right_pipette.touch_tip()
            remove_tip(right_pipette, protocol.params.dry_run)

        protocol.comment("Gentil agitation for 1 minute ("+str(shake_speed)+"rpm)")
        # hs_mod.open_labware_latch()
        # protocol.move_labware(reagent_plate, hs_mod, use_gripper=True)
        # hs_mod.close_labware_latch()
        hs_mod.set_and_wait_for_shake_speed(shake_speed)       #1300 rpm
        protocol.delay(seconds=60 if protocol.params.dry_run else 60, msg="1 minute incubation (10 seconds for dry run)")
        hs_mod.deactivate_shaker()
        hs_mod.open_labware_latch()
        protocol.move_labware(reagent_plate, magnetic_block, use_gripper=True)
        protocol.delay(seconds=bead_settle_time, msg="waiting for beads to settle (20 sec)")
        if i == num_washes-1:       # last wash
            aspirate_spuernatent_to_trash(right_pipette, wash_buffer_resuspend_amt+20, 0.1)
        if i == 0:      # first wash
            aspirate_spuernatent_to_trash(right_pipette, wash_buffer_resuspend_amt-10, 0.1)
        else:
            aspirate_spuernatent_to_trash(right_pipette, wash_buffer_resuspend_amt, 0.1)
    hs_mod.open_labware_latch()
    protocol.move_labware(reagent_plate, new_location=hs_mod, use_gripper=True)
    hs_mod.close_labware_latch()

    protocol.comment("\n\n--------------------Protein Digestion Procedure-----------------------")
    protocol.comment("Resuspending microparticles with absorbed protein mix in 100-200µl digestion buffer")
    for i in range (0, math.ceil(num_samples/8)):
        pick_up(right_pipette)
        right_pipette.aspirate(digestion_buffer_per_sample_amt, digestion_buffer_plate['A' + str(i+1)].bottom(0.5), rate=0.1)
        right_pipette.dispense(digestion_buffer_per_sample_amt, reagent_plate['A' + str(i+1)].bottom(1), rate=0.1)
        right_pipette.mix(3, digestion_buffer_per_sample_amt-10, rate=0.25)
        mix_sides(right_pipette, 1, digestion_buffer_per_sample_amt-15, reagent_plate.wells()[i],0.75)
        right_pipette.blow_out(reagent_plate['A' + str(i+1)].top(2))
        right_pipette.blow_out(reagent_plate['A' + str(i+1)].top())
        right_pipette.touch_tip()
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
    # protocol.delay(seconds=bead_settle_time, msg="waiting for beads to settle (20 sec)")
    for i in range (0, num_samples):
        # left_pipette.pick_up_tip()
        pick_up(left_pipette)
        left_pipette.aspirate(digestion_buffer_per_sample_amt+10, reagent_plate.wells()[i].bottom(0.15), 0.2)
        left_pipette.dispense(digestion_buffer_per_sample_amt+10, final_tube_rack.wells()[i].bottom(0.25), 0.2)
        left_pipette.blow_out(final_tube_rack.wells()[i].bottom(10))
        left_pipette.touch_tip()
        # left_pipette.return_tip()
        remove_tip(left_pipette, protocol.params.dry_run)