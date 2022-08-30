#imports
import PyECLOUD.myloadmat_to_obj as mlo
from scipy.constants import elementary_charge
import os
import numpy as np

#Get heatload per meter

#MUST input all parameters as strings
#beam: 1 or 2
#fill: integer number
#time: decimal number
#SEYii: decimal number
#magnet: ArcDipReal or ArcQuadReal
def get_simulated_heatload(magnet, sey, beam, fill, time):
    sim_folder = "/eos/project/e/ecloud-simulations/vesedlak/fin_sims/"
    sim_name = f"LHC_{magnet}_450GeV_sey{sey:.2f}_Beam{beam}_450GeV_Fill{fill}_T{time:.2f}h"
    logfile_path = sim_folder+sim_name+"/logfile.txt"
    if os.path.exists(logfile_path) and "3564/3565" in open(logfile_path, "r").readlines()[-1]:
        try:
            ob = mlo.myloadmat_to_obj(sim_folder+sim_name+"/Pyecltest.mat")
            energy = 0
            for e in ob.En_imp_eV_time:
                energy=energy+e
            duration = ob.t[-1]
            heatload_eV = energy/duration
            heatload_J = heatload_eV*elementary_charge # converting heatload from eV/s to J/s
        except:
            print("matfile seems to be empty in "+ sim_name)
            heatload_J = np.nan
    else:
        heatload_J = np.nan
        print(f"Simulation {sim_name} is  not complete.") 
    return heatload_J




#SCRIPT

#Open file with names of directiories in which the simulations are
#file_dirs = open("matthew/config/list_of_directories.txt", "r")
#All contents
#folders =  file_dirs.read()
#Folder names in a list
#folder_names = folders.split(" ")
#The last item is an empty character, get rid of it
#folder_names = folder_names[:-1]

#for testing, only submit the first 2
#test_names = folder_names[:3]

#To calculate heatloads
#heatloads =[]
#for folder in folder_names:
#for folder in test_names:
#    heatload = get_heatload(folder+'/Pyecltest.mat')
#    heatloads.append(heatload)


