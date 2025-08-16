import numpy as np
import pandas as pd
from scipy.integrate import cumulative_trapezoid
from scipy.signal import find_peaks
from worklab.utils import lowpass_butter
from worklab.imu import push_imu
import copy


# noinspection PyUnboundLocalVariable
def butterfly(data, sfreq: float = 400., start=1.0, inplace=False):
    """
    Calculate butterfly sprint test outcome measures.

    Parameters
    ----------
    data : dict or pd.Series
        processed sessiondata structure or pd.Series with frame data
    sfreq : float
        sampling frequency
    start: float
        minimal value reached after 0.5s to start test, default = 1.0
    inplace : bool
        performs operation inplace

    Returns
    -------
    data : pd.Series
        pd.Series with Butterfly sprint test data
    outcomes_bs : pd.Series
        pd.Series with most important outcome variables of the
        Butterfly sprint test
    """

    if not inplace:
        data = copy.deepcopy(data)
    if type(data) == dict:
        data = data["frame"]
    data['vel'] = lowpass_butter(data["vel"], sfreq=sfreq, cutoff=10)
    m = int(len(data["vel"]) - (0.5 * sfreq))
    for st in range(1, m):
        if data["vel"][st] > 0.1:
            if data["vel"][int(st + (0.5 * sfreq))] > start:
                start_value = st
                break

    data = data[start_value:].reset_index(drop=True)
    data["dist"] -= data['dist'][0]
    data["dist_y"] = cumulative_trapezoid(
        data['vel'] / sfreq * np.sin(np.deg2rad(cumulative_trapezoid(data["rot_vel"] / sfreq, initial=0.0))),
        initial=0.0)
    data["dist_x"] = cumulative_trapezoid(
        data['vel'] / sfreq * np.cos(np.deg2rad(cumulative_trapezoid(data["rot_vel"] / sfreq, initial=0.0))),
        initial=0.0)

    end_point = int(pd.DataFrame(data["dist_x"]).idxmin())
    dist_x_zero = data["dist_x"][end_point:]
    find_end = dist_x_zero[dist_x_zero > 0]
    end_value = find_end.index[0]

    data = data[:end_value]
    data["time"] -= data['time'][0]
    rot_vel_left = data["rot_vel"][data["rot_vel"] > 30]
    rot_vel_right = data["rot_vel"][data["rot_vel"] < -30]

    rot_vel = data['rot_vel'][abs(data['rot_vel']) > 30]
    rot_vel_peaks = rot_vel.reset_index(drop=True)
    rot_vel_high = data['rot_vel'][abs(data['rot_vel']) > 90]

    rot_vel_left_high = data["rot_vel"][data["rot_vel"] > 90]
    rot_vel_right_high = data["rot_vel"][data["rot_vel"] < -90]

    rot_length = (len(rot_vel_left) + len(rot_vel_right)) / len(data['time']) * 100
    rot_high_length = (len(rot_vel_left_high) + len(rot_vel_right_high)) / len(data['time']) * 100
    forward_acc = data['acc'][data['acc'] > 0.1]

    peaks_l, characters = find_peaks(rot_vel_peaks, distance=2 * sfreq, height=90)
    peaks_r, characters = find_peaks(-rot_vel_peaks, distance=2 * sfreq, height=90)
    peaks = np.concatenate((peaks_r, peaks_l))

    peaks_acc_l, characters = find_peaks(data['rot_acc'], distance=2.5 * sfreq, height=150)
    peaks_acc_l = peaks_acc_l[0:4]
    peaks_acc_r, characters = find_peaks(-data['rot_acc'], distance=2.5 * sfreq, height=150)
    peaks_acc = np.concatenate((peaks_acc_l, peaks_acc_r))

    outcomes_bs = dict()
    outcomes_bs['endtime'] = end_value / sfreq
    outcomes_bs['vel_mean'] = np.mean(data["vel"])
    outcomes_bs['vel_peak'] = np.max(data["vel"])
    outcomes_bs['acc_mean'] = np.mean(forward_acc)
    outcomes_bs['rot_vel_mean_right'] = np.mean(rot_vel_right)
    outcomes_bs['rot_vel_mean_left'] = np.mean(rot_vel_left)
    outcomes_bs['rot_vel_mean'] = np.mean(abs(rot_vel))
    outcomes_bs['rot_vel_high_mean_right'] = np.mean(rot_vel_right_high)
    outcomes_bs['rot_vel_high_mean_left'] = np.mean(rot_vel_left_high)
    outcomes_bs['rot_vel_high_mean'] = np.mean(abs(rot_vel_high))
    outcomes_bs['rot_vel_peak_right'] = np.mean(rot_vel_peaks[peaks_r])
    outcomes_bs['rot_vel_peak_left'] = np.mean(rot_vel_peaks[peaks_l])
    outcomes_bs['rot_vel_peak_mean'] = np.mean(abs(rot_vel_peaks)[peaks])
    outcomes_bs['rot_acc_peak_mean'] = np.mean(abs(data['rot_acc'][peaks_acc]))
    outcomes_bs['rot_percentage'] = rot_length
    outcomes_bs['rot_high_percentage'] = rot_high_length
    outcomes_bs['dist'] = np.max(data['dist'])
    outcomes_bs = pd.DataFrame([outcomes_bs])
    outcomes_bs = round(outcomes_bs, 2)
    return data, outcomes_bs


