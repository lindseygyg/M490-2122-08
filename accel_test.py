import time

import numpy as np  # This is the package needed for functions.

import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.integrate import cumtrapz, trapz
from scipy import signal, special

import csv
import sys

GRAVITY_MS2 = 9.81

def accel_fit(x_input, m_x, b):
    return (m_x*x_input) - b  # fit equation for accel calibration

def accel_fit_sin(x_input, amp, w, p, o):
    return amp * np.sin(w*x_input + p) + o  # std sin fit equation for accel calibration

def sine_curve_fitting(time_array, a_array):
    """
    # Rasha's link: https://www.mathworks.com/matlabcentral/answers/121579-curve-fitting-to-a-sinusoidal-function
    """
    # t_array = np.arange(0, 10, 0.1)     # np.linspace(-5, 5, num=50)
    # accel_array = np.sin(t_array)

    t_array = time_array
    accel_array = a_array

    params, _ = curve_fit(accel_fit_sin, t_array, accel_array, bounds=((.25, 0, -np.pi*2, -.5), (1, 10, 2*np.pi, .5)), maxfev=10000)

    print(params)

    fig, ax = plt.subplots()
    ax.plot(t_array, accel_array, '-o')     # original data points

    new_func = params[0] * np.sin(params[1]*np.array(t_array) + params[2]) + params[3]
    ax.plot(t_array, new_func)

    ax.set_title('Test data plot')
    plt.show()

    # output trial frequency based on average peaks
    get_frequency(t_array, new_func)  # both should be arrays

def integration_test(input_test_data=[]):
    """
    Graphs with and without filter for visual/testing purposes
    """
    data_indx = 2
    mpu_labels = ['a_x', 'a_y', 'a_z']

    plt.style.use('ggplot')
    plt.ion()
    fig, axs = plt.subplots(3, 2, figsize=(12, 9))

    t_array = input_test_data[0]
    accel_array = input_test_data[1]

    dt_stop = t_array[-1]-t_array[0]

    ##################################
    # Signal Filtering
    ##################################
    accel_arrayHP = np.multiply(accel_array, GRAVITY_MS2)
    fs = len(accel_array) / dt_stop    # fs is the sampling rate, in Hz

    ##################################
    # Print Sample Rate and Accel
    # Integration Value
    ##################################
    # print("Sample Rate: {0:2.0f}Hz".format(len(accel_arrayHP) / dt_stop))

    veloc_array = np.zeros(len(accel_arrayHP))

    for n in range(1, len(accel_array)):
        veloc_array[n] = veloc_array[n-1] + accel_arrayHP[n]/fs

    order = 1  # Order is the order of the filter -
    fs = len(accel_array) / dt_stop     # fs is the sampling rate, in Hz
    corner = 0.1  # corner is frequency cut off, so we will keep all data less
    nyq = 0.5 * fs

    # Butterworth Filter - a signal processing filter that aims for
    # as flat a frequency response as possible in the pass band (aka band pass).
    b, a = signal.butter(order, corner / nyq, btype='high', analog=False)
    veloc_arrayHP = signal.filtfilt(b, a, veloc_array)

    disp_array = np.zeros(len(veloc_arrayHP))

    for n in range(1, len(veloc_arrayHP)):
        disp_array[n] = disp_array[n-1] + veloc_arrayHP[n]/fs

    order = 1  # Order is the order of the filter -
    fs = len(accel_array) / dt_stop
    # fs is the sampling rate, in Hz
    corner = 0.1  # corner is the frequency cut off, so we will keep all data less
    # than 0.1 Hz and everything greater than 0.1 Hz will be attenuated.
    nyq = 0.5 * fs
    # Butterworth Filter - a signal processing filter that aims for
    # as flat a frequency response as possible in the passband (aka band pass).
    b, a = signal.butter(order, corner / nyq, btype='high', analog=False)
    disp_arrayHP = signal.filtfilt(b, a, disp_array)

    axs[0, 0].plot(t_array, accel_arrayHP, label="$"+mpu_labels[data_indx]+"$",
                color=plt.cm.Set1(0), linewidth=2.5)

    axs[1, 0].plot(t_array, veloc_arrayHP,
                label="$v_"+mpu_labels[data_indx].split("_")[1]+"$",
                color=plt.cm.Set1(1), linewidth=2.5)

    axs[2, 0].plot(t_array, disp_arrayHP,
                label="$d_"+mpu_labels[data_indx].split("_")[1]+"$",
                color=plt.cm.Set1(2), linewidth=2.5)

    # UNFILTERED DATA
    axs[0, 1].plot(t_array, accel_array, label="$"+mpu_labels[data_indx]+"$",
                color=plt.cm.Set1(0), linewidth=2.5)

    axs[1, 1].plot(t_array, veloc_array,
                label="$v_"+mpu_labels[data_indx].split("_")[1]+"$",
                color=plt.cm.Set1(1), linewidth=2.5)

    axs[2, 1].plot(t_array, disp_array,
                label="$d_"+mpu_labels[data_indx].split("_")[1]+"$",
                color=plt.cm.Set1(2), linewidth=2.5)

    #[axs[ii].legend() for ii in range(0, len(axs))]
    axs[0, 0].set_ylabel('Acceleration [m$\cdot$s$^{-2}$]', fontsize=12)
    axs[0, 1].set_ylabel('Acceleration [m$\cdot$s$^{-2}$]', fontsize=12)

    axs[1, 0].set_ylabel('Vel [m$\cdot$s$^{-1}$]', fontsize=12)
    axs[1, 1].set_ylabel('Vel [m$\cdot$s$^{-1}$] NO FILTER', fontsize=12)

    axs[2, 0].set_ylabel('Displacement [m]', fontsize=12)
    axs[2, 1].set_ylabel('Displacement [m] NO FILTER', fontsize=12)

    axs[0, 0].set_title("MPU9250 Accelerometer Integration", fontsize=18)
    axs[0, 1].set_title("MPU9250 Accelerometer Integration NO FILTER", fontsize=18)

    axs[2, 0].set_xlabel('Time [s]', fontsize=18)
    axs[2, 1].set_xlabel('Time [s]', fontsize=18)

    plt.pause(0.01)
    plt.savefig("accel_veloc_displace_integ.png", dpi=300,
                bbox_inches='tight', facecolor="#FCFCFC")

    return t_array, disp_arrayHP

