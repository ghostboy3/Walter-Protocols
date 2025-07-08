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
        default=400,
        minimum=100,
        maximum=1000,
        unit="mM"
    )
    #Default true
    parameters.add_bool(
        variable_name="create_buffers",
        display_name="Create buffers with Walt",
        description="Use walt to create/mix binding, wash, and equilibration buffers",
        default=True
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
    ammonium_acetate = (total_buffer_amt)*(100/ammonium_acetate_concentration)
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
    ammonium_acetate = (total_buffer_amt)*(200/ammonium_acetate_concentration)
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


aa_conc = 400
print("eq")
print(get_eq_buffer_vols(5000, aa_conc))
print("bb")
print(get_binding_buffer_vols(5000, aa_conc))
print("wb")
print(get_wash_buffer_vols(5000))
# def run(protocol: protocol_api.ProtocolContext):
#     #defining variables
#     wash_volume = 100#protocol.params.wash_volume   #µl
#     shake_speed = 1400#protocol.params.shake_speed   #rpm
#     num_washes = 2
#     num_samples = protocol.params.numSamples
#     bead_settle_time = 10 #seconds
    
#     bead_amt = 12.5#(num_samples)*25     #µl
#     protein_sample_amt = 60#protocol.params.protein_sample_amt     # amount of protein per sample (µl)
#     equilibartion_buffer_amt = (300*8*(math.ceil(num_samples/8)) + 1000)/1000       #ml
#     binding_buffer_amt = (40*8*(math.ceil(num_samples/8)) + 500)/1000       #ml
#     wash_buffer_amt = (300*8*(math.ceil(num_samples/8)) + 1000)/1000       #ml
#     digestion_buffer_per_sample_amt = 100#protocol.params.digestion_buffer_per_sample_amt       #100-150µl
    
#     #loading
#     tips1000 = [protocol.load_labware("opentrons_flex_96_filtertiprack_200uL", slot) for slot in ["A3","B3","C3"]]
#     chute = protocol.load_waste_chute()
#     left_pipette = protocol.load_instrument("flex_1channel_1000", "left", tip_racks=tips1000)
#     right_pipette = protocol.load_instrument("flex_8channel_1000", "right", tip_racks=tips1000)
#     magnetic_block = protocol.load_module(module_name="magneticBlockV1", location="C1")
#     hs_mod = protocol.load_module(module_name="heaterShakerModuleV1", location="D1")    #heat shaker module
#     tube_rack = protocol.load_labware("opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap", "A2", "bead + final solution rack")
#     sample_plate = protocol.load_labware("opentrons_96_wellplate_200ul_pcr_full_skirt", "A1", "sample stock plate")
#     reagent_plate = hs_mod.load_labware("opentrons_96_wellplate_200ul_pcr_full_skirt","reagent plate")
#     digestion_buffer_reservoir = protocol.load_labware("nest_96_wellplate_2ml_deep", location= "B2")        ## change deck location
#     # final_sample_plate = protocol.load_labware("opentrons_96_wellplate_200ul_pcr_full_skirt", "B1", "reagent plate")
#     # buffer_rack = protocol.load_labware("opentrons_10_tuberack_falcon_4x50ml_6x15ml_conical", "B1", "reagent stock rack")   # equilibration, binding, and wash buffer
#     working_reagent_reservoir = protocol.load_labware("nest_12_reservoir_15ml", "D2")
#     final_tube_rack = protocol.load_labware("opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap", "B1", "final solution rack")
#     # trash_reservoir = protocol.load_labware("nest_1_reservoir_195ml", "C2", "trash reservoir")
    
#     #defining liquids
#     bead_sol = protocol.define_liquid("HILIC Bead Solution", "An alloquat of the HILIC bead solution", "#000000")
#     equilibration_buffer = protocol.define_liquid("Equilibration Buffer", "100mM ammonium acetate, pH 4.5, 15%% acetonitrile", "#32a852")
#     binding_buffer = protocol.define_liquid("Binding Buffer", "200mM ammonium acetate, pH 4.5, 30%% acetonitrile", "#8d32a8")
#     wash_buffer = protocol.define_liquid("Wash Buffer", "95%% acetonitrile (5% water)", "#05a1f5")
#     digestion_buffer = protocol.define_liquid("Digestion Buffer", "95%% acetonitrile (5% water)", "#fafa02")          # CHANGE THIS AFTER ASKING LAURA
#     water = protocol.define_liquid("water", "water", "#00b7ff")
#     acetonitrile = protocol.define_liquid("acn", "acn", "#03fc31")
#     ammoniumAcetate = protocol.define_liquid("ammonium acetate", "ammonium acetate", "#fa05ee")
#     # Loading Liquids
#     tube_rack["A1"].load_liquid(bead_sol, bead_amt)
#     bead_storage = tube_rack["A1"]
#     # tube_rack["B1"].load_liquid(digestion_buffer, digestion_buffer_stock_amt)
#     # digestion_buffer_storage = tube_rack["B1"]
#     # digestion_buffer_storage = reservoir.columns_by_name()['1']
#     # digestion_buffer_storage.load_liquid(digestion_buffer, digestion_buffer_stock_amt)
#     buffer_tube_rack = protocol.load_labware("opentrons_10_tuberack_falcon_4x50ml_6x15ml_conical", "C2", "new solution rack")
#     buffer_tube_rack["A1"].load_liquid(digestion_buffer, digestion_buffer_per_sample_amt*num_samples)
#     dig_buffer_location = buffer_tube_rack["A1"]
    
#     buffer_tube_rack["A3"].load_liquid(water, 100)
#     water_location = buffer_tube_rack["A3"]
#     buffer_tube_rack["A4"].load_liquid(acetonitrile, 100)
#     acn_location = buffer_tube_rack["A4"]
#     buffer_tube_rack["B3"].load_liquid(ammoniumAcetate, 100)
#     ammoniumAcetate_location = buffer_tube_rack["B3"]

#     working_reagent_reservoir["A1"].load_liquid(equilibration_buffer, equilibartion_buffer_amt)
#     working_reagent_reservoir["A2"].load_liquid(equilibration_buffer, equilibartion_buffer_amt)
#     working_reagent_reservoir["A3"].load_liquid(equilibration_buffer, equilibartion_buffer_amt)
#     equilibration_buffer_storage = [working_reagent_reservoir["A1"], working_reagent_reservoir["A2"], working_reagent_reservoir["A3"]]
    
#     working_reagent_reservoir["A4"].load_liquid(binding_buffer, binding_buffer_amt)
#     working_reagent_reservoir["A5"].load_liquid(binding_buffer, binding_buffer_amt)
#     working_reagent_reservoir["A6"].load_liquid(binding_buffer, binding_buffer_amt)
#     binding_buffer_storage = [working_reagent_reservoir["A4"], working_reagent_reservoir["A5"], working_reagent_reservoir["A6"]]

#     working_reagent_reservoir["A7"].load_liquid(wash_buffer, wash_buffer_amt)
#     working_reagent_reservoir["A8"].load_liquid(wash_buffer, wash_buffer_amt)
#     working_reagent_reservoir["A9"].load_liquid(wash_buffer, wash_buffer_amt)
#     wash_buffer_storage = [working_reagent_reservoir["A7"], working_reagent_reservoir["A8"], working_reagent_reservoir["A9"]]
#     # trash1=trash_reservoir.wells()[0].bottom(7)
#     staging_slots = ['A4', 'B4', 'C4', 'D4']
#     staging_racks = [protocol.load_labware('opentrons_flex_96_filtertiprack_200uL',
#                                       slot) for slot in staging_slots]

# #REPLENISHING TIPS

#     count = 0
#     #Functions
#     def remove_tip(pipette, is_dry_run):
#         if is_dry_run:
#             pipette.return_tip()
#         else:
#             pipette.drop_tip(chute)         
#     def pick_up(pip):
#         nonlocal tips1000
#         nonlocal staging_racks
#         nonlocal count

#         try:
#             pip.tip_racks = tips1000
#             pip.pick_up_tip()

#         except protocol_api.labware.OutOfTipsError:
#             check_tips()
#             pick_up(pip)    
#     def check_tips():
#         nonlocal tips1000
#         nonlocal staging_racks
#         nonlocal count
#         # tip_box = protocol.load_labware('opentrons_flex_96_filtertiprack_1000uL', 'A3')
#         for i in range (0,3):
#             tip_box_slots = ['A3', 'B3', 'C3']
#             bottom_right_well = tips1000[i].wells_by_name()['H12']
            
#             if bottom_right_well.has_tip or protocol.deck['D4'] == None:
#                 protocol.comment("A tip is present in the bottom-right corner (H12). or all staging slots are empty")
#                 if protocol.deck['D4'] == None:
#                     protocol.comment("No tip box detected in slot D4.")
#                     staging_slots = ['A4', 'B4', 'C4', 'D4']
#                     staging_racks = [protocol.load_labware('opentrons_flex_96_filtertiprack_200uL',
#                                       slot) for slot in staging_slots]
#                 pass
#             else:
#                 protocol.comment("\n\n\n Starting moving phase")
#                 protocol.move_labware(
#                         labware=tips1000[i],
#                         new_location=chute,
#                         use_gripper=True
#                     )
#                 rack_num = 0
#                 for slot in ['A4', 'B4', 'C4', 'D4']:
#                     labware = protocol.deck[slot]
#                     if labware and labware.is_tiprack:
#                         tips1000[i] = staging_racks[rack_num]
#                         protocol.move_labware(
#                             labware=staging_racks[rack_num],
#                             new_location=tip_box_slots[i],
#                             use_gripper=True
#                         )
#                         break
#                         # protocol.comment(f"A tip box is present in slot {slot}.")
#                     else:
#                         protocol.comment(f"No tip box detected in slot {slot}.")
#                         rack_num+=1
#                         pass
#     def create_buffers(total_vol, start_location, end_location):
#         '''
#         total_vol: list of transfer volumes in ul [vol1, vol2]
#         start_location: location of the acn, aa, or h2o
#         end_location: well number of the first slot for the buffer (1 to 12)
#         '''
#         protocol.comment(str(total_vol))
#         for i in range (0, len(total_vol)):
#             vol = total_vol[i]
#             for x in range (0, math.ceil(vol/1000)):
#                 if x != math.ceil(vol/1000)-1:  #not last one yet
#                     left_pipette.aspirate(1000, start_location)
#                     left_pipette.dispense(1000, working_reagent_reservoir["A" +str(end_location+i)].top(-5))
#                 else:
#                     left_pipette.aspirate(vol-(1000*x), start_location)
#                     left_pipette.dispense(vol-(1000*x),working_reagent_reservoir["A" +str(end_location+i)].top(-5))
#                 left_pipette.blow_out(working_reagent_reservoir["A" +str(end_location+i)].top(-5))
#     if protocol.params.create_buffers:
#         protocol.comment("-------------BUFFER CREATION ---------------")
#         channel_max_vol = 10000 #each channel can hold up to 10000 ul
#         acn_eq_vols = []
#         acn_binding_vols = []
#         acn_wash_vols = []
#         aa_eq_vols = []
#         aa_binding_vols = []
#         water_eq_vols = []
#         water_binding_vols = []
#         water_wash_vols = []
#         #equilibartion buffer
#         for i in range (0, math.ceil((equilibartion_buffer_amt*1000)/channel_max_vol)):
#             #Not on last loop yet
#             if i !=math.ceil((equilibartion_buffer_amt*1000)/channel_max_vol)-1:
#                 volumes =get_eq_buffer_vols(channel_max_vol, protocol.params.ammoniumAcetate_conc)
#                 acn_eq_vols.append(volumes['acn'])
#                 aa_eq_vols.append(volumes['ammonium_acetate'])
#                 water_eq_vols.append(volumes['water'])
#             else:
#                 volumes =get_eq_buffer_vols((equilibartion_buffer_amt*1000)-(channel_max_vol*i), protocol.params.ammoniumAcetate_conc)
#                 acn_eq_vols.append(volumes['acn'])
#                 aa_eq_vols.append(volumes['ammonium_acetate'])
#                 water_eq_vols.append(volumes['water'])
#         #Binding buffer
#         for i in range (0, math.ceil((binding_buffer_amt*1000)/channel_max_vol)):
#             #Not on last loop yet
#             if i !=math.ceil((binding_buffer_amt*1000)/channel_max_vol)-1:
#                 volumes =get_binding_buffer_vols(channel_max_vol, protocol.params.ammoniumAcetate_conc)
#                 acn_binding_vols.append(volumes['acn'])
#                 aa_binding_vols.append(volumes['ammonium_acetate'])
#                 water_binding_vols.append(volumes['water'])
#             else:
#                 volumes =get_binding_buffer_vols((equilibartion_buffer_amt*1000)-(channel_max_vol*i), protocol.params.ammoniumAcetate_conc)
#                 acn_binding_vols.append(volumes['acn'])
#                 aa_binding_vols.append(volumes['ammonium_acetate'])
#                 water_binding_vols.append(volumes['water'])
#         #Wash buffer
#         for i in range (0, math.ceil((wash_buffer_amt*1000)/channel_max_vol)):
#             #Not on last loop yet
#             if i !=math.ceil((wash_buffer_amt*1000)/channel_max_vol)-1:
#                 volumes =get_wash_buffer_vols(channel_max_vol)
#                 acn_wash_vols.append(volumes['acn'])
#                 water_wash_vols.append(volumes['water'])
#             else:
#                 volumes =get_wash_buffer_vols((equilibartion_buffer_amt*1000)-(channel_max_vol*i))
#                 acn_wash_vols.append(volumes['acn'])
#                 water_wash_vols.append(volumes['water'])
        
#         #Loading ACN
#         left_pipette.pick_up_tip()
#         create_buffers(acn_eq_vols, acn_location, 1)
#         create_buffers(acn_binding_vols, acn_location, 4)
#         create_buffers(acn_wash_vols, acn_location, 7)
#         remove_tip(left_pipette, protocol.params.dry_run)
        
#         #Loading Ammonium Acetate
#         left_pipette.pick_up_tip()
#         create_buffers(aa_eq_vols, ammoniumAcetate_location, 1)
#         create_buffers(aa_binding_vols, ammoniumAcetate_location, 4)
#         remove_tip(left_pipette, protocol.params.dry_run)
#         #Loading H2O
#         left_pipette.pick_up_tip()
#         create_buffers(water_eq_vols, water_location, 1)
#         create_buffers(water_binding_vols, water_location, 4)
#         create_buffers(water_wash_vols, water_location, 7)
#         remove_tip(left_pipette, protocol.params.dry_run)
#         protocol.comment("\n"*10)
#         protocol.comment(str(acn_eq_vols))
#         protocol.comment(str(acn_binding_vols))
#         protocol.comment(str(acn_wash_vols))
#         protocol.comment(str(aa_eq_vols))
#         protocol.comment(str(aa_binding_vols))
#         protocol.comment(str(water_eq_vols))
#         protocol.comment(str(water_binding_vols))
#         protocol.comment(str(water_wash_vols))
#         protocol.comment("\n"*10)

#         for j in range (0,3):
#             i = [acn_eq_vols, acn_binding_vols, acn_wash_vols][j]
#             left_pipette.pick_up_tip()
#             for x in range (0, len(i)):
#                 left_pipette.mix(3, 900, working_reagent_reservoir["A"+str(1+j*3+x)].bottom().move(types.Point(x=0, y=-20, z=3)))
#                 left_pipette.mix(3, 900, working_reagent_reservoir["A"+str(1+j*3+x)].bottom().move(types.Point(x=0, y=0, z=3)))
#                 left_pipette.mix(3, 900, working_reagent_reservoir["A"+str(1+j*3+x)].bottom().move(types.Point(x=0, y=20, z=3)))
#             remove_tip(left_pipette, protocol.params.dry_run)
            
