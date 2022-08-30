import numpy as np
import scipy.interpolate
import get_heat
import json
import matplotlib.pyplot as plt
from scipy.stats import norm
from scipy import optimize
import get_input_lists
from numpy import meshgrid

#calculate the total heatload as simulated
def get_mu(fill, time, sey_d, sey_q, key_type, hl_sr, hl_imp, hl_dict):
    sim1_d = f"LHC_ArcDipReal_450GeV_sey{sey_d:.2f}_Beam1_450GeV_Fill{fill}_T{time:.2f}h"
    sim2_d = f"LHC_ArcDipReal_450GeV_sey{sey_d:.2f}_Beam2_450GeV_Fill{fill}_T{time:.2f}h"
    hl1_d = hl_dict[sim1_d]
    hl2_d = hl_dict[sim2_d]
    sim1_q = f"LHC_ArcQuadReal_450GeV_sey{sey_q:.2f}_Beam1_450GeV_Fill{fill}_T{time:.2f}h"
    sim2_q = f"LHC_ArcQuadReal_450GeV_sey{sey_q:.2f}_Beam2_450GeV_Fill{fill}_T{time:.2f}h"
    hl1_q = hl_dict[sim1_q]
    hl2_q = hl_dict[sim2_q]
    if hl1_d == -1000 or hl2_d == -1000 or hl1_q ==-1000 or hl2_q == -1000:
        print(f"Skipping fill {fill}, time {time:.2f}, SEYD {sey_d:.2f}, SEYQ {sey_q:.2f} - one or more heatloads missing")
        mu = 0

    if key_type in ["AVG_ARC", "half-cells"]:
        l_d = 14.3*3 #length of dipoles in a half-cell [m]
        l_q = 3.1 #length of quadrupoles in  a half cell [m]
        l_hc = 53.45 #length of half-cell [m]
        mu = hl1_d*l_d + hl1_q*l_q+hl2_d*l_d + hl2_q*l_q + hl_sr + hl_imp #total heatload
    
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

#simulated heatloads 
def get_hl_data(fill, t_obs, key_types, hl_sr, hl_imp, hl_dict):
    if fill < 7819:
        seys_d = np.round(np.arange(1.0,3.01,0.05),2)
        seys_q = np.round(np.arange(1.0,3.01,0.05),2)
    elif fill >= 7819:
        seys_d = np.round(np.arange(1.0,2.21,0.05),2)
        seys_q = np.round(np.arange(1.0,2.21,0.05),2)
    #meshgrid
    SEY_D, SEY_Q = meshgrid(seys_d, seys_q, indexing = 'ij')
    hl_data_dict = {}
    for key_type in key_types:
        hl_data = np.zeros_like(SEY_D)
        Nd, Nq = SEY_D.shape
        for i in range(Nd):
            for j in range(Nq):
                hl = get_mu(fill, t_obs, SEY_D[i,j], SEY_Q[i,j], key_type, hl_sr, hl_imp, hl_dict)
                hl_data[i,j] = hl
        hl_data_dict[key_type] = hl_data
    return hl_data_dict


#extracts the measured heatload from the input json file
def get_meas_hl(fill, time, key_type, key_concrete, err_in_percent):
    with open(f"/eos/project/e/ecloud-simulations/vesedlak/output/meas_hl_Fill{fill}_T{time:.2f}.json", "r") as json_file:
        hls_dict = json.load(json_file)
    #what type of heatload: arc/half-cells/...
    type_dict = hls_dict[key_type]
    #concrete measured heatload
    hl = type_dict[key_concrete]
    err = abs(hl)*err_in_percent / 100
    return hl, err

#calculates the most likely sey and it's error
def log_L_2D(meas_hl, meas_hl_err, imp_hl, sr_hl, t_obs, fill, key_type, hl_data_dict):
    if fill < 7819:
        seys_d = np.round(np.arange(1.0,3.01,0.05),2)
        seys_q = np.round(np.arange(1.0,3.01,0.05),2)
    elif fill >= 7819:
        seys_d = np.round(np.arange(1.0,2.21,0.05),2)
        seys_q = np.round(np.arange(1.0,2.21,0.05),2)
    #meshgrid
    SEY_D, SEY_Q = meshgrid(seys_d, seys_q, indexing = 'ij')
    hl_concrete = hl_data_dict[f"{t_obs:.2f}"]
    hl_data = hl_concrete[key_type] + imp_hl + sr_hl
    #interpolate
    if fill < 7819:
        seys_int_d  = np.linspace(1.0,3.0,2000)
        seys_int_q  = np.linspace(1.0,3.0,2000)
    elif fill >= 7819:
        seys_int_d  = np.linspace(1.0,2.2,1000)
        seys_int_q  = np.linspace(1.0,2.2,1000)
    SID, SIQ = meshgrid(seys_int_d, seys_int_q, indexing = 'ij')
    hl_int = np.zeros_like(SID)
    log_lik = np.zeros_like(SID)

    hl_int_f = scipy.interpolate.interp2d(SEY_D, SEY_Q, hl_data)

    hl = hl_int_f(SID[:,0], SIQ[0,:]).T
    
    if meas_hl_err < 0.00001:
        return log_lik, -1, -1, SID, SIQ

    log_lik = - np.log(meas_hl_err) - (meas_hl - hl)**2/(2*meas_hl_err**2)

    min_d, min_q = get_min_sey(SID, SIQ, log_lik)
    return log_lik, min_d, min_q, SID, SIQ

