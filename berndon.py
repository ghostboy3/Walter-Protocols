from opentrons import protocol_api

metadata = {
    "protocolName": "Adding formic acid",
    "author": "Nico To",
    "description": "Brendon protocol for adding formic acid to samples",
}
requirements = {"robotType": "Flex", "apiLevel": "2.20"}


def run(protocol: protocol_api.ProtocolContext):
    sample_plate = protocol.load_labware(
        "opentrons_96_wellplate_200ul_pcr_full_skirt", "C2", "sample stock plate"
    )
    final_plate = protocol.load_labware(
        "opentrons_96_wellplate_200ul_pcr_full_skirt", "D2", "final plate"
    )
    tube_rack = protocol.load_labware("opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap", "B2")
    formic_acid = tube_rack.wells_by_name()["A1"]
    tips50 = [
            protocol.load_labware("opentrons_flex_96_filtertiprack_50uL", "A3"),
            protocol.load_labware("opentrons_flex_96_filtertiprack_50uL", "B3"),
        ]
    left_pipette = protocol.load_instrument(
        "flex_1channel_50", "left", tip_racks=tips50
    )
    chute = protocol.load_waste_chute()


    wells = [ "D1", "E1", "F1", "G1", "H1", "A2", "B2", "C2", "D2", "E2", "F2", "G2", "H2", "A3", "B3", "C3", "D3", "A11", "B11", "C11", "D11", "G11", "H11"]
    vols = [ 13.9, 13.7, 14.2, 14.6, 16.4, 12.8, 12.5, 14.4, 12.2, 22.5, 17, 16, 11.9, 15.9, 13.1, 13.3, 19.4, 11.8, 9.4, 13.1, 49.2, 33, 31.5]
    for i in range (0, len(wells)):
        print (wells[i], vols[i])
        protocol.comment(f"{vols[i]} {wells[i]}")
        
        left_pipette.pick_up_tip()
        left_pipette.aspirate(vols[i], formic_acid.bottom(0.5), 0.7)
        left_pipette.dispense(vols[i], sample_plate.wells_by_name()[wells[i]].bottom(0.5), 0.7)
        left_pipette.mix(3, vols[i], sample_plate.wells_by_name()[wells[i]].bottom(0.5), rate=0.7)
        
        left_pipette.aspirate(vols[i], sample_plate.wells_by_name()[wells[i]].bottom(0.5), 0.7)
        left_pipette.dispense(vols[i], final_plate.wells_by_name()[wells[i]].bottom(0.5), 0.7)
        left_pipette.drop_tip(chute)