from scipy.signal import find_peaks


def search(xx, yy):
    thresh = 0
    peakHeight = 0.001
    width = 10

    peaks, params_ = find_peaks(yy, width=width, height=thresh, prominence=peakHeight, rel_height=0.5)

    try:
        peaks = peaks[0]  # Allows only one peak, the first detected by default
    except IndexError:
        peaks = -1  # in case no peak is found
    # TODo calculate following parameters only if peak exists
    # baseline equation
    m = (yy[-1]-yy[0])/(xx[-1]-xx[0])
    b = yy[0] - m*xx[0]

    #peak height
    curr_base = m * xx[peaks] + b
    ph = yy[peaks] - curr_base

    area = peak_area(xx, yy, m, b)

    return peaks, params_, area, ph, xx[0], xx[-1], yy[0], yy[-1]



def peak_area(xx, yy, mbase, bbase):
    soma = 0

    for i in range(1, len(xx)):
        yb1 = mbase * xx[i - 1] + bbase
        yb2 = mbase * xx[i] + bbase
        area = (xx[i] - xx[i - 1]) * (yy[i] - yy[i - 1]) + (xx[i] - xx[i - 1]) * (yb2 - yb1) + \
               (xx[i] - xx[i - 1]) * (max([yy[i], yy[i - 1]]) - min(yb1, yb2))

        soma += area

    return soma