def log_L_2D_all(input_arr, fill, key_type,  hl_data_dict):
    list_meas_hl = []
    list_meas_hl_err = []
    list_imp_hl = []
    list_sr_hl = []
    list_t_obs = []
    for this_array in input_arr:
        list_meas_hl.append(this_array[0])
        list_meas_hl_err.append(this_array[1])
        list_imp_hl.append(this_array[2])
        list_sr_hl.append(this_array[3])
        list_t_obs.append(this_array[4])

    dummy1, dummy2, dummy3, SID, SIQ = log_L_2D(list_meas_hl[0], list_meas_hl_err[0], list_imp_hl[0], list_sr_hl[0], list_t_obs[0], fill, key_type, hl_data_dict)
    log_L = np.zeros_like(SID)
    for meas_hl, meas_hl_err, imp_hl, sr_hl, t_obs in zip(list_meas_hl, list_meas_hl_err, list_imp_hl, list_sr_hl, list_t_obs):
        #print(ii)
        log_lik, min_d, min_q, SID, SIQ = log_L_2D(meas_hl, meas_hl_err, imp_hl, sr_hl, t_obs, fill, key_type, hl_data_dict)
        log_L = log_L + log_lik
    #remove min value
    max_L = np.max(log_L)#max(max(li)for li in log_L)
    log_L = max_L - log_L
    min_d, min_q = get_min_sey(SID, SIQ, log_L)
    left_err_d, right_err_d, left_err_q, right_err_q = get_std(SID,SIQ,log_L, min_d, min_q)
    return  min_d, min_q, left_err_d, right_err_d, left_err_q, right_err_q


#given time, fill and measurement error (assumed, eg 10% on the measured heatloads), uses other methods to get sey and err and writes into the file
def create_sey_db(times, fill, measurement_err, hl_data_dict):
    #open input file
    #try: #if file doesn't exist, this will throw an error
    with open(f"/eos/project/e/ecloud-simulations/vesedlak/output/meas_hl_Fill{fill}_T{times[0]:.2f}.json", "r") as json_file:
        hl_dict = json.load(json_file)
        #get keys and sub-keys
    type_keys = list(hl_dict.keys())
    seys_dict_d = {}
    seys_dict_q = {}
    errs_dict_d_left = {}
    errs_dict_d_right = {}
    errs_dict_q_left = {}
    errs_dict_q_right = {}
    for key in type_keys:
         #skip impedance and sr data
        if key == "model":
            continue
        subkeys = list(hl_dict[key].keys())
        sub_dict_sey_d = {}
        sub_dict_err_d_l = {}
        sub_dict_err_d_r = {}
        sub_dict_sey_q = {}
        sub_dict_err_q_l = {}
        sub_dict_err_q_r = {}
        for subkey in subkeys:
            in_list = get_input_lists.get_2D_input_list(fill, times, key, subkey, measurement_err)
            sey_d, sey_q, left_err_d, right_err_d, left_err_q, right_err_q  = log_L_2D_all(in_list, fill, key, hl_data_dict)
            sub_dict_sey_d[subkey] = sey_d
            sub_dict_err_d_l[subkey] = left_err_d
            sub_dict_err_d_r[subkey] = right_err_d
            sub_dict_sey_q[subkey] = sey_q
            sub_dict_err_q_l[subkey] = left_err_q
            sub_dict_err_q_r[subkey] = right_err_q
        seys_dict_d[key]=sub_dict_sey_d
        seys_dict_q[key]=sub_dict_sey_q
        errs_dict_d_left[key]=sub_dict_err_d_l
        errs_dict_d_right[key]=sub_dict_err_d_r
        errs_dict_q_left[key]=sub_dict_err_q_l
        errs_dict_q_right[key]=sub_dict_err_q_r
        print(f'Created dictionary entry for {key}')
    #write result in a json file - separately for this time and fill
    json.dump(seys_dict_d, open(f"/eos/project/e/ecloud-simulations/vesedlak/results/result_sey_2D_dip_fill{fill}.json","w"), sort_keys=True, indent=4)
    json.dump(seys_dict_q, open(f"/eos/project/e/ecloud-simulations/vesedlak/results/result_sey_2D_quad_fill{fill}.json","w"), sort_keys=True, indent=4)
    json.dump(errs_dict_d_left, open(f"/eos/project/e/ecloud-simulations/vesedlak/results/result_err_2D_dip_left_fill{fill}.json","w"), sort_keys=True, indent=4)
    json.dump(errs_dict_d_right, open(f"/eos/project/e/ecloud-simulations/vesedlak/results/result_err_2D_dip_right_fill{fill}.json","w"), sort_keys=True, indent=4)
    json.dump(errs_dict_q_left, open(f"/eos/project/e/ecloud-simulations/vesedlak/results/result_err_2D_quad_left_fill{fill}.json","w"), sort_keys=True, indent=4)
    json.dump(errs_dict_q_right, open(f"/eos/project/e/ecloud-simulations/vesedlak/results/result_err_2D_quad_right_fill{fill}.json","w"), sort_keys=True, indent=4)


