import matplotlib.colors as mlc
import numpy as np
import matplotlib.pyplot as plt
import time
from matplotlib.backends.backend_pdf import PdfPages
import json


import LHCMeasurementTools.mystyle as ms
import LHCMeasurementTools.LHC_BCT as BCT
import LHCMeasurementTools.LHC_Energy as Energy
import LHCMeasurementTools.LHC_BQM as BQM
import LHCMeasurementTools.LHC_FBCT as FBCT
import LHCMeasurementTools.LHC_Heatloads as HL
import LHCMeasurementTools.TimberManager as tm
import LHCMeasurementTools.TimestampHelpers as th
from LHCMeasurementTools.LHC_Fill_LDB_Query import load_fill_dict_from_json
from LHCMeasurementTools.SetOfHomogeneousVariables import SetOfHomogeneousNumericVariables
from data_folders import data_folder_list, recalc_h5_folder
from scipy.constants import c
import scipy.io as sio

import argparse

parser = argparse.ArgumentParser(description="Save beam snapshots (intensity and bunch length) for PyECLOUD simulations")
parser.add_argument("--fill", required=True, type=int)
parser.add_argument("--save", action="store_true")
parser.add_argument("--t_obs_h", required=True, type=float)

args = parser.parse_args()

#filln = 7932
#filln = 7774
filln = args.fill
t_obs_h = args.t_obs_h
energy_str="450GeV"

halfcell_length = 53.45

dict_fill_bmodes={}
for df in data_folder_list:
    this_dict_fill_bmodes = load_fill_dict_from_json(
            df+'/fills_and_bmodes.json')
    for kk in this_dict_fill_bmodes:
        this_dict_fill_bmodes[kk]['data_folder'] = df
    dict_fill_bmodes.update(this_dict_fill_bmodes)


t_ref = dict_fill_bmodes[filln]['t_startfill']
t_end = dict_fill_bmodes[filln]['t_endfill']
tref_string = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime(t_ref))

data_folder_fill = dict_fill_bmodes[filln]['data_folder']
fill_dict = {}
fill_dict.update(tm.CalsVariables_from_h5(data_folder_fill
    +'/fill_basic_data_h5s/basic_data_fill_%d.h5'%filln,
    ))
fill_dict.update(tm.CalsVariables_from_h5(data_folder_fill +
    '/fill_heatload_data_h5s/heatloads_fill_%d.h5'%filln))
fill_dict.update(tm.CalsVariables_from_h5(data_folder_fill +
    '/heatloads_fill_h5s/imp_and_SR_fill_%d.h5'%filln))
fill_dict.update(tm.CalsVariables_from_h5(data_folder_fill +
    '/fill_cell_by_cell_heatload_data_h5s/cell_by_cell_heatloads_fill_%d.h5'%filln))

data_folder_fill = dict_fill_bmodes[filln]['data_folder']

cell_by_cell_lists =[HL.arc_cells_by_sector[key] for key in HL.arc_cells_by_sector.keys()]
hc_varlist = [x for xs in cell_by_cell_lists for x in xs]
arc_avg_varlist = HL.heat_loads_plot_sets['AVG_ARC']

vlh = HL.variable_lists_heatloads
#q4d2_varlist = vlh["Q4D2s_IR1"] + vlh["Q4D2s_IR5"] + vlh["Q4D2s_IR2"] + vlh["Q4D2s_IR8"]	
#q6_varlist = vlh["Q6s_IR1"] + vlh["Q6s_IR5"] + vlh["Q6s_IR2"] + vlh["Q6s_IR8"]	
#q5_varlist = vlh["Q5s_IR1"] + vlh["Q5s_IR5"] + vlh["Q5s_IR2"] + vlh["Q5s_IR8"]	
special_Q1B1 = vlh['special_HC_Q1B1']
special_D2B1 = vlh['special_HC_D2B1']
special_D3B1 = vlh['special_HC_D3B1']
special_D4B1 = vlh['special_HC_D4B1']
special_Q1B2 = vlh['special_HC_Q1B2']
special_D2B2 = vlh['special_HC_D2B2']
special_D3B2 = vlh['special_HC_D3B2']
special_D4B2 = vlh['special_HC_D4B2']


#remove 17L6
#del special_q1[4]
## del special_q1[-4] #17L6
## del special_q1[-3] #15R2
## del special_q1[-2] #27L8
## del special_q1[-1] #33R2
## 
## del special_d2[-4] #17L6
## del special_d2[-3] #15R2
## del special_d2[-2] #27L8
## del special_d2[-1] #33R2
## 
## del special_d3[-4] #17L6
## del special_d3[-3] #15R2
## del special_d3[-2] #27L8
## del special_d3[-1] #33R2
## 
## del special_d4[-4] #17L6
## del special_d4[-3] #15R2
## del special_d4[-2] #27L8
## del special_d4[-1] #33R2


hl_varlist = hc_varlist + arc_avg_varlist \
             + special_Q1B1 +  special_D2B1 + special_D3B1 + special_D4B1 \
             + special_Q1B2 +  special_D2B2 + special_D3B2 + special_D4B2 


heatloads = SetOfHomogeneousNumericVariables(variable_list=hl_varlist, timber_variables=fill_dict)
impedance_hl_per_m = fill_dict["imp_arc_wm"]
impedance_hl_per_m.values = impedance_hl_per_m.values[0]
sr_hl_per_m = fill_dict["sr_arc_wm"]
sr_hl_per_m.values = sr_hl_per_m.values[0]


meas_hl = {}
meas_hl["model"] = {}
impedance_hl = impedance_hl_per_m.nearest_older_sample(t_obs_h*3600 + t_ref)*halfcell_length
sr_hl = sr_hl_per_m.nearest_older_sample(t_obs_h*3600 + t_ref)*halfcell_length
meas_hl["model"]["impedance_hl_hc"] = impedance_hl
meas_hl["model"]["sr_hl_hc"] = sr_hl


def assign_heat(name, varlist, meas_hl, heatloads):
    meas_hl[name] = {}
    for ii, kk in enumerate(varlist):
        timber_var = heatloads.timber_variables[kk]
        meas_hl[name][kk] = timber_var.nearest_older_sample(t_obs_h*3600 + t_ref)

assign_heat("AVG_ARC", arc_avg_varlist, meas_hl, heatloads)
assign_heat("half-cells", hc_varlist, meas_hl, heatloads)
# assign_heat("Q4D2", q4d2_varlist, meas_hl, heatloads)
# assign_heat("Q5", q5_varlist, meas_hl, heatloads)
# assign_heat("Q6", q6_varlist, meas_hl, heatloads)
assign_heat("special_Q1B1", special_Q1B1, meas_hl, heatloads)
assign_heat("special_D2B1", special_D2B1, meas_hl, heatloads)
assign_heat("special_D3B1", special_D3B1, meas_hl, heatloads)
assign_heat("special_D4B1", special_D4B1, meas_hl, heatloads)
assign_heat("special_Q1B2", special_Q1B2, meas_hl, heatloads)
assign_heat("special_D2B2", special_D2B2, meas_hl, heatloads)
assign_heat("special_D3B2", special_D3B2, meas_hl, heatloads)
assign_heat("special_D4B2", special_D4B2, meas_hl, heatloads)

json.dump(meas_hl, open(f"/eos/project/e/ecloud-simulations/vesedlak/output/meas_hl_Fill{filln}_T{t_obs_h:.2f}.json","w"), indent=4)
