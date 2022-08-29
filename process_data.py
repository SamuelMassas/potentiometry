import numpy as np

""" This modulo contains functions to process the raw data sent by the platform"""


def process_this(name, x, y, parameters):
    """
    process_this will identify the nature of the data and call the most suitable function process the data.
    get_parameters should be called prior to this function in the main code, to gather the information need by this
    function to make the correct call.

    :param name: str
        Name of the electrochemical technic
    :param x: ndarray
        numpy vector containing the x points
    :param y: ndarray
        numpy vector containing y points
    :param parameters: dictionary
        dictionary containing the key value pairs with the names (key) and values (value) of the used parameters during
        the measure

    :return delta_y: ndarray
        Processed y data
    :return delta_x: ndarray
        Processed x data
    """
    if name == 'Normal Pulse Voltammetry' or name == 'Differential Pulse Voltammetry':

        npts_pulse = int(parameters['t pulse (s)'] * 1000 / 5)
        npts_base = round(parameters['E step (V)'] / parameters['Scan rate (V/s)'] * 1000 / 5 - npts_pulse)

        delta_y, volt_x = raw2dpv(x, y, npts_base, npts_pulse)
    elif name == 'Square Wave Voltammetry':
        npts_base = int(1/parameters['Frequency (Hz)'] * 1000 / 2 / 5)
        npts_pulse = npts_base

        delta_y, volt_x = raw2dpv(x, y, npts_base, npts_pulse)
    else:
        # If the data doesn't need to be processed
        delta_y, volt_x = y, x

    return delta_y, volt_x


def get_parameters(file=None):
    """
    This function loads the data saved in (...)/Active_parameters.txt and build a dictionary with it.

    :param file: .txt file
        file containing the saved parameters

    :return name: str
        name of the electrochemical technic
    :return parameters: dictionary
        dictionary containing the key value pairs with the names (key) and values (value) of the used parameters during
        the measure
    """
    if file is None:
        # If no other path is given used default path for file
        with open('Active_parameters.txt', 'r') as file:
            data = file.read()
    else:
        data = file

    data = data.split('\n')
    name = data[0]
    parameters = {}
    for item in data[1:-1]:
        key, value = item.split('\t')
        parameters[key] = float(value)

    return name, parameters


def raw2dpv(x, y, npts_base, npts_pulse):
    """
    Preprocessing pulse nature data. DPV, NPV

    :param x: ndarray
        numpy vector containing the x points
    :param y: ndarray
        numpy vector containing y points
    :param npts_base: integer
        number of points measured before the pulse (base)
    :param npts_pulse:
        number of points measured during the pulse

    :return delta_y: ndarray
        Processed y data
    :return delta_x: ndarray
        Processed x data
    """
    npts = npts_base+npts_pulse
    base_x = []
    pulse_x = []
    base_y = []
    pulse_y = []

    for i in range(0, len(x), npts):
        i_base = i + npts_base
        i_pulse = i_base+npts_pulse
        base_x.append(np.mean(x[i:i_base]))
        base_y.append(np.mean(y[i:i_base]))

        pulse_x.append(np.mean(x[i_base:i_pulse]))
        pulse_y.append(np.mean(y[i_base:i_pulse]))

    delta_y = []
    for i in range(len(base_x)):
        delta_y.append(pulse_y[i] - base_y[i])

    return delta_y, base_x


def raw2sw(x, y, npts):
    """
    Preprocessing pulse nature data. SW

    :param x: ndarray
        numpy vector containing the x points
    :param y: ndarray
        numpy vector containing y points
    :param npts: integer
        number of points measured per half wave

    :return delta_y: ndarray
        Processed y data
    :return delta_x: ndrray
        Processed x data
    """

    cathodic_x = []
    anodic_x = []
    cathodic_y = []
    anodic_y = []
    a = 'cath'

    for i in range(0, len(x), npts):
        if a == 'cath':
            cathodic_x.append(np.mean(x[i:(i + npts)]))
            cathodic_y.append(np.mean(y[i:(i + npts)]))
            a = 'ano'
        else:
            anodic_x.append(np.mean(x[i:(i + npts)]))
            anodic_y.append(np.mean(y[i:(i + npts)]))
            a = 'cath'

    delta_y = []
    for i in range(len(cathodic_x)):
        delta_y.append(anodic_y[i]-cathodic_y[i])

    return delta_y, anodic_x
