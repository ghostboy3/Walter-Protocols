import opentrons.simulate
protocol_file = open('protocol.py')
opentrons.simulate.simulate(protocol_file)
