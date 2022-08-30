import matplotlib.pyplot as plt
import json
import pandas as pd
import numpy as np
import pickle

def swap_even_odd(vect):
    temp_list = []
    for ii in range(len(vect)//2):
        temp_list.append(vect[2*ii+1])
        temp_list.append(vect[2*ii])
    return np.array(temp_list)

res_fol = "/eos/project/e/ecloud-simulations/vesedlak/results/"

data_dip = json.load(open(res_fol+"result_sey_2D_dip_fill7938.json"))["half-cells"]
data_quad = json.load(open(res_fol+"result_sey_2D_quad_fill7938.json"))["half-cells"]
data_dip_r = json.load(open(res_fol+"result_err_2D_dip_right_fill7938.json"))["half-cells"]
data_dip_l = json.load(open(res_fol+"result_err_2D_dip_left_fill7938.json"))["half-cells"]
data_quad_r = json.load(open(res_fol+"result_err_2D_quad_right_fill7938.json"))["half-cells"]
data_quad_l = json.load(open(res_fol+"result_err_2D_quad_left_fill7938.json"))["half-cells"]



def get_cell_by_cell(data):
    first_cell = 11
    sectors = [12,23,34,45,56,67,78,81]
    dict_sey_cellbycell = {}
    for i, s in enumerate(sectors[:]):
    
        sect_str = str(s)
        R_part = 'R'+sect_str[0]
        L_part = 'L'+sect_str[1]
    
        # Find values at t_sample_h and t2 for each cell.
        val1 = []
        cells = []
        for cell in list(data.keys()):
            if R_part not in cell and L_part not in cell:
                continue
            cellname = cell.split('_')[1]+'_'+cell.split('.POSST')[0][-1]
            if int(cellname[:2])<=first_cell: continue # skip LSS and DS
    
            #~ if cellname=='11L1_3': print cell, cellname
            cells.append(cellname)
    
    
            val1.append(data[cell])
    
        val1 = np.array(val1)
        cells = np.array(cells)
    
        # Sort everything
        # it's R(IP) 09, 10, 11, ... L(IP+1) 33, 32, ...
        msk_l = (np.char.find(cells, 'L') > -1)
        cells_lip = cells[msk_l]
        cells_rip = cells[~msk_l]
     
        #~ print val1.shape
        #~ print msk_l.shape
        val1_lip = val1[msk_l]
        val1_rip = val1[~msk_l]
     
        ind_sort = (np.argsort(cells_lip))[::-1]
        cells_lip = cells_lip[ind_sort]
        val1_lip = val1_lip[ind_sort]
        ind_sort = swap_even_odd(np.argsort(cells_rip))
        cells_rip = cells_rip[ind_sort]
        val1_rip = val1_rip[ind_sort]
     
        cells = np.append(cells_rip, cells_lip)
        val1 = np.append(val1_rip, val1_lip)
        
        dict_sey_cellbycell[s] = {'cell_names':cells, 'sey':val1}
    return dict_sey_cellbycell
    
plt.close('all')
width=0.8
N_snapshots=2
sectors = [12,23,34,45,56,67,78,81]
for jj, s in enumerate(sectors):
    fig1 = plt.figure(jj, figsize=[24/2.,9/2.])
    ax1 = fig1.add_subplot(111)
    
    dip_sey = get_cell_by_cell(data_dip)
    dip_lerr = get_cell_by_cell(data_dip_l)
    dip_rerr = get_cell_by_cell(data_dip_r)
    dip_err = np.array([dip_lerr[s]["sey"], dip_rerr[s]["sey"]])
    quad_sey = get_cell_by_cell(data_quad)
    quad_lerr = get_cell_by_cell(data_quad_l)
    quad_rerr = get_cell_by_cell(data_quad_r)
    quad_err = np.array([quad_lerr[s]["sey"], quad_rerr[s]["sey"]])
    cells = dip_sey[s]["cell_names"]
    ind = np.arange(len(cells))
    ax1.bar(ind-width/2+0*width/N_snapshots, dip_sey[s]["sey"], width/N_snapshots, color='b', alpha=.5, yerr=dip_err, capsize=3)
    ax1.bar(ind-width/2+1*width/N_snapshots, quad_sey[s]["sey"], width/N_snapshots, color='r', alpha=.5, yerr=quad_err, capsize=3)
    
    
    for igrey in ind[1::2]:
        ax1.axvspan(igrey-width/2.-width/4., igrey+width/2., color='k', alpha=.1)
    ax1.set_ylim(1., 2.2)
    
    ax1.set_xticks(ind)
    ax1.set_xticklabels(cells, rotation=90)
    ax1.set_xlim(ind[0]-2*width, ind[-1]+2*width)
    fig1.subplots_adjust(left=.06, right=.96, top=0.9, hspace=0.35, bottom=0.15)
    ax1.set_ylabel("SEY")
    ax1.yaxis.grid(True)
    ax1.set_title(f"Sector {s}")

plt.show()
