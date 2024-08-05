from opentrons import protocol_api
import math


metadata = {
    "protocolName": "TESTING sp3 protocol3",
    "author": "Hugge Mann",
    "description": "Just playing around with some stuff",
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

    
slow_aspiration_rate = 10 # in microliters per second

def run(protocol: protocol_api.ProtocolContext):
    #defining variables
    num_samples = protocol.params.numSamples

    # amount of the bead solution in micro liters
    bead_amt = (num_samples +2) *20         #20µl per sample
    protein_sample_amt = (num_samples + 2)*30
    anhy_etho_amt = (num_samples + 2)*50    #50µl per sample
    aque_etho_amt = (num_samples + 7)*(180*3)    #180µl x 3 rinses per sample
    # trypsin_amt = 0.4 * (num_samples + 2)       #CHANGE LATER
    ammonium_bicarbonate_amt = (num_samples + 2) * 100
    
    
    #loading
    tips1000 = [protocol.load_labware("opentrons_flex_96_filtertiprack_1000uL", slot) for slot in ["A3","B3","C3"]]
    chute = protocol.load_waste_chute()
    left_pipette = protocol.load_instrument("flex_1channel_1000", "left", tip_racks=tips1000)
    right_pipette = protocol.load_instrument("flex_8channel_1000", "right", tip_racks=tips1000)
    magnetic_block = protocol.load_module(module_name="magneticBlockV1", location="C1")
    # mag_plate = magnetic_block.load_labware(name="biorad_96_wellplate_200ul_pcr")   # Load a 96-well plate on the magnetic block
    hs_mod = protocol.load_module(module_name="heaterShakerModuleV1", location="D1")    #heat shaker module
    tube_rack = protocol.load_labware("opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap", "A2", "stock rack")
    reagent_plate = protocol.load_labware("opentrons_96_wellplate_200ul_pcr_full_skirt", "B2", "reagent plate")
    new_vessel = protocol.load_labware("opentrons_96_wellplate_200ul_pcr_full_skirt", "C2", "reagent plate")
    working_reagent_reservoir = protocol.load_labware("nest_12_reservoir_15ml", "B1")

    #defining liquids
    bead_sol = protocol.define_liquid("Bead Solution", "Premade bead solution 1 µl of 50 µl/ul for both type of beads supsended in 10x origial volume of pure water", "#000000")
    anhy_etho = protocol.define_liquid("Anhydrous Ethanol", "Anhydrous Ethanol used to disperse the sample and magnetic particles", "#ffffff")
    aque_etho = protocol.define_liquid("80%% aqueous Ethanol", "80%% aqueous Ethanol used to wash and clean the magnetic particles and sample", "#8a8a8a")
    # trypsin = protocol.define_liquid("Trypsin", "Trypsin, used to digest proteins and prep them for MS analysis", "#00ff44")
    ammonium_bicarbonate = protocol.define_liquid("100mM Ammonium Bicarbonate", "100mM Ammonium Bicarbonate (pH 8-8.5), buffer during protein digestion process. TRYPSIN ALREADY ADDED IN.", "#fa05cd")
    protein_sample = protocol.define_liquid("Protein Sample", "Reduced, alkylated protein sample", "#03fcf8")   #sample
    
    #loading liquids
    tube_rack["A1"].load_liquid(bead_sol, bead_amt)
    bead_storage = tube_rack["A1"]
    tube_rack["B1"].load_liquid(protein_sample, bead_amt)   #reagents
    sample_storage = tube_rack["B1"]    # storage of protein sample
    tube_rack["C1"].load_liquid(ammonium_bicarbonate, ammonium_bicarbonate_amt)
    ammonium_bicarbonate_storage = tube_rack["C1"]
    working_reagent_reservoir["A1"].load_liquid(anhy_etho, anhy_etho_amt)
    anhy_etho_storage = working_reagent_reservoir["A1"]
    working_reagent_reservoir["A2"].load_liquid(aque_etho, aque_etho_amt)
    aque_etho_storage = working_reagent_reservoir["A2"]
    # working_reagent_reservoir["A3"].load_liquid(trypsin, trypsin_amt)
    # trypsin_storage = working_reagent_reservoir["A3"]
    # working_reagent_reservoir["A4"].load_liquid(ammonium_bicarbonate, ammonium_bicarbonate_amt)
    # ammonium_bicarbonate_storage = working_reagent_reservoir["A4"]
    #trash reservoirs
    trash1=working_reagent_reservoir["A11"]
    
    
    #setting defaults
    
    default_aspirating_rate = 300
    default_dispensing_rate = 500
    left_pipette.flow_rate.aspirate = default_aspirating_rate
    right_pipette.flow_rate.aspirate = default_aspirating_rate
    left_pipette.flow_rate.dispense = default_dispensing_rate
    right_pipette.flow_rate.dispense = default_dispensing_rate
    
    
    fast_aspirate_rate = 1000
    fast_dispense_rate = 1200
    # functions    
    def aspirate_spuernatent_to_trash(pipette, amt):
        '''amt: amount ot aspirirate out'''
        pipette.flow_rate.dispense = 500
        for i in range (0, math.ceil(num_samples/8)):
            pipette.pick_up_tip()
            pipette.aspirate(amt, reagent_plate['A' + str(i+1)].bottom(0.5))
            pipette.dispense(amt, trash1)
            remove_tip(pipette, protocol.params.dry_run)
            # pipette.return_tip()
        pipette.flow_rate.dispense = default_dispensing_rate
            # right_pipette.drop_tip(chute) 
    def remove_tip(pipette, is_dry_run):
        if is_dry_run:
            pipette.return_tip()
        else:
            pipette.drop_tip(chute)
    
    protocol.comment("--------Loading Sample---------")
    # setup protein sample
    for i in range (0, num_samples):
        left_pipette.pick_up_tip()
        left_pipette.aspirate(30, sample_storage.bottom(2))
        left_pipette.dispense(30,reagent_plate.wells()[i].bottom(2))
        left_pipette.blow_out(reagent_plate.wells()[i].top())
        left_pipette.touch_tip()
        remove_tip(left_pipette, protocol.params.dry_run)
        # left_pipette.return_tip()
        # left_pipette.transfer(30, sample_storage.bottom(2), reagent_plate.wells()[i].bottom(2), blow_out=True,touch_tip=True,blowout_location="destination well", trash=False)
    # setup bead sample
    protocol.comment("--------Loading beads---------")
    for i in range (0, num_samples):
        left_pipette.pick_up_tip()
        if i % 6 ==0:       # mix the beads every 6 samples
            left_pipette.mix(3, bead_amt-43, bead_storage.bottom(1))
            left_pipette.blow_out(bead_storage.top())
        left_pipette.aspirate(20, bead_storage.bottom(1))
        left_pipette.dispense(20, reagent_plate.wells()[i])
        left_pipette.blow_out(reagent_plate.wells()[i].top())
        left_pipette.touch_tip()
        remove_tip(left_pipette, protocol.params.dry_run)
        # left_pipette.return_tip()
        # left_pipette.transfer(20, bead_storage, reagent_plate.wells()[i],touch_tip=True, blow_out=True,blowout_location="destination well", trash=False)
    protocol.comment("--------Loading Anhydrous Ethanol---------")
    for i in range (0, math.ceil(num_samples/8)):
        right_pipette.pick_up_tip()
        right_pipette.aspirate(50, anhy_etho_storage.bottom(1))
        # print(working_reagent_reservoir.rows()[i])
        right_pipette.dispense(50, reagent_plate['A' + str(i+1)])
        right_pipette.mix(5, 40, reagent_plate['A' + str(i+1)].bottom(2))
        right_pipette.blow_out(reagent_plate['A' + str(i+1)].top())
        right_pipette.touch_tip()
        # right_pipette.drop_tip(chute)
        remove_tip(right_pipette, protocol.params.dry_run)

        # right_pipette.return_tip()
    # for count, i in enumerate("ABCDEFGH"):
    #     if count==(num_samples%8):
    #         break
    #     left_pipette.pick_up_tip()
    #     left_pipette.aspirate(50, anhy_etho_storage.bottom(1))
    #     left_pipette.dispense(50, reagent_plate[i+str(math.floor(num_samples/8)+1)])
    #     left_pipette.mix(5, 40, reagent_plate[i+str(math.floor(num_samples/8)+1)].bottom(2))
    #     left_pipette.blow_out(reagent_plate[i+str(math.floor(num_samples/8)+1)].top())
    #     left_pipette.touch_tip()
    #     # left_pipette.drop_tip(chute)
    #     left_pipette.return_tip()
    protocol.comment("--------THERMOMIXER 1000rpm for 5 min---------")
    hs_mod.open_labware_latch()
    protocol.move_labware(reagent_plate, hs_mod, use_gripper=True)
    hs_mod.close_labware_latch()
    hs_mod.set_and_wait_for_shake_speed(1000)       #1000 rpm
    protocol.delay(seconds=5, msg="5 minute incubation")
    # deactivating heat shaker
    hs_mod.deactivate_shaker()
    hs_mod.open_labware_latch()
    protocol.move_labware(reagent_plate, magnetic_block, use_gripper=True)
    # hs_mod.close_labware_latch()
    protocol.comment("--------ASPIRATING SPUERNATANT ON MAGNETIC RACK---------")        # lid not closed, room temperature

    # Aspirating - play around with how deep the tip has to go
    # washing could be done outside of walt
    protocol.delay(seconds=20)
    aspirate_spuernatent_to_trash(right_pipette, 250)
    # for i in range (0, math.ceil(num_samples/8)):
    #     right_pipette.pick_up_tip()
    #     right_pipette.aspirate(50, reagent_plate['A' + str(i+1)])
    #     right_pipette.dispense(50, trash1)
    #     right_pipette.drop_tip(chute)

    protocol.comment("---------ETHANOL RINSING (x4)-----------")
    for i in range (0,4):       # temperarily changed to 1
        protocol.move_labware(reagent_plate, new_location="B2", use_gripper=True)
        for i in range (0, math.ceil(num_samples/8)):
            right_pipette.pick_up_tip()
            right_pipette.aspirate(150, aque_etho_storage.bottom(1))
            right_pipette.flow_rate.aspirate = fast_aspirate_rate
            right_pipette.flow_rate.dispense = fast_dispense_rate
            right_pipette.dispense(150, reagent_plate['A' + str(i+1)])
            
            right_pipette.mix(10, 190, reagent_plate['A' + str(i+1)].bottom(3))
            right_pipette.flow_rate.aspirate = default_aspirating_rate
            right_pipette.flow_rate.dispense = default_dispensing_rate
            right_pipette.mix(2, 150, reagent_plate['A' + str(i+1)].bottom(3))

            right_pipette.blow_out(reagent_plate['A' + str(i+1)].top())
            right_pipette.touch_tip()
            # right_pipette.drop_tip(chute)
            # right_pipette.return_tip()
            remove_tip(right_pipette, protocol.params.dry_run)
            right_pipette.flow_rate.aspirate = default_aspirating_rate
            right_pipette.flow_rate.dispense = default_dispensing_rate
        protocol.move_labware(reagent_plate, magnetic_block, use_gripper=True)  #put back on magnetic rack
        protocol.delay(seconds=17)
        #aspirate the supernatant
        aspirate_spuernatent_to_trash(right_pipette, 250)
    protocol.comment("---------ADDING DIGESTION BUFFER-----------")
    protocol.move_labware(reagent_plate, new_location="B2", use_gripper=True)
    for i in range (0, num_samples):
        #change speed later (make it slower)
        left_pipette.transfer(100, ammonium_bicarbonate_storage.bottom(1), reagent_plate.wells()[i].bottom(3),touch_tip=True, blow_out=False, trash=False)
    protocol.comment("---------INCUBATING  AT 37°C, 1500RPM, OVERNIGHT-----------")
    hs_mod.open_labware_latch()
    protocol.move_labware(reagent_plate, hs_mod, use_gripper=True)
    hs_mod.close_labware_latch()
    #Wait for user to put lid on
    protocol.pause("Put the lid on!!!")
    hs_mod.set_and_wait_for_shake_speed(1500)       #1500 rpm
    hs_mod.set_and_wait_for_temperature(37)       #37 deg C
    # protocol.delay(seconds=5, msg="5 second incubation")
    protocol.pause("Press stop when done!!! (～￣▽￣)～")
    hs_mod.deactivate_shaker()
    hs_mod.deactivate_heater()
    hs_mod.open_labware_latch()

    protocol.comment("---------COLLECTING SUPERNATANT-----------")
    protocol.move_labware(reagent_plate, magnetic_block, use_gripper=True)
    protocol.delay(seconds=30, msg="pausing for 30 sec")
    for i in range (0, math.ceil(num_samples/8)):
        #change blowout
        right_pipette.pick_up_tip()
        right_pipette.aspirate(120, reagent_plate['A' + str(i+1)].bottom(0.25))
        right_pipette.dispense(120, new_vessel['A' + str(i+1)].bottom(0.5))
        right_pipette.blow_out(new_vessel['A' + str(i+1)].top())
        right_pipette.touch_tip()
        remove_tip(right_pipette, protocol.params.dry_run)

        # right_pipette.return_tip()
        # right_pipette.transfer(120, reagent_plate['A' + str(i+1)].bottom(0.5), new_vessel['A' + str(i+1)].bottom(0.5), blow_out=True, touch_tip=True, blowout_location="destination well", trash=False)
    protocol.move_labware(reagent_plate, new_location="B2", use_gripper=True)
    protocol.move_labware(new_vessel, magnetic_block, use_gripper=True)
    
    protocol.delay(seconds=10, msg="SITTING ON MAGNETIC RACK FOR 3 MIN")
    
    protocol.comment("---------MOVING SAMPLE TO FINAL VESSEL-----------")
    counter=len(tube_rack.wells())
    for i in range (0, num_samples):
        left_pipette.pick_up_tip()
        left_pipette.aspirate(120, new_vessel.wells()[i].bottom(0.25))
        left_pipette.dispense(120, tube_rack.wells()[counter-1].bottom(0.5))
        left_pipette.blow_out(tube_rack.wells()[counter-1].top())
        left_pipette.touch_tip()
        # left_pipette.return_tip()
        remove_tip(left_pipette, protocol.params.dry_run)
        # left_pipette.transfer(120, new_vessel.wells()[i].bottom(0.25), tube_rack.wells()[counter-1].bottom(0.5), blow_out=True,touch_tip=True,blowout_location="destination well", trash=False)
        counter -= 1

    