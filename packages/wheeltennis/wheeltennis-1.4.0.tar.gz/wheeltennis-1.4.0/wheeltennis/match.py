import pandas as pd
import numpy as np
from scipy.signal import find_peaks
from scipy.integrate import cumulative_trapezoid


def vel_var(sessiondata):
    """
    Calculate velocity variables of a wheelchair tennis match

    Parameters
    ----------
    sessiondata : dict
        processed sessiondata structure

    Returns
    -------
    outcomes_vel : pd.Series
        pd.Series with all velocity variables

    """
    # Cut the dataset in forward and reverse velocity
    forward = sessiondata['frame'][(sessiondata['frame']['vel']) > 0.1].reset_index(drop=True)
    reverse = sessiondata['frame'][(sessiondata['frame']['vel']) < -0.1].reset_index(drop=True)

    mean_vel = np.mean(forward['vel'])

    hsa = forward[forward['vel'] > 2]
    n_hsa = (hsa['time'].diff() > 2).sum()
    n_hsa_pm = (n_hsa / ((len(forward) + len(reverse)) / 100)) * 60

    hsa3 = forward[forward['vel'] > 3]
    n_hsa3 = (hsa3['time'].diff() > 2).sum()
    n_hsa3_pm = (n_hsa3 / ((len(forward) + len(reverse)) / 100)) * 60

    peaks, _ = find_peaks(forward['vel'], prominence=0.5, distance=50, width=30, height=2)
    peaks_rev, _ = find_peaks(-reverse['vel'], prominence=0.5, distance=50, width=30, height=1)
    vel_peaks = forward['vel'][peaks]
    vel_peaks = vel_peaks.sort_values(ascending=False)
    rev_vel_peaks = reverse['vel'][peaks_rev]
    rev_vel_peaks.sort_values(ascending=True)

    mean_vel_best5 = np.mean(vel_peaks.head(5))
    peak_vel = np.max(vel_peaks)
    peak_rev_vel = np.min(rev_vel_peaks)
    mean_rev_vel = np.mean(reverse['vel'])

    outcomes_vel = pd.DataFrame([])
    outcomes_vel['vel_mean'] = [mean_vel]
    outcomes_vel['vel_peak'] = peak_vel
    outcomes_vel['rev_vel_mean'] = mean_rev_vel
    outcomes_vel['rev_vel_peak'] = peak_rev_vel
    outcomes_vel['num_high_speed_activations_pm'] = n_hsa_pm
    outcomes_vel['num_high_speed_activations_3_pm'] = n_hsa3_pm
    outcomes_vel['mean_best_5_vel'] = mean_vel_best5
    outcomes_vel = round(outcomes_vel, 2)

    return outcomes_vel


def acc_var(sessiondata):
    """
    Calculate acceleration variables of a wheelchair tennis match

    Parameters
    ----------
    sessiondata : dict
        processed sessiondata structure

    Returns
    -------
    outcomes_acc : pd.Series
        pd.Series with all acceleration variables

    """
    # Cut the dataset in forward, reverse velocity and positive accelerations
    forward = sessiondata['frame'][(sessiondata['frame']['vel']) > 0.1].reset_index(drop=True)
    forward['acc'] = forward['acc_wheel']
    forward_acc = forward[(forward['acc']) > 0.1].reset_index(drop=True)
    forward_dec = forward[(forward['acc']) < -0.1].reset_index(drop=True)

    mean_acc = np.mean(forward_acc['acc'])
    mean_dec = np.mean(forward_dec['acc'])

    peak_acc = np.max(forward_acc['acc'])
    peak_dec = np.min(forward_dec['acc'])

    outcomes_acc = pd.DataFrame([])
    outcomes_acc['acc_mean'] = [mean_acc]
    outcomes_acc['dec_mean'] = mean_dec
    outcomes_acc['acc_peak'] = peak_acc
    outcomes_acc['dec_peak'] = peak_dec

    outcomes_acc = round(outcomes_acc, 2)

    return outcomes_acc


