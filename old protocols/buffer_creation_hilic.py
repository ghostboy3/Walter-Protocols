# Creates the equilibration, binding, and wash buffer buffer for the HILIC protocol
from opentrons import protocol_api
import math

metadata = {
    "protocolName": "Buffer Creation in the HILIC protocol",
    "author": "Nico To",
    "description": '''
    Creates the equilibration, binding, and wash buffer for the HILIC protocol
    Equilibration Buffer: 100mM ammonium acetate pH 4.5, 15%% acetonitrile
    Binding 'Buffer: 200 mM ammonium acetate pH 4.5, 30%% acetonitrile
    Wash Buffer: 95%% acetonitrile (5%% water)
    ''',
}

requirements = {"robotType": "Flex", "apiLevel": "2.19"}

def add_parameters(parameters: protocol_api.Parameters):
    parameters.add_int(
        variable_name="ammoniumAcetate_conc",
        display_name="Concentration of Ammonium Acetate Stock",
        description="_______ mM Ammonium Acetate (4.5pH)",
        default=300,
        minimum=100,
        maximum=1000,
        unit="mM"
    )
    
    parameters.add_float(
        variable_name="ammoniumAcetate_amt",
        display_name="Amount of Ammonium Acetate Stock",
        description="_______ ml Ammonium Acetate (4.5pH) in 50ml falcon",
        default=50,
        minimum=5,
        maximum=50,
        unit="ml"
    )

    parameters.add_float(
        variable_name="acn_amt",
        display_name="Amount of 100% Acetonitrile Stock",
        description="_______ ml 100% Acetonitrile in 50ml falcon",
        default=50,
        minimum=5,
        maximum=50,
        unit="ml"
    )
    
    parameters.add_float(
        variable_name="water_amt",
        display_name="Amount of H2O Stock",
        description="_______ ml water in 50ml falcon",
        default=50,
        minimum=5,
        maximum=50,
        unit="ml"
    )

    parameters.add_float(
        variable_name="eq_buff_amt",
        display_name="Equilibration Buffer Amount",
        description="Amount of equilibration buffer to create",
        default=5,
        minimum=1,
        maximum=15,
        unit="ml"
    )

    parameters.add_float(
        variable_name="binding_buff_amt",
        display_name="Binding Buffer Amount",
        description="Amount of binding buffer to create",
        default=5,
        minimum=1,
        maximum=15,
        unit="ml"
    )
    
    parameters.add_float(
        variable_name="wash_buff_amt",
        display_name="Wash Buffer Amount",
        description="Amount of wash buffer to create",
        default=5,
        minimum=1,
        maximum=15,
        unit="ml"
    )

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
    ammonium_acetate = (total_buffer_amt-acn)*(100/ammonium_acetate_concentration)
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
    ammonium_acetate = (total_buffer_amt-acn)*(200/ammonium_acetate_concentration)
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


print(get_eq_buffer_vols(5000, 300))
print(get_binding_buffer_vols(5000, 300))
print(get_wash_buffer_vols(5000))
    
    
        
