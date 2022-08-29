import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


def read_excel(filename):
    """
    Loads the data from a excel file.
    :param
    filename: str
        string with the path to the desired file
    :return:
    xx: ndarray
        array with the frequencies
    yy: complex ndarray
        impedance array
    """
    data = pd.read_excel(filename)

    # take the ndarray from dataframe
    np_data = data.values

    xx = np_data[:, 0]
    yy = np_data[:, 1]

    return xx, yy


def read_csv_sdf(filename):
    """
     Loads the data from a CSV or space delimited file.
     :param
     filename: str
         string with the path to the desired file
     :return:
     xx: ndarray
         array with the frequencies
     yy: complex ndarray
         impedance array
     """
    with open(filename, 'r') as file:
        file = file.read()

        # Checking the delimiter
        if file.find(',') == -1:
            char = ' '
        else:
            char = ','

        # Rearrange file
        file = file.split('\n')
        pro_data = np.array([[0, 0],
                             [0, 0]])

        for i, item in enumerate(file):
            item = item.split(char)

            try:
                item = np.array([[float(i) for i in item]])
                pro_data = np.concatenate((pro_data, item))
            except ValueError:
                pass

        xx = pro_data[2:, 0]
        yy = pro_data[2:, 1]
        return xx, yy


def corr_(y_ini, y_fit):
    """
    Calculates the correlation coefficient between the initial data and the predicted data from a fitting model.
    :param
    y_ini: ndarray
        initial data
    y_fit: ndarray
        predicted data
    :return:
    rs: float
        coefficient
    """
    res = y_ini - y_fit
    s_res = np.sum(res ** 2)

    y_mean = np.mean(y_ini)
    variance = y_ini - y_mean
    s_tol = np.sum(variance ** 2)

    r_square = 1 - s_res / s_tol

    return r_square


def parabola(x, a, b, c):
    """
    Defines a quadratic function
    :param
    x: float, int

    with a,b and c being the coefficients
    a: float, int
    b: float, int
    c: float, int
    :return:
    y: float int
        f(x)
    """
    y = a*x**2 + b*x + c
    return y


def quad_deriv(cofs):
    """
    Derivative of ax**2 + bx + c
    :param
    cofs: ndarray
        Contains the coefficients from the quadratic equation
    :return:
    slope: float
        slope of the first derivative
    """

    a = cofs[0]
    b = cofs[1]
    c = cofs[2]

    slope = 2*a
    return slope


def transform(x, y):
    """
    -Transform Matrix-

        [ xt ] = [     1            0     ] * [x]
        [ yt ]   [ sin(teta)    cos(teta) ]   [y]

    Rotates a function according to the points of the extremities of that function.
    math:
        The final rotation must produce a function in which:
                Ri = Rf
        with R being the rotated function and i and f the first and last point of the array.
        According to the rotation matrix:
                x' = x*1 - y*0
                y' = x*sin(teta) + y*cos(teta)
        So,
                xi*sin(teta) + yi*cos(teta) = xf*sin(teta) + yf*cos(teta)
            =>  (xi-xf)*tan(teta) = yf-yi
            =>  teta = arctan((yf-yi)/(xi-xf))

    :param
    x: ndarray
    y: ndarray
    :return:
    rot_x: ndarray
        rotated data
    rot_y: ndarray
        rotated data
    """

    teta = np.arctan((y[-1]-y[0])/(x[0]-x[-1]))

    rot_x = x*1-y*0
    rot_y = x*np.sin(teta) + y*np.cos(teta)

    return rot_x, rot_y, teta


def transform_inv(xt, yt, teta):
    """
    -Inverse of transform matrix-
    Rotates the data back to the original coordinates.
    math:
            x' = x
            y' = x*sin(teta) + y*cos(teta)
        Solving both equation in order to the initial coordinates, x and y:
            x = x'
            y = y'/cos(teta) - x*tan(teta)

    :param
    xt: ndarray
        Transform x data
    yt: ndarray
        transform y data
    teta: float
        angle of the transformation in radians

    :return:
    xdata: ndarray
        xdata in the initial coordinates. Transform inverse of xt
    ydata: ndarray
        ydata in the initail coordinates  Transform inverse of yt
    """
    x_real = xt * 1 - yt * 0
    y_real = yt/np.cos(teta) - x_real*np.tan(teta)

    return x_real, y_real


def identify_baseline(xrs_array, yts_array, slopes_array):
    """
    Identifies the x coordinates at which the peak starts and ends.
        1º splits the slopes array by the max value (related to the peak) of that array and finds the minimal value
            of each split. This minimal values positions, correspond to the x arrays (in xrs_array)
            where the peaks start and end.
        2º Select the transformed y and x data that origins the minimal slopes and finds the max value var of x. This
            max values are the points in the initial coordinates where the peaks start and end.

    :param:
    xrs_array: ndarray
        2 dimensional array that contains the x arrays used for fitting, sorted in rows
    yts_array: ndarray
        2 dimensional array with the transformed y arrays values used in fitting, sorted in rows
    slopes_array: ndarray
        array with all the calculated slopes from the fittings

    :return:
    max_xr_left: float
        the x value where the peak starts
    max_xr_right:
        the x value where the peak ends
    """

    """ Splitting the slopes array in the var that holds the maximum slope (corresponding to the peak) """
    max_slope = max(slopes_array)
    splitter = np.where(slopes_array == max_slope)
    splitter = int(splitter[0])
    left_slopes = slopes_array[:splitter]
    right_slopes = slopes_array[splitter:-1]

    """ minimal of left slopes (corresponds to beginning of the peak) """
    minl_slope = min(left_slopes)
    ileft = int(np.where(left_slopes == minl_slope)[0])
    """ miminal of right slopes (corresponds to ending of the peak) """
    minr_slope = min(right_slopes)
    iright = int(np.where(right_slopes == minr_slope)[0]) + splitter

    """ Finding the max value var of each yt array inside the yts_array """
    yt_left = yts_array[ileft, :]
    yt_right = yts_array[iright, :]
    basel_yt_i = int(np.where(yt_left == max(yt_left))[0])
    baser_yt_i = int(np.where(yt_right == max(yt_right))[0])
    # basel_yt_i = 0
    # baser_yt_i = -1

    """ Check where this max indexes are in the initial coordinates """
    xr_left = xrs_array[ileft, :]
    xr_right = xrs_array[iright, :]

    max_xr_left = xr_left[basel_yt_i]
    max_xr_right = xr_right[baser_yt_i]

    return max_xr_left, max_xr_right