# noinspection PyUnboundLocalVariable
def fandrill(data, sfreq: float = 400., start=1.0, inplace=False):
    """
    Calculate fan drill test outcome measures.

    Parameters
    ----------
    data : dict or pd.Series
        processed sessiondata structure or pd.Series with frame data
    sfreq : float
        sampling frequency
    start: float
        minimal value reached after 0.5s to start test, default = 1.0
    inplace : bool
        performs operation inplace

    Returns
    -------
    data : pd.Series
        pd.Series with Fan drill test data
    outcomes_fd : pd.Series
        pd.Series with most important outcome variables of the
        Fan drill test
    """

    if not inplace:
        data = copy.deepcopy(data)
    if type(data) == dict:
        data = data["frame"]
    data['vel'] = lowpass_butter(data["vel"], sfreq=sfreq, cutoff=10)
    m = int(len(data["vel"]) - (0.5 * sfreq))
    for st in range(1, m):
        if data["vel"][st] > 0.1:
            if data["vel"][int(st + (0.5 * sfreq))] > start:
                start_value = st
                break

    data = data[start_value:].reset_index(drop=True)
    data["dist"] -= data['dist'][0]
    data["dist_y"] = cumulative_trapezoid(
        data['vel'] / sfreq * np.sin(np.deg2rad(cumulative_trapezoid(data["rot_vel"] / sfreq, initial=0.0))),
        initial=0.0)
    data["dist_x"] = cumulative_trapezoid(
        data['vel'] / sfreq * np.cos(np.deg2rad(cumulative_trapezoid(data["rot_vel"] / sfreq, initial=0.0))),
        initial=0.0)

    peaks, _ = find_peaks(data["dist_y"], height=2)
    end_point = peaks[-1]
    dist_y_zero = data["dist_y"][end_point:]
    find_end = dist_y_zero[dist_y_zero < 0]
    end_value = find_end.index[0]

    data = data[:end_value]
    data["time"] -= data['time'][0]
    rot_vel_left = data["rot_vel"][data["rot_vel"] > 30]
    rot_vel_right = data["rot_vel"][data["rot_vel"] < -30]

    rot_vel = data['rot_vel'][abs(data['rot_vel']) > 30]
    rot_vel_peaks = rot_vel.reset_index(drop=True)
    rot_vel_high = data['rot_vel'][abs(data['rot_vel']) > 90]

    rot_vel_left_high = data["rot_vel"][data["rot_vel"] > 90]
    rot_vel_right_high = data["rot_vel"][data["rot_vel"] < -90]

    rot_length = (len(rot_vel_left) + len(rot_vel_right)) / len(data['time']) * 100
    rot_high_length = (len(rot_vel_left_high) + len(rot_vel_right_high)) / len(data['time']) * 100
    forward_acc = data['acc'][data['acc'] > 0.1]

    peaks_l, characters = find_peaks(rot_vel_peaks, distance=2 * sfreq, height=90)
    peaks_r, characters = find_peaks(-rot_vel_peaks, distance=2 * sfreq, height=90)
    peaks = np.concatenate((peaks_r, peaks_l))

    outcomes_fd = dict()
    outcomes_fd['endtime'] = end_value / sfreq
    outcomes_fd['vel_mean'] = np.mean(data["vel"])
    outcomes_fd['vel_peak'] = np.max(data["vel"])
    outcomes_fd['acc_mean'] = np.mean(forward_acc)
    outcomes_fd['rot_vel_mean_right'] = np.mean(rot_vel_right)
    outcomes_fd['rot_vel_mean_left'] = np.mean(rot_vel_left)
    outcomes_fd['rot_vel_mean'] = np.mean(abs(rot_vel))
    outcomes_fd['rot_vel_high_mean_right'] = np.mean(rot_vel_right_high)
    outcomes_fd['rot_vel_high_mean_left'] = np.mean(rot_vel_left_high)
    outcomes_fd['rot_vel_high_mean'] = np.mean(abs(rot_vel_high))
    outcomes_fd['rot_vel_peak_right'] = np.mean(rot_vel_peaks[peaks_r])
    outcomes_fd['rot_vel_peak_left'] = np.mean(rot_vel_peaks[peaks_l])
    outcomes_fd['rot_vel_peak_mean'] = np.mean(abs(rot_vel_peaks)[peaks])
    outcomes_fd['rot_percentage'] = rot_length
    outcomes_fd['rot_high_percentage'] = rot_high_length
    outcomes_fd['dist'] = np.max(data['dist'])
    outcomes_fd = pd.DataFrame([outcomes_fd])
    outcomes_fd = round(outcomes_fd, 2)
    return data, outcomes_fd


