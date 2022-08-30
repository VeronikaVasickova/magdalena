import numpy as np
import scipy.interpolate
import get_heat
import json
import matplotlib.pyplot as plt
from scipy.stats import norm
from scipy import optimize
import fills_times
import os

#calculate the total heatload as simulated
def get_mu(fill, time, sey, hl_imp, hl_sr, key_type):
    with open(f"/eos/project/e/ecloud-simulations/vesedlak/output/sim_heatloads_{fill}.json", "r") as json_file:
        hl_dict = json.load(json_file)
    try:
        sim1_d = f"LHC_ArcDipReal_450GeV_sey{sey:.2f}_Beam1_450GeV_Fill{fill}_T{time:.2f}h"
        sim2_d = f"LHC_ArcDipReal_450GeV_sey{sey:.2f}_Beam2_450GeV_Fill{fill}_T{time:.2f}h"
        hl1_d = hl_dict[sim1_d]
        hl2_d = hl_dict[sim2_d]
        sim1_q = f"LHC_ArcQuadReal_450GeV_sey{sey:.2f}_Beam1_450GeV_Fill{fill}_T{time:.2f}h"
        sim2_q = f"LHC_ArcQuadReal_450GeV_sey{sey:.2f}_Beam2_450GeV_Fill{fill}_T{time:.2f}h"
        hl1_q = hl_dict[sim1_q]
        hl2_q = hl_dict[sim2_q]
    except:
        print(f"Skipping fill {fill}, time {time:.2f}, SEY {sey:.2f} - one or more heatloads missing")
        return np.nan

    if key_type in ["AVG_ARC", "half-cells"]:
        l_d = 14.3*3 #length of dipoles in a half-cell [m]
        l_q = 3.1 #length of quadrupoles in  a half cell [m]
        l_hc = 53.45 #length of half-cell [m]
        mu = hl1_d*l_d + hl1_q*l_q+hl2_d*l_d + hl2_q*l_q+hl_imp+hl_sr #total heatload
    
    elif key_type in ["special_D2B1", "special_D3B1", "special_D4B1"]:
        l_d = 14.3 #length of one dipole [m]
        l_hc = 53.45 #length of half-cell [m]
        hl_imp = hl_imp * l_d / (2 * l_hc) #need to average over the lenghth of the magnet, only have results for a full half cell, and one beam -> 1/2
        hl_sr = hl_sr * l_d / (2 * l_hc)  #need to average over the lenghth of the magnet, only have results for a full half cell  and one beam -> 1/2
        mu = hl1_d*l_d + hl_sr + hl_imp  #total heatload

    elif key_type in ["special_D2B2", "special_D3B2", "special_D4B2"]:
        l_d = 14.3 #length of one dipole [m]
        l_hc = 53.45 #length of half-cell [m]
        hl_imp = hl_imp * l_d / (2 * l_hc) #need to average over the lenghth of the magnet, only have results for a full half cell and one beam -> 1/2
        hl_sr = hl_sr * l_d / (2 * l_hc) #need to average over the lenghth of the magnet, only have results for a full half cell and one beam -> 1/2
        mu = hl2_d*l_d + hl_sr + hl_imp  #total heatload

    elif key_type in ["special_Q1B1"]:
        l_q = 3.1 #length of quadrupoles in  a half cell [m]
        l_hc = 53.45 #length of half-cell [m]
        hl_imp = hl_imp * l_q / (2 * l_hc) #need to average over the lenghth of the magnet, only have results for a full half cell
        hl_sr = hl_sr * l_q / (2 * l_hc) #need to average over the lenghth of the magnet, only have results for a full half cell
        mu = hl1_q*l_q + hl_imp + hl_sr #total heatload

    elif key_type in ["special_Q1B2"]:
        l_q = 3.1 #length of quadrupoles in  a half cell [m]
        l_hc = 53.45 #length of half-cell [m]
        hl_imp = hl_imp * l_q / (2 * l_hc) #need to average over the lenghth of the magnet, only have results for a full half cell
        hl_sr = hl_sr * l_q / (2 * l_hc) #need to average over the lenghth of the magnet, only have results for a full half cell
        mu = hl2_q*l_q + hl_imp + hl_sr #total heatload

    else:
        print(f'Unknown key {key_type}')
        mu = np.nan

    return mu

#extracts the measured heatload from the input json file
def get_meas_hl(fill, time, key_type, key_concrete, err_in_percent):
    with open(f"/eos/project/e/ecloud-simulations/vesedlak/output/meas_hl_Fill{fill}_T{time:.2f}.json", "r") as json_file:
        hl_dict = json.load(json_file)
    #what type of heatload: arc/half-cells/...
    type_dict = hl_dict[key_type]
    #concrete measured heatload
    hl = type_dict[key_concrete]
    err = abs(hl)*err_in_percent / 100
    return hl, err

