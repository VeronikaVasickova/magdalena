import matplotlib.colors as mlc
import numpy as np
import matplotlib.pyplot as plt
import time
from matplotlib.backends.backend_pdf import PdfPages


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
parser.add_argument("--t_obs", nargs="+", default=[0])

args = parser.parse_args()

#filln = 7932
#filln = 7774
filln = args.fill
energy_str="450GeV"
save = args.save
#list_of_t_obs = [1.6, 1.7, 1.8, 1.9]
list_of_t_obs = list(map(float, args.t_obs))
save_dir = f"/eos/project/e/ecloud-simulations/vesedlak/input_snapshots_one_time/"


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
fill_dict.update(tm.CalsVariables_from_h5(data_folder_fill
        +'/fill_bunchbybunch_data_h5s/bunchbybunch_data_fill_%d.h5'%filln))
fill_dict.update(tm.CalsVariables_from_h5(data_folder_fill +
    '/fill_heatload_data_h5s/heatloads_fill_%d.h5'%filln))

# int_thresh = 2e10
# bint_thresh = 8e9
data_folder_fill = dict_fill_bmodes[filln]['data_folder']

plt.close('all')
fig1 = plt.figure(1, figsize=(6.4*1.9, 4.8*1.5))
ax0 = fig1.add_subplot(211)
ax02 = fig1.add_subplot(212, sharex=ax0)
beam_col = ['b','r']

energy = Energy.energy(fill_dict, beam=1, t_start_fill=t_ref, t_end_fill=t_end)

for beam in [1,2]:
    bct = BCT.BCT(fill_dict, beam=beam)
    ax0.plot((bct.t_stamps-t_ref)/3600., bct.values, color=beam_col[beam-1], lw=2, label=f'Intensity B{beam}')
ax0.plot((energy.t_stamps - t_ref)/3600., energy.energy/1e3, c='black', lw=1.5, alpha=0.2,label='Energy')

hl_varlist = HL.heat_loads_plot_sets['AVG_ARC']
heatloads = SetOfHomogeneousNumericVariables(variable_list=hl_varlist, timber_variables=fill_dict)
for ii, kk in enumerate(heatloads.variable_list):
    colorcurr = ms.colorprog(i_prog=ii, Nplots=len(heatloads.variable_list))
    ax02.plot((heatloads.timber_variables[kk].t_stamps - t_ref)/3600., heatloads.timber_variables[kk].values,
                       '-', color=colorcurr, lw=2., label=kk[:3])

ax0.set_xlabel("Time [h]")
ax02.set_xlabel("Time [h]")
ax0.set_ylabel("Beam intensity [p]")
ax02.set_ylabel("Heat load [W/half-cell]")
ax0.legend(bbox_to_anchor=(1.1, 1.05),  loc='upper left', prop={'size': 14})
ax02.legend(bbox_to_anchor=(1.1, 1.05),  loc='upper left', prop={'size': 14})

fig1.subplots_adjust(left=.1, right=.76, hspace=.28, top=.89)

beam_col = ['b','r']
fbct1 = FBCT.FBCT(fill_dict, beam=1)
fbct2 = FBCT.FBCT(fill_dict, beam=2)
bqm1 = BQM.blength(fill_dict,beam=1)
bqm2 = BQM.blength(fill_dict,beam=2)



#dt=0.1
figs = []
for ii,t_obs_h in enumerate(list_of_t_obs):
    ax0.axvline(t_obs_h, c='k', ls='--')
    #ax0.axvspan(t_obs_h, t_obs_h+dt, facecolor='k', alpha=0.5)
    ax02.axvline(t_obs_h, c='k', ls='--')
    #ax02.axvspan(t_obs_h, t_obs_h+dt, facecolor='k', alpha=0.5)

    beam1_intensity = fbct1.nearest_sample(t_obs_h*3600 + t_ref)
    beam2_intensity = fbct2.nearest_sample(t_obs_h*3600 + t_ref)
    
    blength1 = bqm1.nearest_older_sample(t_obs_h*3600 + t_ref)/4.*c
    blength2 = bqm2.nearest_older_sample(t_obs_h*3600 + t_ref)/4.*c
    
    beam1_dict = {"ppb_vect" : beam1_intensity, "sigmaz_vect": blength1}
    beam2_dict = {"ppb_vect" : beam2_intensity, "sigmaz_vect": blength2}
    beam1_fname = f"Beam1_{energy_str}_Fill{filln}_T{t_obs_h:.2f}h.mat"
    beam2_fname = f"Beam2_{energy_str}_Fill{filln}_T{t_obs_h:.2f}h.mat"

    if save:
        sio.savemat(save_dir+beam1_fname, beam1_dict)
        sio.savemat(save_dir+beam2_fname, beam2_dict)

    figs.append(plt.figure(2+ii))
    ax2 = figs[-1].add_subplot(211)
    ax21 = figs[-1].add_subplot(212)
    ax2.plot(beam1_intensity,'b.')
    ax21.plot(blength1,'b.')
    ax2.plot(beam2_intensity,'r.')
    ax21.plot(blength2,'r.')

    ax2.set_xlabel("25 ns slot")
    ax21.set_xlabel("25 ns slot")
    ax2.set_ylabel("Bunch intensity [p/b]")
    ax21.set_ylabel("Bunch length [m]")
    ax2.set_title(f"Time = {t_obs_h} h")

if save:
    pp = PdfPages(save_dir+f"Fill{filln}_{energy_str}.pdf")
    fig1.savefig(pp, format='pdf')
    for fig in figs:
        fig.savefig(pp, format='pdf')
    pp.close()
else:
    plt.show()