# noinspection PyUnboundLocalVariable
def five_o_five(data, sfreq: float = 400., start=1.0, inplace=False):
    """
    Calculate five-o-five sprint test outcome measures.

    Parameters
    ----------
    data : dict or pd.Series
        processed sessiondata structure or pd.Series with frame data
    sfreq : float
        sampling frequency
    start: float
        minimal value reached after 0.5s to start test, default = 1.0
    inplace : bool
        performs operation inplace

    Returns
    -------
    data : pd.Series
        pd.Series with five-o-five sprint test data
    outcomes_fof : pd.Series
        pd.Series with most important outcome variables of the
        five-o-five sprint test
    """

    if not inplace:
        data = copy.deepcopy(data)
    if type(data) == dict:
        data = data["frame"]
    data['vel'] = lowpass_butter(data["vel"], sfreq=sfreq, cutoff=10)
    m = int(len(data["vel"]) - (0.5 * sfreq))
    for st in range(1, m):
        if data["vel"][st] > 0.1:
            if data["vel"][int(st + (0.5 * sfreq))] > start:
                start_value = st
                break

    data = data[start_value:].reset_index(drop=True)
    data["dist"] -= data['dist'][0]
    data["dist_y"] = cumulative_trapezoid(
        data['vel'] / sfreq * np.sin(np.deg2rad(cumulative_trapezoid(data["rot_vel"] / sfreq, initial=0.0))),
        initial=0.0)
    data["dist_x"] = cumulative_trapezoid(
        data['vel'] / sfreq * np.cos(np.deg2rad(cumulative_trapezoid(data["rot_vel"] / sfreq, initial=0.0))),
        initial=0.0)

    data = data[data['dist_x'] > 5].reset_index(drop=True)
    data["dist"] -= data['dist'][0]
    data["time"] -= data['time'][0]

    rot_vel_left = data["rot_vel"][data["rot_vel"] > 30]
    rot_vel_right = data["rot_vel"][data["rot_vel"] < -30]

    rot_vel = data['rot_vel'][abs(data['rot_vel']) > 30]
    rot_vel_peaks = rot_vel.reset_index(drop=True)
    rot_vel_high = data['rot_vel'][abs(data['rot_vel']) > 90]

    rot_vel_left_high = data["rot_vel"][data["rot_vel"] > 90]
    rot_vel_right_high = data["rot_vel"][data["rot_vel"] < -90]

    rot_length = (len(rot_vel_left) + len(rot_vel_right)) / len(data['time']) * 100
    rot_high_length = (len(rot_vel_left_high) + len(rot_vel_right_high)) / len(data['time']) * 100
    forward_acc = data['acc'][data['acc'] > 0.1]

    peaks_l, characters = find_peaks(rot_vel_peaks, distance=2 * sfreq, height=90)
    peaks_r, characters = find_peaks(-rot_vel_peaks, distance=2 * sfreq, height=90)
    peaks = np.concatenate((peaks_r, peaks_l))

    outcomes_fof = dict()
    outcomes_fof['endtime'] = data['time'].iloc[-1]
    outcomes_fof['vel_mean'] = np.mean(data["vel"])
    outcomes_fof['vel_peak'] = np.max(data["vel"])
    outcomes_fof['acc_mean'] = np.mean(forward_acc)
    outcomes_fof['rot_vel_mean'] = np.mean(abs(rot_vel))
    outcomes_fof['rot_vel_high_mean'] = np.mean(abs(rot_vel_high))
    outcomes_fof['rot_vel_peak_mean'] = np.mean(abs(rot_vel_peaks)[peaks])
    outcomes_fof['rot_percentage'] = rot_length
    outcomes_fof['rot_high_percentage'] = rot_high_length
    outcomes_fof['dist'] = np.max(data['dist'])
    outcomes_fof = pd.DataFrame([outcomes_fof])
    outcomes_fof = round(outcomes_fof, 2)

    return data, outcomes_fof


