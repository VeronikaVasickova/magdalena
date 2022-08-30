import numpy as np
import scipy.interpolate
import get_heat
import json
import matplotlib.pyplot as plt
from scipy.stats import norm
from scipy import optimize
from numpy import meshgrid
import get_input_lists
import cmcrameri.cm as cm
from matplotlib.backends.backend_pdf import PdfPages



#calculate the total heatload as simulated
def get_mu(fill, time, sey_d, sey_q):
    l_d = 14.3*3 #length of dipoles in a half-cell [m]
    l_q = 3.1 #length of quadrupoles in  a half cell [m]
    l_hc = 53.45 #length of half-cell [m]

    #try:
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
    else:
        mu = hl1_d*l_d + hl1_q*l_q+hl2_d*l_d + hl2_q*l_q #total simulated heatload
    return mu

def get_hl_data(fill, t_obs):
    if fill < 7819:
        seys_d = np.round(np.arange(1.0,3.01,0.05),2)
        seys_q = np.round(np.arange(1.0,3,01,0.05),2)
    elif fill >= 7819:
        seys_d = np.round(np.arange(1.0,2.21,0.05),2)
        seys_q = np.round(np.arange(1.0,2.21,0.05),2)
    #meshgrid
    SEY_D, SEY_Q = meshgrid(seys_d, seys_q, indexing = 'ij')
    hl_data = np.zeros_like(SEY_D)
    Nd, Nq = SEY_D.shape 
    for i in range(Nd):
        for j in range(Nq):
            hl = get_mu(fill, t_obs, SEY_D[i,j], SEY_Q[i,j])
            #if np.isnan(hl) or hl == 0.0:
            #    hl = -1
            hl_data[i,j] = hl
    return hl_data

#input is an array of arrays of shape nx5, each sublist is in the form [x, err, imp_hl, sr_hl, t_obs]
def log_L_2D(meas_hl, meas_hl_err, imp_hl, sr_hl, t_obs, fill):
    if fill < 7819:
        seys_d = np.round(np.arange(1.0,3.01,0.05),2)
        seys_q = np.round(np.arange(1.0,3.01,0.05),2)
    elif fill >= 7819:
        seys_d = np.round(np.arange(1.0,2.21,0.05),2)
        seys_q = np.round(np.arange(1.0,2.21,0.05),2)
    #meshgrid
    SEY_D, SEY_Q = meshgrid(seys_d, seys_q, indexing = 'ij')
    hl_data = hl_data_dict[f"{t_obs:.2f}"] + imp_hl + sr_hl
    #interpolate
    if fill < 7819:
        seys_int_d  = np.linspace(1.0,3.0,2000)
        seys_int_q  = np.linspace(1.0,3.0,2000)
    elif fill >= 7819:
        seys_int_d  = np.linspace(1.0,2.2,1000)
        seys_int_q  = np.linspace(1.0,2.2,1000)

    SID, SIQ = meshgrid(seys_int_d, seys_int_q, indexing = 'ij')
    hl_int_f = scipy.interpolate.interp2d(SEY_D, SEY_Q, hl_data)

    hl_int = np.zeros_like(SID)
    log_lik = np.zeros_like(SID)
    NID, NIQ = SID.shape
    hl = hl_int_f(SID[:,0], SIQ[0,:]).T

    log_lik = - np.log(meas_hl_err) - (meas_hl - hl)**2/(2*meas_hl_err**2)

    min_d, min_q = get_min_sey(SID, SIQ, log_lik)
    return log_lik, min_d, min_q, SID, SIQ

#now input_arr is an array of arrays of shape nx5, each of content [x, err, imp_hl, sr_hl, t_obs]
def log_L_2D_all(input_arr, fill):

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

    dummy1, dummy2, dummy3, SID, SIQ = log_L_2D(list_meas_hl[0], list_meas_hl_err[0], list_imp_hl[0], list_sr_hl[0], list_t_obs[0], fill)
    log_L = np.zeros_like(SID)
    for meas_hl, meas_hl_err, imp_hl, sr_hl, t_obs in zip(list_meas_hl, list_meas_hl_err, list_imp_hl, list_sr_hl, list_t_obs):
        #print(ii)
        log_lik, min_d, min_q, SID, SIQ = log_L_2D(meas_hl, meas_hl_err, imp_hl, sr_hl, t_obs, fill)
        log_L = log_L + log_lik
    #remove min value
    max_L = np.max(log_L)#max(max(li)for li in log_L)
    log_L = max_L - log_L
    min_d, min_q = get_min_sey(SID, SIQ, log_L)
    left_err_d, right_err_d, left_err_q, right_err_q = get_std(SID,SIQ,log_L, min_d, min_q)
    return log_L, min_d, min_q, SID, SIQ, left_err_d, right_err_d, left_err_q, right_err_q 

