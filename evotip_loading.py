from opentrons import protocol_api
import math
# import requests
import urllib.request
import urllib.parse
import json



metadata = {
    "protocolName": "Evotip Loading",
    "author": "Nico To",
    "description": "aaaa vacuums suck. My attempt at loading Evotips.",
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
    parameters.add_float(
        variable_name="offset",
        display_name="offset",
        description="height offset amount",
        default=30,
        minimum=0,
        maximum=100,
        unit="mm"
    )

def send_command_to_raspberry_pi(command):
    url = "http://10.197.116.85:5000/command"
    data = {"command": command}
    data_encoded = json.dumps(data).encode('utf-8')
    
    req = urllib.request.Request(url, data=data_encoded, headers={'Content-Type': 'application/json'})
    
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                print(f"{command} command sent successfully")
            else:
                print(f"Failed to send {command} command")
    except urllib.error.URLError as e:
        print(f"Failed to send {command} command. Error: {e.reason}")


def run(protocol: protocol_api.ProtocolContext):
    num_samples = protocol.params.numSamples
    # Loading stuff
    tips1000 = [protocol.load_labware("opentrons_flex_96_filtertiprack_1000uL", slot) for slot in ["A3"]]   # add more later
    tips50 = [protocol.load_labware("opentrons_flex_96_filtertiprack_50uL", slot) for slot in ["B3"]]   # add more later
    left_pipette = protocol.load_instrument("flex_1channel_1000", "left", tip_racks=tips1000)
    right_pipette = protocol.load_instrument("flex_1channel_50", "right", tip_racks=tips50)
    vacuum_box = protocol.load_labware("opentrons_96_wellplate_200ul_pcr_full_skirt", "C3", "reagent plate")
    vacuum_box.set_offset(x=0, y=0, z=protocol.params.offset)
    
    
    # testing the location
    right_pipette.pick_up_tip()
    for i in range (0, num_samples):
        right_pipette.aspirate(10, vacuum_box.wells()[i].top())
        send_command_to_raspberry_pi("start_vacuum")
        protocol.delay(minutes=2)
        send_command_to_raspberry_pi("stop_vacuum")
        right_pipette.dispense(10, vacuum_box.wells()[i].top())
        protocol.delay(seconds=10)
    right_pipette.return_tip()
    