# noinspection PyUnboundLocalVariable
def illinois(data, sfreq: float = 400., start=1.0, inplace=False):
    """
    Calculate illinois test outcome measures.

    Parameters
    ----------
    data : dict or pd.Series
        processed sessiondata structure or pd.Series with frame data
    sfreq : float
        sampling frequency
    start: float
        minimal value reached after 0.5s to start test, default = 1.0
    inplace : bool
        performs operation inplace

    Returns
    -------
    data : pd.Series
        pd.Series with Illinois test data
    outcomes_il : pd.Series
        pd.Series with most important outcome variables of the Illinois test
    """

    if not inplace:
        data = copy.deepcopy(data)
    if type(data) == dict:
        data = data["frame"]
    data['vel'] = lowpass_butter(data["vel"], sfreq=sfreq, cutoff=10)
    m = int(len(data["vel"]) - (0.5 * sfreq))
    for st in range(1, m):
        if data["vel"][st] > 0.1:
            if data["vel"][int(st + (0.5 * sfreq))] > start:
                start_value = st
                break
    data = data[start_value:].reset_index(drop=True)
    data["dist"] -= data['dist'][0]
    data["dist_y"] = cumulative_trapezoid(
        data['vel'] / sfreq * np.sin(np.deg2rad(cumulative_trapezoid(data["rot_vel"] / sfreq, initial=0.0))),
        initial=0.0)
    data["dist_x"] = cumulative_trapezoid(
        data['vel'] / sfreq * np.cos(np.deg2rad(cumulative_trapezoid(data["rot_vel"] / sfreq, initial=0.0))),
        initial=0.0)

    peaks, _ = find_peaks(data["dist_x"])
    end_point = peaks[-1]
    dist_x_zero = data["dist_x"][end_point:]
    find_end = dist_x_zero[dist_x_zero < 0]
    end_value = find_end.index[0]

    data = data[:end_value]
    data["time"] -= data['time'][0]
    data["rot_vel_left"] = data["rot_vel"][data["rot_vel"] > 30]
    data["rot_vel_right"] = data["rot_vel"][data["rot_vel"] < -30]
    rot_vel = data['rot_vel'][abs(data['rot_vel']) > 30]

    rot_vel_high = data['rot_vel'][abs(data['rot_vel']) > 90]
    rot_vel_left_high = data["rot_vel"][data["rot_vel"] > 90]
    rot_vel_right_high = data["rot_vel"][data["rot_vel"] < -90]

    outcomes_il = dict()
    outcomes_il['endtime'] = end_value / sfreq
    outcomes_il['vel_mean'] = np.mean(data["vel"])
    outcomes_il['vel_peak'] = np.max(data["vel"])
    outcomes_il['acc_peak'] = np.max(data["acc"])
    outcomes_il['rot_vel_mean_right'] = np.mean(data["rot_vel_right"])
    outcomes_il['rot_vel_mean_left'] = np.mean(data["rot_vel_left"])
    outcomes_il['rot_vel_mean'] = np.mean(rot_vel)
    outcomes_il['rot_vel_mean_right_high'] = np.mean(rot_vel_right_high)
    outcomes_il['rot_vel_mean_left_high'] = np.mean(rot_vel_left_high)
    outcomes_il['rot_vel_mean_high'] = np.mean(rot_vel_high)
    outcomes_il['rot_vel_peak_right'] = np.min(data["rot_vel_right"])
    outcomes_il['rot_vel_peak_left'] = np.max(data["rot_vel_left"])
    outcomes_il['rot_acc_peak'] = np.max(data["rot_acc"])

    outcomes_il = pd.DataFrame([outcomes_il])
    outcomes_il = round(outcomes_il, 2)
    return data, outcomes_il