def peak_height(peak_pot, peak_curr, xbase, ybase):
    # define a line
    m = (ybase[1]-ybase[0])/(xbase[1]-xbase[0])
    b = ybase[1] - m*xbase[1]

    curr_base = m*peak_pot + b
    ph = peak_curr - curr_base
    return ph, m, b


def peak_area(xx, yy, mbase, bbase):
    soma = 0

    for i in range(1, len(xx)):
        yb1 = mbase * xx[i - 1] + bbase
        yb2 = mbase * xx[i] + bbase
        area = (xx[i] - xx[i - 1]) * (yy[i] - yy[i - 1]) + (xx[i] - xx[i - 1]) * (yb2 - yb1) + \
               (xx[i] - xx[i - 1]) * (max([yy[i], yy[i - 1]]) - min(yb1, yb2))

        soma += area

    return soma


def runner(xdata, ydata, length, step):
    i = 0
    j = length

    slopes = np.array([])
    yt_s = np.zeros((1, length))
    x_samps = np.zeros((1, length))
    count = 0
    while j <= len(xdata):
        """ Selecting sample of data to be fitted"""
        x_samp = xdata[i:j]
        y_samp = ydata[i:j]
        i += step
        j = i+length
        count += 1

        """ transform the data using the transform matrix """
        xt, yt, teta = transform(x_samp, y_samp)
        popt_t, pcov_t = curve_fit(parabola, xt, yt, p0=[1, 1, 1])
        fit_t = parabola(xt, popt_t[0], popt_t[1], popt_t[2])
        x_real, fit_real = transform_inv(xt, fit_t, teta)

        # Analyses
        r2 = corr_(yt, fit_t)
        slope = quad_deriv(popt_t)
        ax2.plot(count, slope, 's')
        print(f'{name} in j={j}: m = {slope}, r**2 = {r2}')

        slopes = np.concatenate((slopes, [slope]))
        yt_s = np.concatenate((yt_s, [yt]))
        x_samps = np.concatenate((x_samps, [x_samp]))

        ax.plot(x_real, fit_real, '-')

    try:
        # Visualization
        base_x0, base_x1 = identify_baseline(x_samps[1:, :], yt_s[1:, :], slopes)
        base_xi0 = int(np.where(xdata == base_x0)[0])
        base_xi1 = int(np.where(xdata == base_x1)[0])
        base_y0 = ydata[base_xi0]
        base_y1 = ydata[base_xi1]
        base_x = np.array([base_x0, base_x1])
        base_y = np.array([base_y0, base_y1])
        ax.plot(base_x, base_y, 'y-')

        # Selecting data for peak search
        y_peak = ydata[base_xi0:base_xi1]
        x_peak = xdata[base_xi0:base_xi1]
        xt_peak, yt_peak, teta = transform(x_peak, y_peak)
        yt_peak_min = min(yt_peak)
        yt_i = int(np.where(yt_peak == yt_peak_min)[0])
        y_pp = y_peak[yt_i]
        x_pp = x_peak[yt_i]

        ax.plot(x_pp, y_pp, 'r*')

        # Calculating peak height and area
        ph, m, b = peak_height(x_pp, y_pp, base_x, base_y)
        area = peak_area(x_peak, y_peak, m, b)

        ax.text(x_pp, y_pp*1.25, f'Ph = {round(ph, 3)} uA\n'
                                 f'x = {round(x_pp, 2)} V\n'
                                 f'Area = {round(area, 3)} a.u.')
        return ph, x_pp, area

    except ValueError:
        print(f'Error in {name}')


vector = [0, 5, 10, 20, 50, 75, 100, 150, 200, 250, 300, 500, 600, 700, 800, 900]
# vector = [300]
phs = np.array([])
x_pps = np.array([])
areas = np.array([])
for name in vector:
    pot, curr = read_csv_sdf(f'./SW peaks find data/{name}ugl.csv')

    fig = plt.figure(label=str(name))
    ax = fig.add_subplot(121)
    ax.plot(pot, curr, '.')
    ax.set_ylabel('Current/uA')
    ax.set_xlabel('Potential/V')
    ax2 = fig.add_subplot(122)
    ax2.plot([], [])
    ax2.set_ylabel('Slope (Second derivative)')
    ax2.set_xlabel('Parabola')
    ph, x_pp, area = runner(pot, curr, 7, 5)
    phs = np.concatenate((phs, [ph]))
    x_pps = np.concatenate((x_pps, [x_pp]))
    areas = np.concatenate((areas, [area]))

for i in phs:
    print(i)
print('#'*50)
for i in x_pps:
    print(i)
print('#' * 50)
for i in areas:
    print(i)
plt.show()