def rot_vel_var(sessiondata, side: bool = True, subsets: bool = True):
    """
    Calculate rotational velocity variables of a wheelchair tennis match

    Parameters
    ----------
    sessiondata : dict
        processed sessiondata structure
    side : bool
        if set to True left side is analysed
        if set to False right side is analysed
    subsets : bool
        if set to True subsets are analysed (curve 1-2 and turns 1-2)
            turn 1: velocities -0.5 - 0.5 m/s
            turn 2: velocties -1.5 - 1.5 m/s
            curve 1: velocities 1 - 2 m/s
            curve 2: velocties > 1.5 m/s
        if set to False no subsets are analysed

    Returns
    -------
    outcomes_rot_vel : pd.Series
        pd.Series with all rotational velocity variables

    """
    # Cut the dataset in part where there was movement
    move = sessiondata['frame'][(sessiondata['frame']['vel'] < -0.1) | (sessiondata['frame']['vel'] > 0.1)].reset_index(
        drop=True)

    if side is True:  # left
        rotate = move[move['rot_vel'] > 10].reset_index(drop=True)
        side = 'left'
    else:  # right
        rotate = move[move['rot_vel'] < -10].reset_index(drop=True)
        rotate['rot_vel'] = -rotate['rot_vel']
        side = 'right'

    turn1 = rotate[(rotate['vel'] > -0.5) & (rotate['vel'] < 0.5)].reset_index(drop=True)
    turn2 = rotate[(rotate['vel'] > -1.5) & (rotate['vel'] < 1.5)].reset_index(drop=True)
    curve1 = rotate[(rotate['vel'] > 1) & (rotate['vel'] < 2)].reset_index(drop=True)
    curve2 = rotate[rotate['vel'] > 1.5].reset_index(drop=True)

    moves = [rotate, turn1, turn2, curve1, curve2]
    if subsets is True:
        moves_keys = ['all', 'turn1', 'turn2', 'curve1', 'curve2']
    else:
        moves_keys = ['all']
    outcomes_rot_vel = pd.DataFrame([])

    for movement, keys in zip(moves, moves_keys):
        peaks, _ = find_peaks(movement['rot_vel'], prominence=50, height=90, width=20, distance=50)
        rot_vel_peaks = movement['rot_vel'][peaks]
        rot_vel_peaks = rot_vel_peaks.sort_values(ascending=False)
        mean_rot_vel = np.mean(movement['rot_vel'])
        mean_rot_vel_best5 = np.mean(rot_vel_peaks.head(5))
        peak_rot_vel = np.max(rot_vel_peaks)

        outcomes_rot_vel[keys + '_mean_rot_vel_' + side] = [mean_rot_vel]
        outcomes_rot_vel[keys + '_peak_rot_vel_' + side] = [peak_rot_vel]
        outcomes_rot_vel[keys + '_mean_best5_rot_vel_' + side] = [mean_rot_vel_best5]

    outcomes_rot_vel = round(outcomes_rot_vel, 2)

    return outcomes_rot_vel


