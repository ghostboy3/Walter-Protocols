from opentrons import protocol_api
import math


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
        default=1,
        minimum=1,
        maximum=30,
        unit="samples"
    )
    parameters.add_bool(
        variable_name="dry_run",
        display_name="Dry Run",
        description="Skip incubation delays and return tips.",
        default=True
    )

def get_height_smalltube(volume):
    '''
    Volume: amount of liquid in 1.5ml tube in µL
    Returns height in mm from the bottom of tube that pipette should go to
    '''  
    # volume = volume/1000
    if volume <= 500:     # cone part aaa
        volume = volume/1000
        return -26.8*(volume**2)+45.1*volume+3.98-5 #−26.80x2 +45.10x+3.98

    elif volume > 500:
        return 0.015*volume+11.5-4

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


def run(protocol: protocol_api.ProtocolContext):
    #defining variables
    num_samples = protocol.params.numSamples
    
    bead_amt = (num_samples + 1)*25     #µl
    protein_sample_amt = 25     # amount of protein per sample (µl)
    equilibartion_buffer_amt = 14       #ml
    binding_buffer_amt = 14       #ml
    wash_buffer_amt = 14       #ml
    digestion_buffer_stock_amt = 1000    #µl
    digestion_buffer_per_sample_amt = 150       #100-150µl
    
    #loading
    tips1000 = [protocol.load_labware("opentrons_flex_96_filtertiprack_1000uL", slot) for slot in ["A3","B3","C3"]]
    chute = protocol.load_waste_chute()
    left_pipette = protocol.load_instrument("flex_1channel_1000", "left", tip_racks=tips1000)
    right_pipette = protocol.load_instrument("flex_8channel_1000", "right", tip_racks=tips1000)
    magnetic_block = protocol.load_module(module_name="magneticBlockV1", location="C1")
    hs_mod = protocol.load_module(module_name="heaterShakerModuleV1", location="D1")    #heat shaker module
    tube_rack = protocol.load_labware("opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap", "A2", "stock and final solution rack")
    sample_tube_rack = protocol.load_labware("opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap", "A1", "sample stock rack")
    reagent_plate = protocol.load_labware("opentrons_96_wellplate_200ul_pcr_full_skirt", "B2", "reagent plate")
    buffer_rack = protocol.load_labware("opentrons_10_tuberack_falcon_4x50ml_6x15ml_conical", "B1", "reagent stock rack")   # equilibration, binding, and wash buffer
    working_reagent_reservoir = protocol.load_labware("nest_12_reservoir_15ml", "C2")


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
    
    buffer_rack["A1"].load_liquid(equilibration_buffer, equilibartion_buffer_amt)
    equilibration_buffer_storage = buffer_rack["A1"]
    buffer_rack["A2"].load_liquid(binding_buffer, binding_buffer_amt)
    binding_buffer_storage = buffer_rack["A2"]
    buffer_rack["B1"].load_liquid(wash_buffer, wash_buffer_amt)
    wash_buffer_storage = buffer_rack["B1"]
    
    # tube_rack["B2"].load_liquid()
    trash1=working_reagent_reservoir["A11"]

    
    #Functions
    def remove_tip(pipette, is_dry_run):
        if is_dry_run:
            pipette.return_tip()
        else:
            pipette.drop_tip(chute)         
    def aspirate_spuernatent_to_trash(pipette, amt):
        '''amt: amount ot aspirirate out'''
        protocol.comment("\nAspriating supernatant to trash")
        for i in range (0, math.ceil(num_samples/8)):
            pipette.pick_up_tip()
            pipette.aspirate(amt, reagent_plate['A' + str(i+1)].bottom(0.2), 0.9)
            pipette.dispense(amt, trash1,5)
            remove_tip(pipette, protocol.params.dry_run)
    
    protocol.comment("-------------Equilibration ---------------")
    protocol.comment("Vortex Mixing for 3 seconds")
    left_pipette.pick_up_tip()
    left_pipette.mix(10, bead_amt-5, bead_storage.bottom(1), 1.5)
    
    protocol.comment("\nTransfering 25µl HILIC beads into well plate")
    for i in range (0, num_samples):
        if left_pipette.has_tip == False:
            left_pipette.pick_up_tip()
        if  (i +1)%6 == 0: # mix every 6 samples
            left_pipette.mix(5, bead_amt-5, bead_storage.bottom(1), 1.5)
        bead_amt -= 25
        left_pipette.aspirate(25, bead_storage.bottom(get_height_smalltube(bead_amt)))
        left_pipette.dispense(25, reagent_plate.wells()[i].bottom(2))
        left_pipette.blow_out(reagent_plate.wells()[i].top())
        left_pipette.touch_tip()
        remove_tip(left_pipette, protocol.params.dry_run)
        
    protocol.comment("\nPlacing tube on magnetic separator and allowing 10s for microparticles to clear")
    protocol.move_labware(reagent_plate, magnetic_block, use_gripper=True)
    protocol.delay(seconds=10, msg="waiting 10 seconds for microparticles to clear")
    aspirate_spuernatent_to_trash(right_pipette, 50)
    
    protocol.comment("\nWashing and equilibrating the microparticles in 180µl Equilibration Buffer (2 times)")
    for i in range (0,2):    
        protocol.comment("Wash number: "+  str(i+1))
        protocol.move_labware(reagent_plate, new_location="B2", use_gripper=True)
        for i in range (0, num_samples):
            left_pipette.pick_up_tip()
            equilibartion_buffer_amt -= 0.18
            left_pipette.aspirate(180, equilibration_buffer_storage.bottom(get_height_falcon(equilibartion_buffer_amt)))
            left_pipette.dispense(180, reagent_plate.wells()[i].bottom(2))
            left_pipette.mix(4, 160, reagent_plate.wells()[i].bottom(2))
            left_pipette.blow_out(reagent_plate.wells()[i].top())
            left_pipette.touch_tip()
            remove_tip(left_pipette, protocol.params.dry_run)

        protocol.comment("Gentil agitation for 1 minute (1000rpm)")
        hs_mod.open_labware_latch()
        protocol.move_labware(reagent_plate, hs_mod, use_gripper=True)
        hs_mod.close_labware_latch()
        hs_mod.set_and_wait_for_shake_speed(1000)       #1000 rpm
        protocol.delay(seconds=10 if protocol.params.dry_run else 60, msg="1 minute incubation (10 seconds for dry run)")
        hs_mod.deactivate_shaker()
        hs_mod.open_labware_latch()
        protocol.move_labware(reagent_plate, magnetic_block, use_gripper=True)
        protocol.delay(seconds=20, msg="waiting for beads to settle (20 sec)")
        aspirate_spuernatent_to_trash(right_pipette, 220)
    protocol.move_labware(reagent_plate, new_location="B2", use_gripper=True)
    
    protocol.comment("\n\n---------------Protein Binding Procedure------------------")
    protocol.comment("\nAdding 25µl sample and 25µl binding buffer to beads")
    for i in range (0, num_samples):
        left_pipette.pick_up_tip()
        left_pipette.aspirate(protein_sample_amt, sample_tube_rack.wells()[i].bottom(get_height_smalltube(25)))
        left_pipette.dispense(protein_sample_amt, reagent_plate.wells()[i].bottom(2))
        left_pipette.blow_out(reagent_plate.wells()[i].top())
        left_pipette.touch_tip()
        remove_tip(left_pipette, protocol.params.dry_run)
        
        left_pipette.pick_up_tip()
        binding_buffer_amt -= 0.025
        left_pipette.aspirate(25, binding_buffer_storage.bottom(get_height_falcon(binding_buffer_amt)))
        left_pipette.dispense(25, reagent_plate.wells()[i].bottom(2))
        left_pipette.mix(7, 40, reagent_plate.wells()[i], 1.5)
        left_pipette.blow_out(reagent_plate.wells()[i].top())
        left_pipette.touch_tip()
        remove_tip(left_pipette, protocol.params.dry_run)
    
    protocol.comment("\nAllow proteins to bind to microparticles for 30 min. Mix gently and continuously")
    hs_mod.open_labware_latch()
    protocol.move_labware(reagent_plate, hs_mod, use_gripper=True)
    hs_mod.close_labware_latch()
    protocol.pause('''"Put the lid on!!!" -O____________O''')
    hs_mod.set_and_wait_for_shake_speed(1100)       #1100 rpm
    protocol.delay(seconds=10 if protocol.params.dry_run else 1800, msg="30 minute incubation (10 seconds for dry run)")
    hs_mod.deactivate_shaker()
    hs_mod.open_labware_latch()
    protocol.move_labware(reagent_plate, magnetic_block, use_gripper=True)
    protocol.delay(seconds=20, msg="waiting for beads to settle (20 sec)")
    aspirate_spuernatent_to_trash(right_pipette, 220)
    
    protocol.comment("\nResuspend beads in 180µl wash buffer and mix thoroughly for 1 minute (x2)")     # TO-DO: PUT THIS INTO A FRICKEN FUNCTION!
    # protocol.move_labware(reagent_plate, new_location="B2", use_gripper=True)
    for i in range (0,2):    
        protocol.comment("Resuspend number: "+  str(i+1))
        protocol.move_labware(reagent_plate, new_location="B2", use_gripper=True)
        for i in range (0, num_samples):
            left_pipette.pick_up_tip()
            wash_buffer_amt -= 0.18
            left_pipette.aspirate(180, wash_buffer_storage.bottom(get_height_falcon(wash_buffer_amt)))
            left_pipette.dispense(180, reagent_plate.wells()[i].bottom(2))
            left_pipette.mix(4, 160, reagent_plate.wells()[i].bottom(2), 10)

            left_pipette.blow_out(reagent_plate.wells()[i].top())
            left_pipette.touch_tip()
            remove_tip(left_pipette, protocol.params.dry_run)

        protocol.comment("Gentil agitation for 1 minute (1000rpm)")
        hs_mod.open_labware_latch()
        protocol.move_labware(reagent_plate, hs_mod, use_gripper=True)
        hs_mod.close_labware_latch()
        hs_mod.set_and_wait_for_shake_speed(1000)       #1000 rpm
        protocol.delay(seconds=10 if protocol.params.dry_run else 60, msg="1 minute incubation (10 seconds for dry run)")
        hs_mod.deactivate_shaker()
        hs_mod.open_labware_latch()
        protocol.move_labware(reagent_plate, magnetic_block, use_gripper=True)
        protocol.delay(seconds=20, msg="waiting for beads to settle (20 sec)")
        aspirate_spuernatent_to_trash(right_pipette, 220)
    protocol.move_labware(reagent_plate, new_location="B2", use_gripper=True)

    protocol.comment("\n\n--------------------Protein Digestion Procedure-----------------------")
    protocol.comment("Resuspending microparticles with absorbed protein mix in 100-200µl digestion buffer")
    for i in range (0, num_samples):
        left_pipette.pick_up_tip()
        digestion_buffer_stock_amt -= digestion_buffer_per_sample_amt
        left_pipette.aspirate(digestion_buffer_per_sample_amt, digestion_buffer_storage.bottom(get_height_smalltube(digestion_buffer_stock_amt)))
        left_pipette.dispense(digestion_buffer_per_sample_amt, reagent_plate.wells()[i].bottom(2), 10)
        left_pipette.blow_out(reagent_plate.wells()[i].top())
        left_pipette.touch_tip()
        remove_tip(left_pipette, protocol.params.dry_run)
    protocol.comment("\nIncubating sample at 37°C for 4 hours. Mix continuously at 1000 rpm")
    hs_mod.open_labware_latch()
    protocol.move_labware(reagent_plate, hs_mod, use_gripper=True)
    hs_mod.close_labware_latch()
    protocol.pause('''"Put the lid on!!!" -O____________O''')
    hs_mod.set_and_wait_for_shake_speed(1000)       #1000 rpm
    hs_mod.set_and_wait_for_temperature(37)         #37°C
    protocol.delay(minutes=1/6 if protocol.params.dry_run else 240, msg="4 hour incubation at 37°C (10 seconds for dry run)")
    hs_mod.deactivate_shaker()
    hs_mod.deactivate_heater()
    hs_mod.open_labware_latch()
    
    protocol.comment("\nRecovering the microparticles on magnetic separator and aspirating the supernatant containing peptides with a pipette")
    protocol.move_labware(reagent_plate, magnetic_block, use_gripper=True)
    protocol.delay(seconds=20, msg="waiting for beads to settle (20 sec)")
    counter=len(tube_rack.wells())-1
    for i in range (0, num_samples):
        left_pipette.pick_up_tip()
        left_pipette.aspirate(250, reagent_plate.wells()[i].bottom(0.25), 1.5)
        left_pipette.dispense(250, tube_rack.wells()[counter-i].bottom(0.5), 1.5)
        left_pipette.blow_out(tube_rack.wells()[counter-i].top())
        left_pipette.touch_tip()
        # left_pipette.return_tip()
        remove_tip(left_pipette, protocol.params.dry_run)
        # left_pipette.transfer(120, new_vessel.wells()[i].bottom(0.25), tube_rack.wells()[counter-1].bottom(0.5), blow_out=True,touch_tip=True,blowout_location="destination well", trash=False)
        # counter -= 1