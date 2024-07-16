from opentrons import protocol_api
import math

metadata = {
    "protocolName": "SP3 sample prep",
    "author": "Nico To",
    "description": "hello world",
}

requirements = {"robotType": "Flex", "apiLevel": "2.19"}

num_samples = 5

# amount of the bead solution in micro liters
bead_amt = (num_samples +2) *20         #20µl per sample
protein_sample_amt = (num_samples + 2)*30
anhy_etho_amt = (num_samples + 2)*50    #50µl per sample
aque_etho_amt = (num_samples + 2)*(180*3)    #180µl x 3 rinses per sample
trypsin_amt = 0.4 * (num_samples + 2)       #CHANGE LATER
ammonium_bicarbonate_amt = (num_samples + 2) * 100

def run(protocol: protocol_api.ProtocolContext):
    #loading
    tips1000 = [protocol.load_labware("opentrons_flex_96_filtertiprack_1000uL", slot) for slot in ["A3","B3","C3"]]
    chute = protocol.load_waste_chute()
    left_pipette = protocol.load_instrument("flex_1channel_1000", "left", tip_racks=tips1000)
    right_pipette = protocol.load_instrument("flex_8channel_1000", "right", tip_racks=tips1000)
    magnetic_block = protocol.load_module(module_name="magneticBlockV1", location="C1")
    mag_plate = magnetic_block.load_labware(name="biorad_96_wellplate_200ul_pcr")   # Load a 96-well plate on the magnetic block
    hs_mod = protocol.load_module(module_name="heaterShakerModuleV1", location="D1")    #heat shaker module
    tube_rack = protocol.load_labware("opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap", "A2", "stock rack")
    reagent_plate = protocol.load_labware("opentrons_96_wellplate_200ul_pcr_full_skirt", "B2", "reagent plate")
    working_reagent_reservoir = protocol.load_labware("nest_12_reservoir_15ml", "B1")

    #defining liquids
    bead_sol = protocol.define_liquid("Bead Solution", "Premade bead solution 1 µl of 50 µl/ul for both type of beads supsended in 10x origial volume of pure water", "#000000")
    anhy_etho = protocol.define_liquid("Anhydrous Ethanol", "Anhydrous Ethanol used to disperse the sample and magnetic particles", "#ffffff")
    aque_etho = protocol.define_liquid("80%% aqueous Ethanol", "80%% aqueous Ethanol used to wash and clean the magnetic particles and sample", "#8a8a8a")
    trypsin = protocol.define_liquid("Trypsin", "Trypsin, used to digest proteins and prep them for MS analysis", "#00ff44")
    ammonium_bicarbonate = protocol.define_liquid("100mM Ammonium Bicarbonate", "100mM Ammonium Bicarbonate (pH 8-8.5), buffer during protein digestion process", "#fa05cd")
    protein_sample = protocol.define_liquid("Protein Sample", "Reduced, alkylated protein sample", "#03fcf8")   #sample
    
    #loading liquids
    tube_rack["A1"].load_liquid(bead_sol, bead_amt)
    bead_storage = tube_rack["A1"]
    tube_rack["A2"].load_liquid(protein_sample, bead_amt)   #reagents
    sample_storage = tube_rack["A2"]    # storage of protein sample
    working_reagent_reservoir["A1"].load_liquid(anhy_etho, anhy_etho_amt)
    anhy_etho_storage = working_reagent_reservoir["A1"]
    working_reagent_reservoir["A2"].load_liquid(aque_etho, aque_etho_amt)
    aque_etho_storage = working_reagent_reservoir["A2"]
    working_reagent_reservoir["A3"].load_liquid(trypsin, trypsin_amt)
    trypsin_storage = working_reagent_reservoir["A3"]
    working_reagent_reservoir["A4"].load_liquid(ammonium_bicarbonate, ammonium_bicarbonate_amt)
    ammonium_bicarbonate_storage = working_reagent_reservoir["A4"]
    protocol.comment("--------Loading Sample---------")
    # setup protein sample
    for i in range (0, num_samples):
        left_pipette.pick_up_tip()
        left_pipette.aspirate(30, sample_storage)
        left_pipette.dispense(30, working_reagent_reservoir.wells()[i])
        left_pipette.touch_tip()
        left_pipette.drop_tip(chute)
    # setup bead sample
    protocol.comment("--------Loading beads---------")
    for i in range (0, num_samples):
        left_pipette.pick_up_tip()
        left_pipette.aspirate(20, bead_storage)
        left_pipette.dispense(20, working_reagent_reservoir.wells()[i])
        left_pipette.touch_tip()
        left_pipette.drop_tip(chute)
    protocol.comment("--------Loading Anhydrous Ethanol---------")
    for i in range (0, math.floor(num_samples/8)):
        right_pipette.pick_up_tip()
        right_pipette.aspirate(50, anhy_etho_storage)
        right_pipette.dispense(50, working_reagent_reservoir.rows()[i])
        right_pipette.mix(5, 40, working_reagent_reservoir.rows()[i])
        
        right_pipette.drop_tip(chute)
    # for i in range (0, num_samples%8):
    #     left_pipette.pick_up_tip()
    #     left_pipette.aspirate(50, anhy_etho_storage)
    #     left_pipette.dispense
