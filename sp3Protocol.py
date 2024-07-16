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
bead_amt = (num_samples +2) *20


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

    #defining liquids
    bead_sol = protocol.define_liquid("Bead Solution", "Premade bead solution 1 µl of 50 µl/ul for both type of beads supsended in 10x origial volume of pure water", "#000000")
    anhy_etho = protocol.define_liquid("Anhydrous Ethanol", "Anhydrous Ethanol used to disperse the sample and magnetic particles", "#ffffff")
    aque_etho = protocol.define_liquid("80%% aqueous Ethanol", "80%% aqueous Ethanol used to wash and clean the magnetic particles and sample", "#8a8a8a")
    trypsin = protocol.define_liquid("Trypsin", "Trypsin, used to digest proteins and prep them for MS analysis", "#00ff44")
    ammonium_bicarbonate = protocol.define_liquid("Ammonium Bicarbonate", "Ammonium Bicarbonate (pH 8-8.5), buffer during protein digestion process", "#fa05cd")
    
    # left_pipette.pick_up_tip()
