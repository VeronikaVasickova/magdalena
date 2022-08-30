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
def get_mu(fill, time, sey_d, sey_q, hl_imp, hl_sr):
    l_d = 14.3*3 #length of dipoles in a half-cell [m]
    l_q = 3.1 #length of quadrupoles in  a half cell [m]
    l_hc = 53.45 #length of half-cell [m]

    with open(f"/eos/project/e/ecloud-simulations/vesedlak/output/sim_heatloads_{fill}.json", "r") as json_file:
        hl_dict = json.load(json_file)
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
        mu = hl1_d*l_d + hl1_q*l_q+hl2_d*l_d + hl2_q*l_q+hl_imp+hl_sr #total heatload
    return mu

def get_mu_dip_q(fill, time, sey_d, sey_q, beam):
    l_d = 14.3*3 #length of dipoles in a half-cell [m]
    l_q = 3.1 #length of quadrupoles in  a half cell [m]
    l_hc = 53.45 #length of half-cell [m]
    with open(f"/eos/project/e/ecloud-simulations/vesedlak/output/sim_heatloads_{fill}.json", "r") as json_file:
        hl_dict = json.load(json_file)
    try:
        sim1_d = f"LHC_ArcDipReal_450GeV_sey{sey_d:.2f}_Beam{beam}_450GeV_Fill{fill}_T{time:.2f}h"
        hl1_d = hl_dict[sim1_d]
        mu_dip =  hl1_d*l_d  
    except:
        mu_dip = np.nan
        print(f"Skipping dipoles, beam {beam}, fill {fill}, time {time:.2f}, SEY {sey_d:.2f} - heatload missing")
    try:
        sim1_q = f"LHC_ArcQuadReal_450GeV_sey{sey_q:.2f}_Beam1_450GeV_Fill{fill}_T{time:.2f}h"
        hl1_q = hl_dict[sim1_q]
        mu_q = hl1_q*l_q 
    except:
       mu_q = np.nan
       print(f"Skipping quadrupoles, beam{beam}, fill {fill}, time {time:.2f}, SEY {sey_q:.2f} - heatload missing")
    return mu_dip, mu_q


#def log_L_term(err,x,fill, time, sey, hl_imp, hl_sr):
#    term = - np.log(err) - (x - get_mu(fill, time, sey, hl_imp, hl_sr))**2/(2*err**2)
#    #print("term is "+str(term))
#    return term


#input is an array of arrays of shape nx5, each sublist is in the form [x, err, imp_hl, sr_hl, t_obs]
def log_L_2D(arr,fill):
    if fill < 7819:
        seys_d = np.round(np.arange(1.0,3.01,0.05),2)
        seys_q = np.round(np.arange(1.0,3.01,0.05),2)
    elif fill >= 7819:
        seys_d = np.round(np.arange(1.0,2.21,0.05),2)
        seys_q = np.round(np.arange(1.0,2.21,0.05),2)
    #meshgrid
    SEY_D, SEY_Q = meshgrid(seys_d, seys_q, indexing = 'ij')
    hl_data = np.zeros_like(SEY_D)
    Nd, Nq = SEY_D.shape 
    for i in range(Nd):
        for j in range(Nq):
            hl = get_mu(fill, arr[4], SEY_D[i,j], SEY_Q[i,j], arr[2], arr[3])
            #if np.isnan(hl) or hl == 0.0:
            #    hl = -1
            hl_data[i,j] = hl
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
    # for i in range(NID):
    #     for j in range(NIQ):
    #         hl = hl_int_f(SID[i,j], SIQ[i,j])
    #         hl_int[i,j] = hl
    #         log_lik[i,j] = - np.log(arr[1]) - (arr[0] - hl)**2/(2*arr[1]**2)
    hl = hl_int_f(SID[:,0], SIQ[0,:]).T
    log_lik = - np.log(arr[1]) - (arr[0] - hl)**2/(2*arr[1]**2)
    #remove min value    
    #max_L = max(max(li)for li in log_lik)
    #log_lik = max_L - log_lik
    #position of min likelihood
    #min_d, min_q = get_min_sey(SID, SIQ, log_lik)
    min_d, min_q = [0,0]
    return log_lik, min_d, min_q, SID, SIQ

