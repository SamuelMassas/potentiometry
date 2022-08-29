import numpy as np


def decimal2signed16bit(integer):
    """
    Converts an integer decimal number to a signed 16-bit string (twos complement)
    :param
        integer: int
            decimal base number
    :return:
    bit16: str
        16-bit array
    """
    if not isinstance(integer, int):
        raise TypeError("Only integers can be converted to 16-bit.")

    s = bin(integer & int("1"*16, 2))[2:]
    bit16 = ("{0:0>%s}" % (16)).format(s)

    return bit16


def signed16bit2decimal(bit16):
    """ Converts 2' complement to an decimal number"""
    if bit16[0] == '1':
        compl = int(bit16, 2) ^ int('1'*len(bit16), 2)
        dec = -(compl + 1)
    else:
        dec = int(bit16[1:], 2)
    return dec


def bits2bytes(bit16, order='LR'):
    """
    Converint a 16-bit string to bytes type
    :param
    bit16: str
        string with 16 bits
    :return:
    byte_array: bytes
        byte array
    """

    byteM = bit16[:8]
    byteL = bit16[8:]

    numM = int(byteM, 2)
    numL = int(byteL, 2)
    if order == 'LR':
        byte_array = bytes([numM, numL])
    else:
        byte_array = bytes([numL, numM])

    return byte_array


def bytes2bits(byte16):
    """
    Converts a byte array to a 16-bit string
    :param
    byte16: bytes
        Array with 2 bytes
    :return:
    bit16: str
        string containing 16 bits
    """
    # Converting to decimal
    decimal = int.from_bytes(byte16, byteorder='little', signed=False)
    # converting to bits
    bit16 = decimal2signed16bit(decimal)
    return bit16


def bytes2decimal(byte16):
    """
    Converts a byte array to decimal using 2'complement
    :param
    byte16: bytes
        Array with 2 bytes
    :return:
    decimal: int
        decimal number
    """
    # Converting to decimal
    decimal = int.from_bytes(byte16, byteorder='little', signed=True)
    return decimal
##########################################################################################################


def volt_dac(byte16):
    # bit16 = bytes2bits(byte16)
    # v0 = signed16bit2decimal(bit16[0:8])
    # v1 = int(bit16[8:], 2)
    #
    # vt = v1 + v0*256
    vt = bytes2decimal(byte16)
    volt = vt*2.45/32768

    return volt


def current_conversor(byte16):
    volt = volt_dac(byte16)
    return volt/24000


def get_parameters(time_step):
    """
    Loads the ramps from Ramps.txt and calculates the parameters for the measurement
    :return:
    n_ramps: int
        Number of ramps
    array: nd.array
        2D array containing the ramps
    """

    with open('Ramps.txt', 'r') as file:
        str_ramps = file.read()
    list_ramps = str_ramps.split('\n')

    n_ramps = len(list_ramps)-1

    array = np.zeros((n_ramps, 3))
    for i, item in enumerate(list_ramps):
        item_list = item.split('\t')
        for j, text in enumerate(item_list):
            try:
                if j == 2:
                    array[i, j] = float(text)/(time_step*5)
                else:
                    array[i, j] = float(text)*32768/2048  # ADC
            except ValueError:
                pass


    # Removing first row if any zeros
    if array[0, 2] < 1:
        array = np.delete(array, 0, axis=0)
        n_ramps = n_ramps - 1

    return n_ramps, array


def number_pts(time_array):
    npoints = 0
    for number in time_array:
        npoints = npoints + number

    return npoints