def rot_acc_var(sessiondata, side: bool = True, subsets: bool = True):
    """
    Calculate rotational acceleration variables of a wheelchair tennis match

    Parameters
    ----------
    sessiondata : dict
        processed sessiondata structure
    side : bool
        if set to True left side is analysed
        if set to False right side is analysed
    subsets : bool
        if set to True subsets are analysed (curve 1-2 and turns 1-2)
            turn 1: velocities -0.5 - 0.5 m/s
            turn 2: velocties -1.5 - 1.5 m/s
            curve 1: velocities 1 - 2 m/s
            curve 2: velocties > 1.5 m/s
        if set to False no subsets are analysed
    Returns
    -------
    outcomes_rot_acc : pd.Series
        pd.Series with all rotational acceleration variables

    """
    # Cut the dataset in part where there was movement
    move = sessiondata['frame'][(sessiondata['frame']['vel'] < -0.1) | (sessiondata['frame']['vel'] > 0.1)].reset_index(
        drop=True)

    if side is True:  # left
        rotate = move[move['rot_vel'] > 10].reset_index(drop=True)
        rotate_acc = rotate[rotate['rot_acc'] > 10].reset_index(drop=True)
        side = 'left'
    else:  # right
        rotate = move[move['rot_vel'] < -10].reset_index(drop=True)
        rotate_acc = rotate[rotate['rot_acc'] > 10].reset_index(drop=True)
        side = 'right'

    turn1 = rotate_acc[(rotate_acc['vel'] > -0.5) & (rotate_acc['vel'] < 0.5)].reset_index(drop=True)
    turn2 = rotate_acc[(rotate_acc['vel'] > -1.5) & (rotate_acc['vel'] < 1.5)].reset_index(drop=True)
    curve1 = rotate_acc[(rotate_acc['vel'] > 1) & (rotate_acc['vel'] < 2)].reset_index(drop=True)
    curve2 = rotate_acc[rotate_acc['vel'] > 1.5].reset_index(drop=True)

    moves = [rotate_acc, turn1, turn2, curve1, curve2]
    if subsets is True:
        moves_keys = ['all', 'turn1', 'turn2', 'curve1', 'curve2']
    else:
        moves_keys = ['all']
    outcomes_rot_acc = pd.DataFrame([])

    for movement, keys in zip(moves, moves_keys):
        mean_rot_acc = np.mean(movement['rot_acc'])
        outcomes_rot_acc[keys + '_mean_rot_acc_' + side] = [mean_rot_acc]
    outcomes_rot_acc = round(outcomes_rot_acc, 2)

    return outcomes_rot_acc


def gen_var(sessiondata):
    """
    Calculate general variables of a wheelchair tennis match

    Parameters
    ----------
    sessiondata : dict
        processed sessiondata structure

    Returns
    -------
    outcomes_gen : pd.Series
        pd.Series with all general variables (time, distance, ratios)

    """
    # Cut the dataset in forward and reverse velocity and the resting part
    sfreq = 1 / sessiondata['frame']['time'].diff().mean()
    forward = sessiondata['frame'][(sessiondata['frame']['vel']) > 0.1].reset_index(drop=True)
    reverse = sessiondata['frame'][(sessiondata['frame']['vel']) < -0.1].reset_index(drop=True)
    rest = sessiondata['frame'][(sessiondata['frame']['vel'] < 0.1) & (sessiondata['frame']['vel'] > -0.1)].reset_index(
        drop=True)

    work = len(forward['time']) + len(reverse['time'])
    rest = len(rest['time'])
    total = len(sessiondata['frame']['time'])

    ratio_forward = len(forward['time']) / work * 100
    ratio_reverse = len(reverse['time']) / work * 100
    for_rev = ratio_forward / ratio_reverse
    forward['dist'] = cumulative_trapezoid(forward["vel"] / sfreq, initial=0.0)
    reverse['dist'] = cumulative_trapezoid(reverse["vel"] / sfreq, initial=0.0)

    ratio_work = work / total * 100
    ratio_rest = rest / total * 100
    work_rest = ratio_work / ratio_rest

    tot_duration_min = total / (sfreq * 60)
    tot_duration_active = work / (sfreq * 60)

    tot_distance = max(sessiondata['frame']['dist'])
    tot_forward_distance = max(forward['dist'])
    tot_reverse_distance = max(abs(reverse['dist']))
    distance_pm = tot_distance / tot_duration_active
    distance_forward_pm = tot_forward_distance / tot_duration_active
    distance_reverse_pm = tot_reverse_distance / tot_duration_active

    outcomes_gen = pd.DataFrame([])
    outcomes_gen['ratio_forward'] = [ratio_forward]
    outcomes_gen['ratio_reverse'] = ratio_reverse
    outcomes_gen['forward_reverse'] = for_rev
    outcomes_gen['ratio_work'] = ratio_work
    outcomes_gen['ratio_rest'] = ratio_rest
    outcomes_gen['work_rest'] = work_rest
    outcomes_gen['tot_duration_active_min'] = tot_duration_active
    outcomes_gen['tot_duration'] = tot_duration_min
    outcomes_gen['tot_distance'] = tot_distance
    outcomes_gen['distance_forward'] = tot_forward_distance
    outcomes_gen['distance_reverse'] = tot_reverse_distance
    outcomes_gen['distance_permin'] = distance_pm
    outcomes_gen['distance_forward_permin'] = distance_forward_pm
    outcomes_gen['distance_reverse_permin'] = distance_reverse_pm
    outcomes_gen = round(outcomes_gen, 2)

    return outcomes_gen