# noinspection PyUnboundLocalVariable
def spider(data, sfreq: float = 400., start=1.0, inplace=False):
    """
    Calculate spider outcomes measures.

    Parameters
    ----------
    data : dict or pd.Series
        processed sessiondata structure or pd.Series with frame data
    sfreq : float
        sampling frequency
    start: float
        minimal value reached after 0.5s to start test, default = 1.0
    inplace : bool
        performs operation inplace

    Returns
    -------
    data : pd.Series
        pd.Series with spider test data
    outcomes_spider : pd.Series
        pd.Series with most important outcome variables of the spider test

    """

    if not inplace:
        data = copy.deepcopy(data)
    if type(data) == dict:
        data = data["frame"]

    data['vel'] = lowpass_butter(data["vel"], sfreq=sfreq, cutoff=10)
    m = int(len(data["vel"]) - (0.5 * sfreq))
    for st in range(1, m):
        if data["vel"][st] > 0.1:
            if data["vel"][int(st + (0.5 * sfreq))] > start:
                start_value = st
                break
    data = data[start_value:].reset_index(drop=True)
    data["dist"] -= data['dist'][0]
    data['dist_x'] -= data['dist_x'][0]
    data['dist_y'] -= data['dist_y'][0]

    end_point = int(pd.DataFrame(data["dist_x"]).idxmax())
    dist_x_zero = data["dist_x"][end_point:]
    find_end = dist_x_zero[dist_x_zero < 0]

    end_value = find_end.index[0]

    data = data[:end_value]
    data["time"] -= data['time'][0]
    forward_acc = data['acc'][data['acc'] > 0.1]
    data["rot_vel_left"] = data["rot_vel"][data["rot_vel"] > 30]
    data["rot_vel_right"] = data["rot_vel"][data["rot_vel"] < -30]
    rot_vel = data['rot_vel'][abs(data['rot_vel']) > 30]
    rot_vel_peaks = rot_vel.reset_index(drop=True)

    rot_vel_high = data['rot_vel'][abs(data['rot_vel']) > 90]
    rot_vel_left_high = data["rot_vel"][data["rot_vel"] > 90]
    rot_vel_right_high = data["rot_vel"][data["rot_vel"] < -90]

    peaks_l, characters = find_peaks(rot_vel_peaks, distance=2 * sfreq, height=90)
    peaks_r, characters = find_peaks(-rot_vel_peaks, distance=2 * sfreq, height=90)
    peaks = np.concatenate((peaks_r, peaks_l))

    peaks_acc_l, characters = find_peaks(data['rot_acc'], distance=2.5 * sfreq, height=150)
    peaks_acc_l = peaks_acc_l[0:4]
    peaks_acc_r, characters = find_peaks(-data['rot_acc'], distance=2.5 * sfreq, height=150)

    peaks_acc = np.concatenate((peaks_acc_l, peaks_acc_r))

    outcomes_spider = dict()
    if end_value == -1:
        outcomes_spider['endtime'] = np.nan
    else:
        outcomes_spider['endtime'] = end_value / sfreq
    outcomes_spider['vel_mean'] = np.mean(data["vel"])
    outcomes_spider['vel_peak'] = np.max(data["vel"])
    outcomes_spider['acc_mean'] = np.mean(forward_acc)
    outcomes_spider['rot_vel_mean_right'] = np.mean(data["rot_vel_right"])
    outcomes_spider['rot_vel_mean_left'] = np.mean(data["rot_vel_left"])
    outcomes_spider['rot_vel_mean'] = np.mean(abs(rot_vel))
    outcomes_spider['rot_vel_mean_right_high'] = np.mean(rot_vel_right_high)
    outcomes_spider['rot_vel_mean_left_high'] = np.mean(rot_vel_left_high)
    outcomes_spider['rot_vel_mean_high'] = np.mean(abs(rot_vel_high))
    outcomes_spider['rot_vel_peak_right'] = np.mean(rot_vel_peaks[peaks_r])
    outcomes_spider['rot_vel_peak_left'] = np.mean(rot_vel_peaks[peaks_l])
    outcomes_spider['rot_vel_peak_mean'] = np.mean(abs(rot_vel_peaks)[peaks])
    outcomes_spider['rot_acc_peak_mean'] = np.mean(abs(data['rot_acc'][peaks_acc]))

    outcomes_spider = pd.DataFrame([outcomes_spider])
    outcomes_spider = round(outcomes_spider, 2)
    return data, outcomes_spider