#now input_arr is an array of arrays of shape nx5, each of content [x, err, imp_hl, sr_hl, t_obs]
def log_L_2D_all(input_arr, fill):
    dummy1, dummy2, dummy3, SID, SIQ = log_L_2D(input_arr[0],fill)
    log_L = np.zeros_like(SID)
    for ii,arr in enumerate(input_arr):
        #print(ii)
        log_lik, min_d, min_q, SID, SIQ = log_L_2D(arr, fill)
        log_L = log_L + log_lik
    #remove min value
    max_L = np.max(log_L)#max(max(li)for li in log_L)
    log_L = max_L - log_L
    min_d, min_q = get_min_sey(SID, SIQ, log_L)
    return log_L, min_d, min_q, SID, SIQ

def get_min_sey(seys_d, seys_q, log_lik):
    min_ind = np.where(log_lik == np.min(log_lik))
    #print(min_ind)
    min_sey_d = seys_d[min_ind]
    min_sey_q = seys_q[min_ind]
    return min_sey_d, min_sey_q
    
def plot_log_L_2D(sey_d, sey_q, log_L_2D, min_d, min_q, fill, sector):
    fig1 = plt.figure()
    ax1 = fig1.add_subplot(111)
    ax1.set_xlabel("SEY dipoles")
    ax1.set_ylabel("SEY quadrupoles")
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
    try:
        plt.title(f"{fill}, {sector}, dipoles: {min_d[0]:.2f}, quadrupoles:{min_q[0]:.2f}")
    except:
        plt.title(f"Fill {fill}, sector {sector}, cannot estimate minimum SEY")
    return fig1

def plot_slices(seys,data_mesh, slice_at_d, slice_at_q):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    dips, = ax.plot(seys, data_mesh[:,slice_at_d], label="Dipoles")
    quads, = ax.plot(seys, data_mesh[slice_at_q], label="Quadrupoles")
    plt.legend(handles=[dips, quads])
    plt.grid(visible=True)
    plt.xlabel("SEY")
    plt.ylabel("- log L")
    plt.ylim(0,5)
    plt.title(f"Cut throught the {slice_at_d}. array in dipoles and {slice_at_q}. in quadrupoles")
    return fig

def plot_slices(seys,data_mesh, slice_at_d, slice_at_q):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    dips, = ax.plot(seys, data_mesh[:,slice_at_d], label="Dipoles")
    quads, = ax.plot(seys, data_mesh[slice_at_q], label="Quadrupoles")
    plt.legend(handles=[dips, quads])
    plt.grid(visible=True)
    plt.xlabel("SEY")
    plt.ylabel("- log L")
    plt.ylim(0,5)
    plt.title(f"Cut throught the {slice_at_d}. array in dipoles and {slice_at_q}. in quadrupoles")
    return fig

def get_std(sid, siq, logL):
    contour = np.where(logL == 0.5)
    print(contour)


def plot_diagonal(seys,data_mesh):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    diag = []
    n = seys.shape[0]
    for i in range(n):
        diag.append(data_mesh[i,i])
    ax.plot(seys, diag)
    plt.grid(visible=True)
    plt.xlabel("SEY")
    plt.ylabel("- log L")
    plt.ylim(0,5)
    plt.title(f"Diagonal cut")
    return fig


