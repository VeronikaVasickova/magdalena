#This is Veronika Vasickova (Sedlakova)'s master script from summer 2022, supervisor: Konstantinos Paraschou. 
#Do whatever you want with it, no guarantees given


#imports
import numpy as np
import matplotlib.pyplot as plt
import PyECLOUD.myloadmat_to_obj as mlo
import scipy.constants as const
import os

#definitions
eVtoJ = const.elementary_charge

#testing that magdalena is in the pythonpath
def say_hi():
    print("Hi, I am Magdalena, and I know and can do a lot of things")
    return


#numerical integration of heatload
def get_heatload(path_to_mat):
    ob = mlo.myloadmat_to_obj(path_to_mat)
    energy =np.trapz(ob.En_imp_eV_time)
    duration = ob.t[-1]
    heatload_eV = energy/duration
    heatload_J = heatload_eV*eVtoJ
    return heatload_J

#Runs all simulations in the directories provided
def run_sims(dirs):
    #dirs are a 1D list of strings, containing the names of directories in which the simulations are
    for di in dirs:
        os.chdir(di)
        os.system("sbatch job.job")


