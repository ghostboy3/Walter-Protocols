from opentrons import protocol_api

from opentrons import types
metadata = {
    "protocolName": "Testing Large Well Plate",
    "author": "Nico To",
    "description": "Testing a large well plate with a 96-well format, V bottom",
}

requirements = {"robotType": "Flex", "apiLevel": "2.20"}
def add_parameters(parameters: protocol_api.Parameters):

    parameters.add_float(
        variable_name="offset_z",
        display_name="Number of Samples",
        description="Number of samples",
        default=4.1,
        minimum=-100,
        maximum=96,
        unit="samples",
    )

def run(protocol: protocol_api.ProtocolContext):
    
    def mix_sides(pipette, num_mixes, vol, plate, rate):
        pipette.mix(
            num_mixes, vol, plate.bottom().move(types.Point(x=0, y=1.5, z=offset+2)), rate=rate
        )
        pipette.mix(
            num_mixes,
            vol,
            plate.bottom().move(types.Point(x=0, y=-1.5, z=offset+2)),
            rate=rate,
        )
        pipette.mix(
            num_mixes, vol, plate.bottom().move(types.Point(x=1.5, y=0, z=offset+2)), rate=rate
        )
        pipette.mix(
            num_mixes,
            vol,
            plate.bottom().move(types.Point(x=-1.5, y=0, z=offset+2)),
            rate=rate,
        )
        pipette.mix(1, vol, plate.bottom(0.1+offset), rate=0.1)

    offset = protocol.params.offset_z
    reagent_plate = protocol.load_labware("opentrons_96_wellplate_200ul_pcr_full_skirt","D2","reagent plate")
    # reagent_plate.set_offset(x=0, y=0, z=protocol.params.offset_z)
    tips200 = [protocol.load_labware("opentrons_flex_96_filtertiprack_200uL", "A3")]
    left_pipette = protocol.load_instrument("flex_1channel_1000", "left", tip_racks=tips200)
    left_pipette.pick_up_tip()
    mix_sides(left_pipette, 3, 100, reagent_plate["A1"], 3)
    left_pipette.aspirate(100, reagent_plate.wells_by_name()["A1"].bottom(0.1+offset))
    left_pipette.return_tip()