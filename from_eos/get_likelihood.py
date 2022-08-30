import numpy as np
import scipy.interpolate
import get_heat
import json
import matplotlib.pyplot as plt
from scipy.stats import norm
from scipy import optimize
import get_input_lists

#calculate the total heatload as simulated
def get_mu(fill, time, sey, hl_imp, hl_sr):
    l_d = 14.3*3 #length of dipoles in a half-cell [m]
    l_q = 3.1 #length of quadrupoles in  a half cell [m]
    l_hc = 53.45 #length of half-cell [m]

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
        mu = hl1_d*l_d + hl1_q*l_q+hl2_d*l_d + hl2_q*l_q+hl_imp+hl_sr #total heatload
    except:
        mu = np.nan
        print(f"Skipping fill {fill}, time {time:.2f}, SEY {sey:.2f} - one or more heatloads missing")
    return mu

#def log_L_term(err,x,fill, time, sey, hl_imp, hl_sr):
#    term = - np.log(err) - (x - get_mu(fill, time, sey, hl_imp, hl_sr))**2/(2*err**2)
#    #print("term is "+str(term))
#    return term


#input is an array of arrays of shape nx5, each sublist is in the form [x, err, time, imp_hl, sr_hl]
def log_L_all(in_array,fill):
    if fill < 7819:
        seys = np.round(np.arange(1.0,3.01,0.05),2)
    elif fill >= 7819:
        seys = np.round(np.arange(1.0,2.21,0.05),2)

    hl_data = []
    for sey in seys:
        hl_sey =[]
        for arr in in_array:
            hl = get_mu(fill, arr[2], sey, arr[3], arr[4])
            if np.isnan(hl):
                continue
            hl_sey.append(hl)
        hl_data.append(hl_sey)
        trans = np.transpose(np.array(hl_data))
    #interpolate
    if fill < 7819:
        seys_int  = np.round(np.arange(1.0,3.0001,0.00003),2)
    elif fill>= 7819:
        seys_int  = np.round(np.arange(1.0,2.2001,0.00003),2)

    hl_curve_trans =[]
    log_L_curve_trans = []
    for timestep_hls in trans:
        hl_interp = scipy.interpolate.interp1d(seys,timestep_hls)
        hl_int = []
        log_L_int = []
        for s in seys_int:
            hl = hl_interp(s)
            log_L_sey = 0 
            for arr in in_array:
                    log_L_sey = log_L_sey - np.log(arr[1]) - (arr[0] - hl)**2/(2*arr[1]**2)
            hl_int.append(hl)
            log_L_int.append(log_L_sey)
        hl_curve_trans.append(hl_int)
        log_L_curve_trans.append(log_L_int)
    #make total
    total_L = np.zeros_like(np.array(log_L_curve_trans[0]))
    for curve in log_L_curve_trans:
        total_L = total_L + curve
    max_L = max(total_L)
    total_L = max_L - total_L
    min_sey = get_min_sey(seys_int, total_L) 
    avg_err =  get_std(seys_int, total_L)
    return seys_int, total_L, min_sey, avg_err, fill

def log_L_one_point(x, err, time, hl_imp, hl_sr, fill):
    if fill < 7819:
        seys = np.round(np.arange(1.0,3.01,0.05),2)
    elif fill >= 7819:
        seys = np.round(np.arange(1.0,2.21,0.05),2)

    hl_data = []
    for sey in seys:
        hl = get_mu(fill, time, sey, hl_imp, hl_sr)
        if np.isnan(hl):
            continue
        hl_data.append([sey, hl])
    trans = np.transpose(np.array(hl_data))
    #interpolate
    hl_interp = scipy.interpolate.interp1d(trans[0], trans[1])
    if fill < 7819:
        seys_int  = np.round(np.arange(1.0,3.0001,0.00003),2)        
    elif fill>= 7819:
        seys_int  = np.round(np.arange(1.0,2.2001,0.00003),2)
    hl_int = []
    log_L_int = []
    for s in seys_int:
        hl = hl_interp(s)
        log_L_sey = - np.log(err) - (x - hl)**2/(2*err**2)
        #log_L_sey = log_L_sey + norm.logpdf(hl,x,err) #or (x,hl,err) ????
        hl_int.append(hl)
        log_L_int.append(log_L_sey)
    #substract to get the correct orientation and to set min to 0
    max_L = max(log_L_int)
    total_L = max_L - log_L_int
    min_sey = get_min_sey(seys_int, total_L)
    avg_err =  get_std(seys_int, total_L)
    return seys_int, total_L, min_sey, avg_err, fill