def get_min_sey(seys_d, seys_q, log_lik):
    min_ind = np.where(log_lik == np.min(log_lik))
    #print(min_ind)
    min_sey_d = seys_d[min_ind]
    min_sey_q = seys_q[min_ind]
    return min_sey_d, min_sey_q
   
def get_std(SID, SIQ, log_L, min_d, min_q):
    stopping = False
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
    left_err_d = abs(min_d-sey_left_d)
    right_err_d = abs(min_d-sey_right_d)
    left_err_q = abs(min_q-sey_left_q)
    right_err_q = abs(min_q-sey_right_q)
    return left_err_d, right_err_d, left_err_q, right_err_q


def plot_log_L_2D(sey_d, sey_q, log_L_2D, min_d=None, min_q=None, fill=None, sector=None):
    fig1 = plt.figure()
    ax1 = fig1.add_subplot(111)
    ax1.set_xlabel("SEY in dipole magnets")
    ax1.set_ylabel("SEY in quadrupole magnets")
    plt.setp(ax1.get_xticklabels(), fontsize=11) 
    plt.setp(ax1.get_yticklabels(), fontsize=11) 
    cf = plt.pcolormesh(sey_d, sey_q, log_L_2D, cmap=cm.batlow_r, lw=0, rasterized=True) 
    plt.clim(0, 5) 
    cbar = plt.colorbar(cf, ticks=np.linspace(0, 5, 11))
    cbar.set_label("- log likelihood")
    cbar.ax.tick_params(labelsize=11)
    levels=[0.5,2.0]
    ct = ax1.contour(sey_d[:-1,:-1], sey_q[:-1,:-1], log_L_2D[:-1,:-1], levels, colors='k', linewidths=2.) 
    plt.clabel(ct, colors='k', fmt='%.1f', fontsize=20)
    plt.plot(min_d, min_q, marker='*', color='r')
    if min_d is None or len(min_d) == 0:
        min_d = [-1]
    if min_q is None or len(min_q) == 0:
        min_q = [-1]
    plt.title(f"{fill}, {sector}, SEY dipoles {min_d[0]:.2f}, SEY quadrupoles {min_q[0]:.2f}")
    return fig1


def plot_2D_halfcells(fill, times, name_to_save):
    #mode = "AVG_ARC"
    mode = "half-cells"
    with open(f"/eos/project/e/ecloud-simulations/vesedlak/output/meas_hl_Fill{fill}_T{times[0]:.2f}.json", "r") as json_file:
            hl_dict = json.load(json_file)
    pp = PdfPages(f"/eos/project/e/ecloud-simulations/vesedlak/results/{name_to_save}.pdf")
    halfcells = list(hl_dict[mode].keys())
    for ii, halfcell in enumerate(halfcells):
        input_list = get_input_lists.get_2D_input_list(7938, times, mode, halfcell, 10)
        print(f"{ii}/{len(halfcells)}, {halfcell}, HL: {input_list[0][0]:.2f}")
        log_lik, min_d, min_q, SID, SIQ = log_L_2D_all(input_list, fill)
        fig = plot_log_L_2D(SID, SIQ, log_lik, min_d, min_q, fill, halfcell)
        fig.savefig(pp, format='pdf')
        plt.close()
    pp.close()

fill = 7938
times = np.arange(1.2,2.61,0.1)

#with open(f"/eos/project/e/ecloud-simulations/vesedlak/output/sim_heatloads_{fill}.json", "r") as json_file:
#    hl_dict = json.load(json_file)


#hl_data_dict = {}
#for t_obs in times:
#    hl_data_dict[f"{t_obs:.2f}"] = get_hl_data(fill, t_obs)



#input_list = get_input_lists.get_2D_input_list(fill, times, "half-cells","QRLBA_09R1_QBS947.POSST", 10)
#log_L_2D_all(input_list, fill)    
    
#plot_2D_halfcells(fill, times, "halfcells_2D_fill7938_new")