# noinspection PyUnboundLocalVariable
def sprint_10m(data, sfreq: float = 400., start=1.0, acc_frame=True,
               inplace=False):
    """
    Calculate 10m sprint test outcomes measures.

    Parameters
    ----------
    data : dict or pd.Series
        processed sessiondata structure or pd.Series with frame data
    sfreq : float
        sampling frequency
    start: float
        minimal value reached after 0.5s to start test, default = 1.0
    acc_frame: boolean
        default is True, acceleration from frame used
        if changed to False, acceleration from velocity wheels is used
    inplace : bool
        performs operation inplace

    Returns
    -------
    data : pd.Series
        pd.Series with 10m sprint data
    outcomes_sprint : pd.Series
        pd.Series with most important outcome variables of the 10m sprint test
    """

    if not inplace:
        data = copy.deepcopy(data)
    if type(data) == dict:
        data = data["frame"]
    if acc_frame is False:
        data['acc'] = data['acc_wheel']
    data['vel'] = lowpass_butter(data["vel"], sfreq=sfreq, cutoff=10)
    m = int(len(data["vel"]) - (0.5 * sfreq))
    for st in range(1, m):
        if data["vel"][st] > 0.1:
            if data["vel"][int(st + (0.5 * sfreq))] > start:
                start_value = st
                break
    data = data[start_value:].reset_index(drop=True)
    data["dist_y"] = cumulative_trapezoid(
        data['vel'] / sfreq * np.sin(np.deg2rad(cumulative_trapezoid(data["rot_vel"] / sfreq, initial=0.0))),
        initial=0.0)
    data["dist_x"] = cumulative_trapezoid(
        data['vel'] / sfreq * np.cos(np.deg2rad(cumulative_trapezoid(data["rot_vel"] / sfreq, initial=0.0))),
        initial=0.0)
    data["dist"] -= data['dist'][0]

    n10 = int(len(data["dist_x"]))
    for val2 in range(0, n10):
        if data["dist_x"][val2] > 2:
            two_value = val2
            break
    for val5 in range(0, n10):
        if data["dist_x"][val5] > 5:
            five_value = val5
            break
    for val10 in range(0, n10):
        if data["dist_x"][val10] > 10:
            end_value = val10
            break

    data = data[:end_value]
    data["time"] -= data['time'][0]
    push_ind, acc_filt, n_pushes, cycle_time, push_freq = push_imu(
        data["acc"], sfreq=sfreq)
    pos_acc = data['acc'][data['acc'] > 0.1]
    neg_acc = data['acc'][data['acc'] < -0.1]

    outcomes_sprint = dict()
    outcomes_sprint['time_2m'] = two_value / sfreq
    outcomes_sprint['time_5m'] = five_value / sfreq
    outcomes_sprint['time_10m'] = end_value / sfreq
    outcomes_sprint['vel_2m_peak'] = np.max(data["vel"][:two_value])
    outcomes_sprint['vel_5m_peak'] = np.max(data["vel"][two_value:five_value])
    outcomes_sprint['vel_10m_peak'] = np.max(data["vel"][five_value:end_value])
    outcomes_sprint['pos_vel_peak'] = data["dist_x"][data["vel"].idxmax()]
    outcomes_sprint['vel_mean'] = np.mean(data["vel"])
    outcomes_sprint['vel_peak'] = np.max(data["vel"])
    outcomes_sprint['acc_peak'] = np.max(data["acc"])
    outcomes_sprint['acc_mean'] = np.mean(pos_acc)
    outcomes_sprint['dec_mean'] = np.mean(neg_acc)
    outcomes_sprint['pos_acc_peak'] = data["dist_x"][data["acc"].idxmax()]
    outcomes_sprint['n_pushes'] = n_pushes
    outcomes_sprint['dist_push1'] = data["dist_x"][push_ind[0]]
    outcomes_sprint['dist_push2'] = data["dist_x"][push_ind[1]]
    outcomes_sprint['dist_push3'] = data["dist_x"][push_ind[2]]
    outcomes_sprint['cycle_time'] = np.mean(cycle_time[0])

    outcomes_sprint = pd.DataFrame([outcomes_sprint])
    outcomes_sprint = round(outcomes_sprint, 2)
    return data, outcomes_sprint