def plot_hl_d_q(fill, time):
    #if fill < 7819:
    #    seys_d = np.round(np.arange(1.0,3.01,0.05),2)
    #    seys_q = np.round(np.arange(1.0,3,01,0.05),2)
    #elif fill >= 7819:
    #    seys_d = np.round(np.arange(1.0,2.21,0.05),2)
    #    seys_q = np.round(np.arange(1.0,2.21,0.05),2)
    seys = np.round(np.arange(1.0,2.21,0.05),2)
    hl_d_1 = []
    hl_q_1 = []
    hl_d_2 = []
    hl_q_2 = []
    for sey in seys:
        hl_d_1.append(get_mu_dip_q(fill, time, sey, sey, 1)[0])
        hl_q_1.append(get_mu_dip_q(fill, time, sey, sey, 1)[1])    
        hl_d_2.append(get_mu_dip_q(fill, time, sey, sey, 2)[0])
        hl_q_2.append(get_mu_dip_q(fill, time, sey, sey, 2)[1])
    fig = plt.figure()
    ax = fig.add_subplot(111)
    dips1, = ax.plot(seys, hl_d_1, label="Dipoles, Beam 1")
    quads1, = ax.plot(seys, hl_q_1, label="Quadrupoles, Beam 1")
    dips2, = ax.plot(seys, hl_d_2, label="Dipoles, Beam 2")
    quads2, = ax.plot(seys, hl_q_2, label="Quadrupoles, Beam 2")
    plt.legend(handles=[dips1, dips2, quads1, quads2])
    plt.grid(visible=True)
    #plt.ylim(0,200)
    plt.xlabel("SEY")
    plt.ylabel("Healtload [W]")
    #plt.title(f"Heatloads in fill {fill}, beam {beam} at time {time}")
    return fig

def plot_hl_d_q_all(fill, times):
    if fill < 7819:
        seys_d = np.round(np.arange(1.0,3.01,0.05),2)
        seys_q = np.round(np.arange(1.0,3.01,0.05),2)
    elif fill >= 7819:
        seys_d = np.round(np.arange(1.0,2.21,0.05),2)
        seys_q = np.round(np.arange(1.0,2.21,0.05),2)

    hl_d_b1 = []
    hl_q_b1 = []
    hl1_b1 = 0
    hl2_b1 = 0
    hl_d_b2 = []
    hl_q_b2 = []
    hl1_b2 = 0
    hl2_b2 = 0
    for sey in seys:
        for time in times:
            hl1_b1 = hl1_b1 + get_mu_dip_q(fill, time, sey, sey, 1)[0]
            hl2_b1 = hl2_b1 + get_mu_dip_q(fill, time, sey, sey, 1)[1]
            hl1_b2 = hl1_b2 + get_mu_dip_q(fill, time, sey, sey, 2)[0]
            hl2_b2 = hl2_b2 + get_mu_dip_q(fill, time, sey, sey, 2)[1]
        hl_d_b1.append(hl1_b1)
        hl_q_b1.append(hl2_b1)
        hl_d_b2.append(hl1_b2)
        hl_q_b2.append(hl2_b2)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    dipsB1, = ax.plot(seys, hl_d_b1, label="Dipoles, Beam 1")
    quadsB1, = ax.plot(seys, hl_q_b1, label="Quadrupoles, Beam 1")
    dipsB2, = ax.plot(seys, hl_d_b2, label="Dipoles, Beam 2")
    quadsB2, = ax.plot(seys, hl_q_b2, label="Quadrupoles, Beam 2")
    plt.legend(handles=[dipsB1, dipsB2, quadsB1, quadsB2])
    plt.grid(visible=True)
    plt.xlabel("SEY")
    plt.ylabel("Healtload [W]")
    plt.title(f"Simulated heatloads in fill {fill}")
    return fig