def speed_zones(sessiondata, percentage=False, top_speed=0, high_zone=True):
    """
    Calculate speed zones during matches

    Parameters
    ----------
    sessiondata : dict
        processed sessiondata structure
    percentage : boolean
        if set to True, personalised percentages are used
    top_speed : int
        players top speed in m/s
    high_zone : boolean
        if set to True, there will be an additional high speed zone

    Returns
    -------
    speed_zone_outcomes_row: pd.DataFrame
        outcomes of speed zones in rows

    """
    sfreq = 1 / sessiondata['frame']['time'].diff().mean()
    speed_zone_outcomes_all = pd.DataFrame([])
    speed_zone_outcomes_disp = pd.DataFrame([])
    speed_zone_outcomes_per = pd.DataFrame([])
    move = sessiondata['frame'][
        (sessiondata['frame']['vel'] > 0.1) | (sessiondata['frame']['vel'] < -0.1)]

    if percentage is True:  # and math.isnan(top_speed) is False
        if high_zone is True:
            zones = [-np.inf, 0, 0.2 * top_speed, 0.5 * top_speed, 0.8 * top_speed,
                     0.95 * top_speed]
            zones2 = [0, 0.2 * top_speed, 0.5 * top_speed, 0.8 * top_speed, 0.95 * top_speed,
                      np.inf]
            zone_names = ['-inf', '0', '20%', '50%', '80%', '95%']
            zone_names2 = ['0', '20%', '50%', '80%', '95%', 'inf']
        else:
            zones = [-np.inf, 0, 0.2 * top_speed, 0.5 * top_speed, 0.8 * top_speed]
            zones2 = [0, 0.2 * top_speed, 0.5 * top_speed, 0.8 * top_speed, np.inf]
            zone_names = ['-inf', '0', '20%', '50%', '80%']
            zone_names2 = ['0', '20%', '50%', '80%', 'inf']
    else:
        if high_zone is True:
            zones = [-np.inf, 0, 1, 2, 3, 4]
            zones2 = [0, 1, 2, 3, 4, np.inf]
            zone_names = ['-inf', '0', '1', '2', '3', '4']
            zone_names2 = ['0', '1', '2', '3', '4', 'inf']
        else:
            zones = [-np.inf, 0, 1, 2, 3]
            zones2 = [0, 1, 2, 3, np.inf]
            zone_names = ['-inf', '0', '1', '2', '3']
            zone_names2 = ['0', '1', '2', '3', 'inf']

    for zone, zone2, zone_name, zone_name2 in zip(zones, zones2, zone_names, zone_names2):
        zone_ind = ((move['vel'] >= zone) & (move['vel'] < zone2))
        move_zone = move[zone_ind]
        if len(move_zone) > 0:
            per_speed_zone = (len(move_zone) / len(move) * 100)
            frame_dist = cumulative_trapezoid(move_zone['vel'], initial=0.0) / sfreq
            disp_speed_zone = (max(abs(frame_dist)))
            freq_speed_zone = ((move_zone['time'].diff() > 0.5).sum())
        else:
            per_speed_zone = 0
            disp_speed_zone = 0
            freq_speed_zone = 0
        outcomes = pd.DataFrame([[per_speed_zone, disp_speed_zone, freq_speed_zone]],
                                columns=['per_speed_zone', 'disp_speed_zone', 'freq_speed_zone'],
                                index=[zone_name + ' - ' + zone_name2])
        outcomes_per = pd.DataFrame([per_speed_zone], columns=['per_speed_zone_' + zone_name + '-' + zone_name2])
        outcomes_disp = pd.DataFrame([disp_speed_zone], columns=['disp_speed_zone_' + zone_name + '-' + zone_name2])

        speed_zone_outcomes_all = pd.concat([speed_zone_outcomes_all, outcomes])
        speed_zone_outcomes_disp = pd.concat([speed_zone_outcomes_disp, outcomes_disp], axis=1)
        speed_zone_outcomes_per = pd.concat([speed_zone_outcomes_per, outcomes_per], axis=1)

    speed_zone_outcomes_row = pd.concat([speed_zone_outcomes_disp, speed_zone_outcomes_per], axis=1)
    speed_zone_outcomes_row = round(speed_zone_outcomes_row, 2)

    return speed_zone_outcomes_row


