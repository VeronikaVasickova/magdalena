#imports
import PyECLOUD.myloadmat_to_obj as mlo
import scipy.constants as const
import os
import numpy as np
import glob


#definitions
eVtoJ = const.elementary_charge

#Runs all simulations in the directories provided
def run_sims(dirs):
    #dirs are a 1D list of strings, containing the names of directories in which the simulations are
    for di in dirs:
#        os.chdir(di)
#        if not os.path.exists("Pyecltest.mat"):
        os.system(f"sbatch {di}/job.job")

#SCRIPT

#Open file with names of directiories in which the simulations are
#file_dirs = open("matthew/config/list_of_directories.txt", "r")
#All contents
#folders =  file_dirs.read()
#Folder names in a list
#folder_names = folders.split(" ")
#The last item is an empty character, get rid of it
#folder_names = folder_names[:-1]


#run simulations
#run_sims(folder_names)



#run sims by fill
def run_sims_by_fill(fill):
    sim_folder="/home/HPC/vesedlak/sim_workspace/matthew/simulations/"
    sim_name = f"LHC*Fill{fill}*"
    sims = glob.glob(sim_folder+sim_name)
    for sim in sims:
        os.chdir(sim)
        os.system(f"sbatch job.job")

#don't do this, use re_submit instead - or you'll cancel somtheing that has perhaps finished...


#fills = [7938, 7790,7799,7829,7878,7879,7880,7881,7902,7904,7905,7906,7907,7909,7932,7933,7934,7935,7936,7937,7939,7940,7943,7944,7945,7949,7950,7951,7952,7953,7954,7955,7956,7983,7984,7985,7986,7987,7988,8000,8002,8003,8004,8005]
#for fill in fills:
#    run_sims_by_fill(fill)

#run_sims_by_fill(7938)

#To calculate heatloads
#heatloads =[]
#for folder in folder_names:
#for folder in test_names:
#    heatload = get_heatload(folder+'/Pyecltest.mat')
#    heatloads.append(heatload)