def plot_2D_halfcells(fill, times, name_to_save):
    with open(f"/eos/project/e/ecloud-simulations/vesedlak/output/meas_hl_Fill{fill}_T{times[0]:.2f}.json", "r") as json_file:
            hl_dict = json.load(json_file)
    pp = PdfPages(f"/eos/project/e/ecloud-simulations/vesedlak/results/{name_to_save}.pdf")
    halfcells = list(hl_dict["half-cells"].keys())
    for ii, halfcell in enumerate(halfcells):
        print(f"{ii}/{len(halfcells)}, {halfcell}")
        input_list = get_input_lists.get_2D_input_list(7938, times, "half-cells", halfcell, 10)
        #try:
        log_lik, min_d, min_q, SID, SIQ = log_L_2D_all(input_list, fill)
        fig = plot_log_L_2D(SID, SIQ, log_lik, min_d, min_q, fill, halfcell)
        fig.savefig(pp, format='pdf')
        #except:
        #    print(f"could not get data for {halfcell}")
            #plt.plot([1,2,3,4,5],[1,2,3,4,5])
            #title(f"could not get data for {halfcell}")
        #fig.savefig(pp, format='pdf')
        plt.close()
    pp.close()

def plot_2D_sections(fill, times, name_to_save, key):
    with open(f"/eos/project/e/ecloud-simulations/vesedlak/output/meas_hl_Fill{fill}_T{times[0]:.2f}.json", "r") as json_file:
            hl_dict = json.load(json_file)
    pp = PdfPages(f"/eos/project/e/ecloud-simulations/vesedlak/results/{name_to_save}.pdf")
    halfcells = list(hl_dict[key].keys())
    for ii, halfcell in enumerate(halfcells):
        print(f"{ii}/{len(halfcells)}, {halfcell}")
        input_list = get_input_lists.get_2D_input_list(7938, times, key , halfcell, 10)
        #try:
        log_lik, min_d, min_q, SID, SIQ = log_L_2D_all(input_list, fill)
        fig = plot_log_L_2D(SID, SIQ, log_lik, min_d, min_q, fill, halfcell)
        fig.savefig(pp, format='pdf')
        #except:
        #    print(f"could not get data for {halfcell}")
            #plt.plot([1,2,3,4,5],[1,2,3,4,5])
            #title(f"could not get data for {halfcell}")
        #fig.savefig(pp, format='pdf')
        plt.close()
    pp.close()

def plot_2D_sections_one_time(fill, times, which_time, key):
    with open(f"/eos/project/e/ecloud-simulations/vesedlak/output/meas_hl_Fill{fill}_T{times[0]:.2f}.json", "r") as json_file:
            hl_dict = json.load(json_file)
    halfcells = list(hl_dict[key].keys())
    for ii, halfcell in enumerate(halfcells):
        print(f"{ii}/{len(halfcells)}, {halfcell}")
        input_list = get_input_lists.get_2D_input_list(7938, times, key , halfcell, 10)[which_time]
        log_lik, min_d, min_q, SID, SIQ = log_L_2D(input_list, fill)
        fig = plot_log_L_2D(SID, SIQ, log_lik, min_d, min_q, fill, halfcell)
        plt.show()


times_7938 = np.arange(1.2,2.61,0.1)
#plot_2D_sections(7938, times_7938, "arcs_2D_fill7938", "AVG_ARC")


#log_lik, min_d, min_q, SID, SIQ = log_L_2D_all(input_list_67,7938)
#get_std(SID, SIQ, log_lik)

#for no in [12,23,34,45,56,67,78,81]:
#    name = f"S{no}_QBS_AVG_ARC.POSST"
#    input_list = get_input_lists.get_2D_input_list(7938, times_7938, "AVG_ARC", name, 10)
#    log_lik, min_d, min_q, SID, SIQ = log_L_2D_all(input_list,7938)
#    seys_int_d  = np.arange(1.0,2.2001,0.003)
#    fig1 = plot_log_L_2D(SID, SIQ, log_lik, min_d, min_q, 7938, no)
#    plt.show()

times_7939 = [1.3, 1.6, 1.9, 2.2, 2.5]

plot_hl_d_q(7938, times_7938[0])
plt.show()



#plot_2D_sections_one_time(7938, times_7938, 4, "AVG_ARC")