def acc_zones(sessiondata):
    """
    Calculate acceleration zones during matches

    Parameters
    ----------
    sessiondata : dict
        processed sessiondata structure

    Returns
    -------
    acc_zone_outcomes: pd.DataFrame
        outcomes of acceleration zones

    """
    sfreq = 1 / sessiondata['frame']['time'].diff().mean()
    acc_zone_outcomes = pd.DataFrame([])
    move = sessiondata['frame'][
        (sessiondata['frame']['vel'] > 0.1) | (sessiondata['frame']['vel'] < -0.1)]
    zones = [-np.inf, 0, 1, 1.5, 2, 2.5, 5]
    zones2 = [0, 1, 1.5, 2, 2.5, 5, np.inf]

    for zone, zone2 in zip(zones, zones2):
        zone_ind = ((move['acc'] >= zone) & (move['acc'] < zone2))
        move_zone = move[zone_ind]
        if len(move_zone) > 0:
            per_acc_zone = (len(move_zone) / len(move) * 100)
            frame_dist = cumulative_trapezoid(move_zone['vel'], initial=0.0) / sfreq
            disp_acc_zone = (max(abs(frame_dist)))
            freq_acc_zone = ((move_zone['time'].diff() > 0.1).sum())
        else:
            per_acc_zone = 0
            disp_acc_zone = 0
            freq_acc_zone = 0

        outcomes = pd.DataFrame([[per_acc_zone, disp_acc_zone, freq_acc_zone]],
                                columns=['per_acc_zone', 'disp_acc_zone', 'freq_acc_zone'],
                                index=[str(round(zone, 2)) + ' - ' + str(round(zone2, 2))])
        acc_zone_outcomes = pd.concat([acc_zone_outcomes, outcomes])
    acc_zone_outcomes = round(acc_zone_outcomes, 2)

    return acc_zone_outcomes


def turns(sessiondata):
    """
    Calculate high speed rotations

    Parameters
    ----------
    sessiondata : dict
        processed sessiondata structure

    Returns
    -------
    turns: pd.DataFrame
        number of high speed turns (> 120 deg/s) in both directions

    """
    sfreq = 1 / sessiondata['frame']['time'].diff().mean()
    move = sessiondata['frame'][(sessiondata['frame']['vel'] > 0.1) | (sessiondata['frame']['vel'] < -0.1)]

    left_rotate = move[move['rot_vel'] > 120]
    right_rotate = move[move['rot_vel'] < -120]

    left_turns = (left_rotate['time'].diff() > 0.5).sum()
    left_turns_pm = (left_turns / (len(move) / sfreq)) * 60
    right_turns = (right_rotate['time'].diff() > 0.5).sum()
    right_turns_pm = (right_turns / (len(move) / sfreq)) * 60

    turns = pd.DataFrame([])
    turns['left_turns'] = [left_turns]
    turns['right_turns'] = right_turns
    turns['left_turns_pm'] = left_turns_pm
    turns['right_turns_pm'] = right_turns_pm
    turns = round(turns, 2)

    return turns