#calculates the most likely sey and it's error
def log_L_one_point(time, fill, key_type, key_concr, measurement_err):
    if fill <7800:
        seys = np.round(np.arange(1.0,3.01,0.05),2)
    elif fill >=7800:
        seys = np.round(np.arange(1.0,2.21,0.05),2)
    #get impedance and synchotron radiation
    imp_hl, dummy = get_meas_hl(fill, time, "model", "impedance_hl_hc", 10)
    sr_hl, dummy = get_meas_hl(fill, time, "model", "sr_hl_hc", 10)
    #simulated heatloads
    hl_data = []
    for sey in seys:
        hl = get_mu(fill, time, sey, imp_hl, sr_hl, key_type)
        if np.isnan(hl):
            #kostas says this is a problem
            continue
        hl_data.append([sey, hl])
    trans = np.transpose(np.array(hl_data))
    #interpolate
    hl_interp = scipy.interpolate.interp1d(trans[0], trans[1])
    if fill <7800:
        seys_int  = np.arange(1.0,3.00001,0.003)
    elif fill >=7800:
        seys_int  = np.arange(1.0,2.20001,0.003)
    #measured data
    x,err = get_meas_hl(fill, time, key_type, key_concr, measurement_err)
    if x == 0.0:
        return -1,-1
    #if x < 0.0:
    #    print(f"I can't handle negative heatloads, fill {fill} big_key {key_type}, subkey {key_concr}")
    #    return -1,-1
    hl_int = []
    log_L_int = []
    for s in seys_int:
        hl = hl_interp(s)
        log_L_sey = - np.log(err) - (x - hl)**2/(2*err**2)
        hl_int.append(hl)
        log_L_int.append(log_L_sey)
    #substract to get the correct orientation and to set min to 0
    max_L = max(log_L_int)
    total_L = max_L - log_L_int
    min_sey = get_min_sey(seys_int, total_L)
    avg_err  =  get_std(seys_int, total_L)
    return  min_sey, avg_err

#given time, fill and measurement error (assumed, eg 10% on the measured heatloads), uses other methods to get sey and err and writes into the file
def create_sey_db(time, fill, measurement_err):
    #open input file
    try: #if file doesn't exist, this will throw an error
        with open(f"/eos/project/e/ecloud-simulations/vesedlak/output/meas_hl_Fill{fill}_T{time:.2f}.json", "r") as json_file:
            hl_dict = json.load(json_file)
        #get keys and sub-keys
        type_keys = list(hl_dict.keys())
        seys_dict = {} #will hold all sey data
        errs_dict = {} #will hold errors for each sey
        for key in type_keys:
            #skip impedance and sr data
            if key == "model":
                continue
            # temporarily skipping these weird magnets (don't remove before get_mu is ready for them)
            if key in  ["Q5", "Q6", "Q4D2"]:
                continue
            subkeys = list(hl_dict[key].keys())
            sub_dict_sey = {}
            sub_dict_err = {}
            for subkey in subkeys:
                sey, err = log_L_one_point(time, fill, key, subkey, measurement_err)
                sub_dict_sey[subkey] = sey
                sub_dict_err[subkey] = err
            seys_dict[key] = sub_dict_sey
            errs_dict[key] = sub_dict_err
    except:
        print(f" could not open /eos/project/e/ecloud-simulations/vesedlak/output/meas_hl_Fill{fill}_T{time:.2f}.json")
        seys_dict = {}
        errs_dict = {}
    #write result in a json file - separately for this time and fill
    json.dump(seys_dict, open(f"/eos/project/e/ecloud-simulations/vesedlak/results/result_sey_sec_fill{fill}_T{time:.2f}.json","w"), sort_keys=True, indent=4)
    json.dump(errs_dict, open(f"/eos/project/e/ecloud-simulations/vesedlak/results/result_err_sec_fill{fill}_T{time:.2f}.json","w"), sort_keys=True, indent=4)
    #into one big master file
    fin_dict_sey = {fill : seys_dict}
    fin_dict_err = {fill : errs_dict}
    json.dump(fin_dict_sey, open(f"/eos/project/e/ecloud-simulations/vesedlak/results/result_sey_sec.json","a"), sort_keys=True, indent=4)
    json.dump(fin_dict_err, open(f"/eos/project/e/ecloud-simulations/vesedlak/results/result_err_sec.json","a"), sort_keys=True, indent=4)


#finds the minimum sey
def get_min_sey(seys, log_lik):
    min_ind = np.where(log_lik == np.min(log_lik))[0]
    min_sey = seys[min_ind]
    return float(min_sey)

#finds the standard deviation, assuming that the arr is the output of the log likelihood fcn
def get_std(xs,arr):
    arr = arr - 0.5 #1 standard deviation where the parabola crosses 0.5 -> now 0
    try:
        min_ind = int(np.where(arr == np.min(arr))[0])
    except:
        print("minimum not found, returning err = -1")
        return -1
    min_sey = xs[min_ind]
    #split in half
    left_arr = arr[:min_ind]
    right_arr = arr[min_ind:]
    right_xs = xs[min_ind:]
    #turn upside down, find the positions of the minima
    right_arr = abs(right_arr)
    left_arr = abs(left_arr)
    try:
        min_ind_l = int(np.where(left_arr == np.min(left_arr))[0])
    except:
        min_ind_l = 0
    min_ind_r = int(np.where(right_arr == np.min(right_arr))[0])
    root1 = xs[min_ind_l]
    root2 = right_xs[min_ind_r]
    #get the error
    left_err = abs(min_sey - root1)
    right_err = abs(root2 - min_sey)
    avg = (left_err + right_err)/2
    return float(avg)


#for pair in fills_times.get_fill_time_pairs_one_time():
#    if pair[0]>=7800:
#        continue
#    print(f"Calculating results for fill {pair[0]} time {pair[1]}")
#    os.system(f"python measure_heatload_new.py --fill {pair[0]}  --t_obs_h {pair[1]} ")
#    create_sey_db(pair[1], pair[0], 10)


