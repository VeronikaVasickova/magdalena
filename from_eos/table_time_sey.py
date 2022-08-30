import numpy as np
import scipy.interpolate
import get_heat
import json
import matplotlib.pyplot as plt


#calculate the total heatload as simulated
def get_mu(fill, time, sey, hl_imp, hl_sr):
    l_d = 14.3*3 #length of dipoles in a half-cell [m]
    l_q = 3.1 #length of quadrupoles in  a half cell [m]
    l_hc = 53.45 #length of half-cell [m]

    with open(f"/eos/project/e/ecloud-simulations/vesedlak/output/sim_heatloads_{fill}.json", "r") as json_file:
        hl_dict = json.load(json_file)
    
    sim1_d = f"LHC_ArcDipReal_450GeV_sey{sey:.2f}_Beam1_450GeV_Fill{fill}_T{time:.2f}h"
    sim2_d = f"LHC_ArcDipReal_450GeV_sey{sey:.2f}_Beam2_450GeV_Fill{fill}_T{time:.2f}h"
    hl1_d = hl_dict[sim1_d]
    #print(hl1_d)
    hl2_d = hl_dict[sim2_d]
    #print(hl2_d)
    sim1_q = f"LHC_ArcQuadReal_450GeV_sey{sey:.2f}_Beam1_450GeV_Fill{fill}_T{time:.2f}h"
    sim2_q = f"LHC_ArcQuadReal_450GeV_sey{sey:.2f}_Beam2_450GeV_Fill{fill}_T{time:.2f}h"
    hl1_q = hl_dict[sim1_q]
    #print(hl1_q)
    hl2_q = hl_dict[sim2_q]
    #print(hl2_q)
    mu = hl1_d*l_d + hl1_q*l_q+hl2_d*l_d + hl2_q*l_q+hl_imp+hl_sr #total heatload
    #print("mu is "+str(mu))
    return mu

def log_L_term(err,x,fill, time, sey, hl_imp, hl_sr):
    term = np.log(err)+np.log((x - get_mu(fill, time, sey, hl_imp, hl_sr))**2/(2*err**2))
    #print("term is "+str(term))
    return term


#input is an array of arrays of shape nx5, each sublist is in the form [x, err, time, imp_hl, sr_hl]
def get_log_L(in_array,fill):
    if fill < 7819:
        seys = np.round(np.arange(1.0,3.01,0.05),2)
    elif fill >= 7819:
        seys = np.round(np.arange(1.0,2.21,0.05),2)

    log_L = []
    for sey in seys:
        log_L_sey = 0
        for arr in in_array:
            log_L_sey = log_L_sey + log_L_term(arr[1], arr[0], fill, arr[2], sey, arr[3], arr[4])    
        log_L.append([sey, log_L_sey])
    #now make plots
    trans_log_L = np.transpose(np.array(log_L))
    #print(trans_log_L)
    plt.plot(trans_log_L[0], trans_log_L[1], marker=".")
    plt.xlabel("SEY")
    plt.ylabel(" - log likelihood")
    plt.title(f"Fitting SEY using log likelihood for fill {fill}")
    plt.show()
    return log_L

def sey_of_min_L(x, err, time, hl_imp, hl_sr, fill):
    if fill < 7819:
        seys = np.round(np.arange(1.0,3.01,0.05),2)
    elif fill >= 7819:
        seys = np.round(np.arange(1.0,2.21,0.05),2)
    hl_data = []
    for sey in seys:
        hl = get_mu(fill, time, sey, hl_imp, hl_sr)
        hl_data.append([sey, hl])
    trans = np.transpose(np.array(hl_data))
    #interpolate
    hl_interp = scipy.interpolate.interp1d(trans[0], trans[1])
    if fill < 7819:
        seys_int  = np.round(np.arange(1.0,3.001,0.0003),2)
    elif fill >= 7819:
        seys_int  = np.round(np.arange(1.0,2.2001,0.0003),2)
    hl_int = []
    log_L_int = []
    for s in seys_int:
        hl = hl_interp(s)
        log_L_sey = np.log(err)+np.log((x - hl)**2/(2*err**2))
        hl_int.append(hl)
        log_L_int.append(log_L_sey)
    pos_of_min = log_L_int.index(min(log_L_int))
    likely_sey = seys_int[pos_of_min]
    return [time, likely_sey]



input_list = [[135.47,13.5,2.6,4.66,0],[133.48,13.3,2.7,4.51,0],[133.99,13.4,2.8,4.36,0],
        [135.61,13.6,2.9,4.20,0],[136.19,13.6,3.0,4.03,0],[136.64,13.7,3.1,3.85,0]]

table = []
for arr in input_list:
    table.append(sey_of_min_L(arr[0], arr[1], arr[2], arr[3], arr[4], 7800))
print(table)