def rot_vel_zones(sessiondata):
    """
    Calculate rotational zones during matches

    Parameters
    ----------
    sessiondata : dict
        processed sessiondata structure

    Returns
    -------
    rot_zone_outcomes_row: pd.DataFrame
        outcomes of rotational zones in rows

    """
    sfreq = 1 / sessiondata['frame']['time'].diff().mean()
    rot_zone_outcomes_all = pd.DataFrame([])
    rot_zone_outcomes_disp = pd.DataFrame([])
    rot_zone_outcomes_per = pd.DataFrame([])

    move = sessiondata['frame'][
        (sessiondata['frame']['vel'] > 0.1) | (sessiondata['frame']['vel'] < -0.1)]
    rotate = move[abs(move['rot_vel']) > 10].reset_index(drop=True)

    zones = [-np.inf, -120, -60, 0, 60, 120]
    zones2 = [-120, -60, 0, 60, 120, np.inf]

    for zone, zone2 in zip(zones, zones2):
        zone_ind = ((rotate['rot_vel'] >= zone) & (rotate['rot_vel'] < zone2))
        move_zone = rotate[zone_ind]
        if len(move_zone) > 0:
            per_rot_vel_zone = (len(move_zone) / len(rotate) * 100)
            frame_dist = cumulative_trapezoid(move_zone['vel'], initial=0.0) / sfreq
            disp_rot_vel_zone = (max(abs(frame_dist)))
            freq_rot_vel_zone = ((move_zone['time'].diff() > 0.1).sum())
        else:
            per_rot_vel_zone = 0
            disp_rot_vel_zone = 0
            freq_rot_vel_zone = 0

        outcomes = pd.DataFrame([[per_rot_vel_zone, disp_rot_vel_zone, freq_rot_vel_zone]],
                                columns=['per_rot_vel_zone', 'disp_rot_vel_zone', 'freq_rot_vel_zone'],
                                index=[str(round(zone, 2)) + ' - ' + str(round(zone2, 2))])
        outcomes_per = pd.DataFrame([per_rot_vel_zone],
                                    columns=['per_rot_vel_zone_' + str(round(zone, 2)) + ' - ' + str(round(zone2, 2))])
        outcomes_disp = pd.DataFrame([disp_rot_vel_zone], columns=[
            'disp_rot_vel_zone_' + str(round(zone, 2)) + ' - ' + str(round(zone2, 2))])

        rot_zone_outcomes_all = pd.concat([rot_zone_outcomes_all, outcomes])
        rot_zone_outcomes_disp = pd.concat([rot_zone_outcomes_disp, outcomes_disp], axis=1)
        rot_zone_outcomes_per = pd.concat([rot_zone_outcomes_per, outcomes_per], axis=1)

    rot_zone_outcomes_row = pd.concat([rot_zone_outcomes_disp, rot_zone_outcomes_per], axis=1)
    rot_zone_outcomes_row = round(rot_zone_outcomes_row, 2)

    return rot_zone_outcomes_row


