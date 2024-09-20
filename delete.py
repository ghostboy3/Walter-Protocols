def get_height(volume):
    '''
    Get's the height of the liquid in the tube
    Volume: volume of liquid in tube in µl
    Return: hieght from bottom of tube in millimeters
    '''
    height = 1
    # return 0.1
    
    #cylinder part
    if volume > 500:
        height= 0.015*volume+11.5
        # return height

    elif volume <= 500 and volume >0:     # cone part aaa
        # volume = volume/1000
        height = -0.0000372 * (volume**2)+0.0491*volume+3.749 # y=-0.0000372x^{2}+0.0491x+3.749
    
    if height < 0.1:
        return 0.1
    return height

print(get_height(500))