# noinspection PyUnboundLocalVariable
def sprint_20m(data, sfreq: float = 400., start=1.0, acc_frame=True,
               inplace=False):
    """
    Calculate 20m sprint outcomes measures.

    Parameters
    ----------
    data : dict or pd.Series
        processed sessiondata structure or pd.Series with frame data
    sfreq : float
        sampling frequency
    start: float
        minimal value reached after 0.5s to start test, default = 1.0
    acc_frame: boolean
        default is True, acceleration from frame used
        if changed to False, acceleration from velocity wheels is used
    inplace : bool
        performs operation inplace

    Returns
    -------
    data : pd.Series
        pd.Series with 20m sprint data
    outcomes_sprint : pd.Series
        pd.Series with most important outcome variables of the 20m sprint test
    """
    if not inplace:
        data = copy.deepcopy(data)
    if type(data) == dict:
        data = data["frame"]
    if acc_frame is False:
        data['acc'] = data['acc_wheel']
    data['vel'] = lowpass_butter(data["vel"], sfreq=sfreq, cutoff=10)
    m = int(len(data["vel"]) - (0.5 * sfreq))
    for st in range(1, m):
        if data["vel"][st] > 0.1:
            if data["vel"][int(st + (0.5 * sfreq))] > start:
                start_value = st
                break
    data = data[start_value:].reset_index(drop=True)
    data["dist_y"] = cumulative_trapezoid(
        data['vel'] / sfreq * np.sin(np.deg2rad(cumulative_trapezoid(data["rot_vel"] / sfreq, initial=0.0))),
        initial=0.0)
    data["dist_x"] = cumulative_trapezoid(
        data['vel'] / sfreq * np.cos(np.deg2rad(cumulative_trapezoid(data["rot_vel"] / sfreq, initial=0.0))),
        initial=0.0)
    data['dist'] -= data['dist'][0]

    n20 = int(len(data["dist_x"]))
    for val5 in range(0, n20):
        if data["dist_x"][val5] > 5:
            five_value = val5
            break
    for val10 in range(0, n20):
        if data["dist_x"][val10] > 10:
            ten_value = val10
            break
    for val20 in range(0, n20):
        if data["dist_x"][val20] > 20:
            end_value = val20
            break

    data = data[:end_value]
    data["time"] -= data['time'][0]
    push_ind, acc_filt, n_pushes, cycle_time, push_freq = push_imu(
        data["acc"], sfreq=sfreq)

    pos_acc = data['acc'][data['acc'] > 0.1]
    neg_acc = data['acc'][data['acc'] < -0.1]

    outcomes_sprint = dict()
    outcomes_sprint['time_5m'] = five_value / sfreq
    outcomes_sprint['time_10m'] = ten_value / sfreq
    outcomes_sprint['time_20m'] = end_value / sfreq
    outcomes_sprint['vel_5m_peak'] = np.max(data["vel"][:five_value])
    outcomes_sprint['vel_10m_peak'] = np.max(data["vel"][five_value:ten_value])
    outcomes_sprint['vel_20m_peak'] = np.max(data["vel"][ten_value:end_value])
    outcomes_sprint['pos_vel_peak'] = data["dist_x"][data["vel"].idxmax()]
    outcomes_sprint['vel_mean'] = np.mean(data["vel"])
    outcomes_sprint['vel_peak'] = np.max(data["vel"])
    outcomes_sprint['acc_peak'] = np.max(data["acc"])
    outcomes_sprint['acc_mean'] = np.mean(pos_acc)
    outcomes_sprint['dec_mean'] = np.mean(neg_acc)
    outcomes_sprint['pos_acc_peak'] = data["dist_x"][data["acc"].idxmax()]
    outcomes_sprint['n_pushes'] = n_pushes
    outcomes_sprint['dist_push1'] = data["dist_x"][push_ind[0]]
    outcomes_sprint['dist_push2'] = data["dist_x"][push_ind[1]]
    outcomes_sprint['dist_push3'] = data["dist_x"][push_ind[2]]
    outcomes_sprint['cycle_time'] = np.mean(cycle_time[0])

    outcomes_sprint = pd.DataFrame([outcomes_sprint])
    outcomes_sprint = round(outcomes_sprint, 2)
    return data, outcomes_sprint