def get_displacement_data(t_array, a_array):
    """
    Rasha's test function - outputs 3 graphs (accel, vel, pos)
    Utilizes 2 high pass filters
    :return:
    """
    data_indx = 2
    mpu_labels = ['a_x', 'a_y', 'a_z']

    plt.style.use('ggplot')
    plt.ion()
    fig, axs = plt.subplots(3, 1, figsize=(12, 9))

    ##################################
    # Signal Filtering
    ##################################
    accel_arrayHP = np.array(a_array) * GRAVITY_MS2
    fs = len(a_array) / (t_array[-1]-t_array[0])     # fs is the sampling rate, in Hz

    ##################################
    # Print Sample Rate and Accel
    # Integration Value
    ##################################
    # print("Sample Rate: {0:2.0f}Hz".format(len(accel_arrayHP) / dt_stop))

    veloc_array = np.zeros(len(accel_arrayHP))

    for n in range(1, len(a_array)):
        veloc_array[n] = veloc_array[n-1] + accel_arrayHP[n]/fs

    order = 1  # Order is the order of the filter
    corner = 0.1  # corner is frequency cut off, so we will keep all data less
    nyq = 0.5 * fs

    # Butterworth Filter - a signal processing filter that aims for
    # as flat a frequency response as possible in the pass band (aka band pass).
    b, a = signal.butter(order, corner / nyq, btype='high', analog=False)
    veloc_arrayHP = signal.filtfilt(b, a, veloc_array)

    disp_array = np.zeros(len(veloc_arrayHP))

    for n in range(1, len(veloc_arrayHP)):
        disp_array[n] = disp_array[n-1] + veloc_arrayHP[n]/fs

    order = 1  # Order is the order of the filter
    # fs is the sampling rate, in Hz
    corner = 0.1  # corner is the frequency cut off, so we will keep all data less
    # than 0.1 Hz and everything greater than 0.1 Hz will be attenuated.
    nyq = 0.5 * fs
    # Butterworth Filter - a signal processing filter that aims for
    # as flat a frequency response as possible in the passband (aka band pass).
    b, a = signal.butter(order, corner / nyq, btype='high', analog=False)
    disp_arrayHP = signal.filtfilt(b, a, disp_array)

    axs[0].plot(t_array, accel_arrayHP, label="$"+mpu_labels[data_indx]+"$",
                color=plt.cm.Set1(0), linewidth=2.5)

    axs[1].plot(t_array, veloc_arrayHP,
                label="$v_"+mpu_labels[data_indx].split("_")[1]+"$",
                color=plt.cm.Set1(1), linewidth=2.5)

    axs[2].plot(t_array, disp_arrayHP,
                label="$d_"+mpu_labels[data_indx].split("_")[1]+"$",
                color=plt.cm.Set1(2), linewidth=2.5)

    [axs[ii].legend() for ii in range(0, len(axs))]
    axs[0].set_ylabel('Acceleration [m$\cdot$s$^{-2}$]', fontsize=16)
    axs[1].set_ylabel('Velocity [m$\cdot$s$^{-1}$]', fontsize=16)
    axs[2].set_ylabel('Displacement [m]', fontsize=16)
    axs[2].set_xlabel('Time [s]', fontsize=18)
    axs[0].set_title("MPU9250 Accelerometer Integration", fontsize=18)
    plt.pause(0.01)
    plt.savefig("accel_veloc_displace_integration.png", dpi=300,
                bbox_inches='tight', facecolor="#FCFCFC")

    return t_array, disp_arrayHP