def get_min_sey(seys, log_lik):
    min_ind = np.where(log_lik == np.amin(log_lik))[0][1]
    min_sey = seys[min_ind]
    return min_sey

def get_std(xs,arr):
    arr = arr - 0.5 #1 standard deviation where the parabola crosses 0.5 -> now 0
    min_ind = int(np.where(arr == np.min(arr))[0][0])
    min_sey = xs[min_ind]
    #split in half
    left_arr = arr[:min_ind]
    right_arr = arr[min_ind:]
    right_xs = xs[min_ind:]
    #turn upside down, find the positions of the minima
    right_arr = abs(right_arr)
    left_arr = abs(left_arr)
    try:
        min_ind_l = int(np.where(left_arr == np.min(left_arr))[0][0])
    except:
        min_ind_l = 0
    min_ind_r = int(np.where(right_arr == np.min(right_arr))[0][0])
    root1 = xs[min_ind_l]
    root2 = right_xs[min_ind_r]
    #get the error
    left_err = abs(min_sey - root1)
    right_err = abs(root2 - min_sey)
    avg = (left_err + right_err)/2
    return float(avg)
 

def plot_lik(seys_int, log_L, min_sey,  avg_err, fill):
    fig1 = plt.subplot(1,1,1)
    plt.plot(seys_int, log_L, marker=".")
    plt.ylim(0,5)
    plt.grid(visible=True)
    plt.hlines(0.5,1,2.2, colors='magenta')
    plt.xlabel("SEY")
    plt.ylabel(" - log likelihood, interpolated")
    plt.title(f"Fill {fill}, minimum at {min_sey:.2f}, standard error {avg_err:.3f}")
    return fig1


def plot_hl():
    #do something
    print("need to be able to print heatloads")
    return

def err_with_samples(input_list, fill):
    errs = []
    npoints = range(np.shape(input_list)[0])
    for n in npoints:
        in_slice = input_list[:n+1]
        seys_int, log_L, min_sey, avg_err, fill = log_L_all(in_slice,fill)
        errs.append(avg_err)
    npoints = np.array(npoints) + 1
    plt.plot(npoints, errs, color="forestgreen")
    plt.grid(visible=True)
    plt.xlabel("Number of datapoints (time snapshots)")
    plt.ylabel("Average error (sigma)")
    plt.title(f"Dependence of error on the number of samples")
    plt.savefig(f"Err_vs_sample_no_graph_fill{fill}_in1.png")
    plt.show()



#input_list = [[135.47,135.47/10,2.6,4.66,0],[133.48,133.48/10,2.7,4.51,0],[133.99,133.99/10,2.8,4.36,0],
#        [135.61,135.61/10,2.9,4.20,0],[136.19,136.19/10,3.0,4.03,0],[136.64,136.64/10,3.1,3.85,0]]
#frac = 10
#new_in_list = [[160.78, 160.78/frac,2.6,4.66,0],[157.1, 157.1/frac,2.7,4.51,0],[155.88, 155.88/frac,2.8,4.36,0],
#        [153.25,153.25/frac,2.9,4.20,0],[151.39,151.39/frac,3.0,4.03,0],[146.74, 146.74/frac,3.1,3.85,0]]

#times = np.arange(1.2,2.61,0.1)
#input_list = get_input_lists.get_1D_input_list(7938, times, "AVG_ARC", "S67_QBS_AVG_ARC.POSST", 10)

#err_with_samples(input_list, 7938)

#x, err, time, hl_imp, hl_sr, fill
#for arr in input_list:
#    a,b,c,d,e = log_L_one_point(arr[0], arr[1], arr[2], arr[3], arr[4], 7938)
#    plot_lik(a,b,c,d,e)
#    plt.show()


#seys_int, total_L, min_sey, avg_err, fill = log_L_all(input_list,7938)
#plot_lik(seys_int, log_L, min_sey,  avg_err, fill)
#plt.show()