def key_var(sessiondata):
    """
    Calculate key variables of a wheelchair tennis match, based on
    Rietveld, T., Vegter, R. J., van der Slikke, R. M., Hoekstra, A. E., van der Woude, L. H., & de Groot, S. (2023).
    Six inertial measurement unit-based components describe wheelchair mobility performance
    during wheelchair tennis matches. Sports Engineering, 26(1), 32.:
    ...

    Parameters
    ----------
    sessiondata : dict
        processed sessiondata structure

    Returns
    -------
    outcomes_key : pd.Series
        pd.Series with all key variables

    """
    # Cut the dataset in forward and reverse velocity
    forward = sessiondata['frame'][(sessiondata['frame']['vel']) > 0.1].reset_index(drop=True)
    reverse = sessiondata['frame'][(sessiondata['frame']['vel']) < -0.1].reset_index(drop=True)
    move = sessiondata['frame'][(sessiondata['frame']['vel'] < -0.1) |
                                (sessiondata['frame']['vel'] > 0.1)].reset_index(drop=True)
    forward['acc'] = forward['acc_wheel']
    forward_acc = forward[(forward['acc']) > 0.1].reset_index(drop=True)
    mean_acc = np.mean(forward_acc['acc'])

    hsa = forward[forward['vel'] > 2]
    n_hsa = (hsa['time'].diff() > 2).sum()
    n_hsa_pm = (n_hsa / ((len(forward) + len(reverse)) / 100)) * 60

    peaks, _ = find_peaks(forward['vel'], height=2.5, width=100, distance=100)
    vel_peaks = forward['vel'][peaks]
    vel_peaks = vel_peaks.sort_values(ascending=False)
    mean_vel_best5 = np.mean(vel_peaks.head(5))

    peak_rev_vel = -np.min(reverse['vel'])

    sides = ['left', 'right']
    outcomes_rot_vel = pd.DataFrame([])

    for side in sides:
        if side == 'left':
            rotate = move[move['rot_vel'] > 10].reset_index(drop=True)
            side = 'left'
        else:  # right
            rotate = move[move['rot_vel'] < -10].reset_index(drop=True)
            rotate['rot_vel'] = -rotate['rot_vel']
            side = 'right'

        turn1 = rotate[(rotate['vel'] > -0.5) & (rotate['vel'] < 0.5)].reset_index(drop=True)
        curve2 = rotate[rotate['vel'] > 1.5].reset_index(drop=True)

        moves = [turn1, curve2]
        moves_keys = ['turn1', 'curve2']

        for movement, keys in zip(moves, moves_keys):
            peaks, _ = find_peaks(movement['rot_vel'], prominence=50, height=90, width=20, distance=50)
            rot_vel_peaks = movement['rot_vel'][peaks]
            rot_vel_peaks = rot_vel_peaks.sort_values(ascending=False)
            mean_rot_vel = np.mean(movement['rot_vel'])
            mean_rot_vel_best5 = np.mean(rot_vel_peaks.head(5))
            peak_rot_vel = np.max(rot_vel_peaks)

            outcomes_rot_vel[keys + '_mean_rot_vel_' + side] = [mean_rot_vel]
            outcomes_rot_vel[keys + '_peak_rot_vel_' + side] = [peak_rot_vel]
            outcomes_rot_vel[keys + '_mean_best5_rot_vel_' + side] = [mean_rot_vel_best5]

    outcomes_key = pd.DataFrame([])
    outcomes_key['rot_vel_curve_right'] = outcomes_rot_vel['curve2_mean_best5_rot_vel_right']
    outcomes_key['rot_vel_turn_right'] = outcomes_rot_vel['turn1_mean_rot_vel_right']
    outcomes_key['num_high_speed_activations_pm'] = n_hsa_pm
    outcomes_key['acc_mean'] = mean_acc
    outcomes_key['rot_vel_turn_left'] = outcomes_rot_vel['turn1_mean_rot_vel_left']
    outcomes_key['rot_vel_curve_left'] = outcomes_rot_vel['curve2_mean_best5_rot_vel_left']
    outcomes_key['rev_vel_peak'] = peak_rev_vel
    outcomes_key['mean_best_5_vel'] = mean_vel_best5
    outcomes_key = round(outcomes_key, 2)

    return outcomes_key