def get_min_sey(seys_d, seys_q, log_lik):
    min_ind = np.where(log_lik == np.min(log_lik))
    #print(min_ind)
    min_sey_d = seys_d[min_ind]
    min_sey_q = seys_q[min_ind]
    return float(min_sey_d[0]), float(min_sey_q[0])


#finds the standard deviation, assuming that the arr is the output of the log likelihood fcn
def get_std(SID, SIQ, log_L, min_d, min_q):
    stopping = False
    sey_left_d = -1
    sey_right_d = -1
    sey_left_q = -1
    sey_right_q = -1
    #going from left
    for i in range(log_L.shape[0]):
        for j in range(log_L.shape[1]):
            if log_L[i,j] < 0.5:
                sey_left_d = SID[i,j]
                stopping = True
                break
        if stopping:
            stopping = False
            break
    #going from right
    for i in range(log_L.shape[0]-1,0,-1):
        for j in range(log_L.shape[1]):
            if log_L[i,j] < 0.5:
                sey_right_d = SID[i,j]
                stopping = True
                break
        if stopping:
            stopping = False
            break
    #going from bottom
    for i in range(log_L.shape[1]):
        for j in range(log_L.shape[0]):
            if log_L[j,i] < 0.5:
                sey_left_q = SIQ[j,i]
                stopping = True
                break
        if stopping:
            stopping = False
            break
    #going from top
    for i in range(log_L.shape[1]-1,0,-1):
        for j in range(log_L.shape[0]):
            if log_L[j,i] < 0.5:
                sey_right_q = SIQ[j,i]
                stopping = True
                break
        if stopping:
            stopping = False
            break
    left_err_d = float(abs(min_d-sey_left_d))
    right_err_d = float(abs(min_d-sey_right_d))
    left_err_q = float(abs(min_q-sey_left_q))
    right_err_q = float(abs(min_q-sey_right_q))
    return left_err_d, right_err_d, left_err_q, right_err_q


fill = 7938
times = np.arange(1.2,2.61,0.1)

def main_2D_database(fill, times, meas_err):
    with open(f"/eos/project/e/ecloud-simulations/vesedlak/output/sim_heatloads_{fill}.json", "r") as json_file:
        hl_dict = json.load(json_file)

    hl_data_dict = {}
    key_types = ["AVG_ARC", "half-cells", "special_D2B1", "special_D3B1", "special_D4B1", "special_Q1B1","special_D2B2", "special_D3B2", "special_D4B2", "special_Q1B2"]
    for t_obs in times:
        with open(f"/eos/project/e/ecloud-simulations/vesedlak/output/meas_hl_Fill{fill}_T{t_obs:.2f}.json", "r") as json_file:
            measured_hls = json.load(json_file)
        model_dict = measured_hls["model"]
        imp = model_dict["impedance_hl_hc"]
        sr = model_dict["sr_hl_hc"]
        hl_data_dict[f"{t_obs:.2f}"] = get_hl_data(fill, t_obs, key_types, sr, imp, hl_dict)

    create_sey_db(times, fill, meas_err, hl_data_dict)

main_2D_database(fill, times, 10)