def get_frequency(t_array, data_array):
    """
    Test function called by sine_curve_fitting to see if peaks work
    Output trial frequency based on average peaks
    :param time_points: t_array
    :param data_points: accel_array (or velocity, data)
    :return:
    """
    peaks, _ = signal.find_peaks(data_array, height=None, threshold=0.05, distance=50, prominence=1)
    print(peaks)

    total_tau = []

    #for p in range(1, len(peaks)):
    #    tau = t_array[p-1] - t_array[p]
    #    total_tau.append(tau)

    #print("frequency:", np.average(total_tau)/(2*np.pi))


def rk4_trap(t_array, a_array):
    """
    Rasha's test function - outputs 3 graphs (accel, vel, pos)
    Utilizes 2 high pass filters
    :return:
    """
    plt.style.use('ggplot')
    plt.ion()
    fig, axs = plt.subplots(3, 1, figsize=(12, 9))

    a = np.array(a_array) #* GRAVITY_MS2

    # root mean square
    #av = np.mean(a)
    #rms = np.sqrt((av - a)**2).mean()
    # print(rms)

    # start at 0, 0
    # dx/dt = v(t) (y1 = x)
    # dv/dt = a(t) (y2 = v; a is value we measure)
    # w = [x, v]; wdot = [xdot, vdot] = [w1, a]
    # initial conditions: x(0) = 0; v(0) = 0
    # f is a fcn of [v(t), a(t)] column vector
    # f(ti, wi) = [vi, ai] where wi is fcn of (xi, vi)
    a1 = []
    v = np.zeros(len(a))
    x = np.zeros(len(a))

    w = np.array([0, 0])
    delt = 2

    t0 = t_array[0]

    for i in range(len(a)-1):

        if int((t_array[i] - t0) % delt) == 0:   # reset every 2 seconds
            a1 = np.zeros(len(a))
            # correction factor
            item = t_array[i] - t0
            t_index = np.array(t_array)
            index = np.where(t_index > item)
            if len(index[0]) > 0:
                av = np.mean(a[index[0][0]:])
            a1[index[0][0]:] = a[index[0][0]:] - av

        # at time 0, w1 = velocity, w2 = acceleration
        # w approximates x and v; first is position, second is velocity; for each time step
        h = t_array[i+1] - t_array[i]   # time step
        # second component of w (w[1]: v)
        k1 = np.array([w[1], a1[i]])   # v, a
        # +2 = np.array(w[1] + h/2 * k1[1], a[i])

        # k3 = np.array(w[1] + h/2 * k2[0], a[i])
        # k4 = w + h*k3
        # w = w + (h/6)*k1 + 2*k2 + 2*k3 + k4)
        w = w + h*k1

        x[i] = w[0]
        v[i] = w[1]
        # error function only works for ~0
        # x = np.subtract(x,special.erg(x))

    axs[0].plot(t_array, a, color=plt.cm.Set1(0), linewidth=2.5)

    axs[1].plot(t_array, v, color=plt.cm.Set1(1), linewidth=2.5)

    axs[2].plot(t_array, x, color=plt.cm.Set1(2), linewidth=2.5)

    axs[0].set_ylabel('Acceleration [m$\cdot$s$^{-2}$]', fontsize=16)
    axs[1].set_ylabel('Velocity [m$\cdot$s$^{-1}$]', fontsize=16)
    axs[2].set_ylabel('Displacement [m]', fontsize=16)
    axs[2].set_xlabel('Time [s]', fontsize=18)
    axs[0].set_title("MPU9250 Accelerometer Integration", fontsize=18)
    plt.pause(0.01)
    #plt.savefig("accel_veloc_displace_integration.png", dpi=300,
    #            bbox_inches='tight', facecolor="#FCFCFC")
    plt.show()

    return t_array, w[1]


if __name__ == '__main__':

    print("Beginning Program.")
    # REAL FUNCTION TESTS

    ta = []
    aa = []

    file = r'/Users/lindsey/Desktop/data_raw_accel.csv'#/Users/lindsey/Desktop/data_raw_accel.csv
    reader = csv.DictReader(open(file))
    for raw in reader:
        ta.append(float(raw['t']))
        aa.append(float(raw['a']))

    #sine_curve_fitting(ta, aa)
    #get_displacement_data(ta, aa)
    #integration_test([ta, aa])

    a_zeros = np.zeros(len(aa))
    a_ones = np.ones(len(aa))

    rk4_trap(ta, aa)

    try:
        while(True):
            print("continuing")
            time.sleep(10)
    except KeyboardInterrupt:
        #sys.exit()
        print("Ending Program.")

