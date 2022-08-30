#imports
import os
import glob
import json


#Runs all simulations in the directories provided
def run_sims_not_finished(fill):
    #Get list of all simulations in the folder
    sim_folder = "/home/HPC/vesedlak/sim_workspace/matthew/simulations/"
    sim_name = f"LHC*{fill}*"
    sim_dirs = glob.glob(sim_folder+sim_name)
    #dirs are a 1D list of strings, containing the paths to directories in which the simulations are
    for di in sim_dirs:
        logfile_path = di+"/logfile.txt"
        #if the logfile doesn't exist, or it isn't finished, run the simulation (at least one of conditins true)
        if not os.path.exists(logfile_path) or "3564/3565" not in open(logfile_path, "r").readlines()[-1]:
            os.chdir(di)
            os.system("sbatch job.job")

#Runs all simulationswhich have no logfile
def run_sims_not_started(fill):
    #Get list of all simulations in the folder
    sim_folder = "/home/HPC/vesedlak/sim_workspace/matthew/simulations/"
    sim_name = f"LHC*{fill}*"
    sim_dirs = glob.glob(sim_folder+sim_name)
    #dirs are a 1D list of strings, containing the paths to directories in which the simulations are
    for di in sim_dirs:
        logfile_path = di+"/logfile.txt"
        #if the logfile doesn't exist, or it isn't finished, run the simulation (at least one of conditins true)
        if not os.path.exists(logfile_path):
            os.chdir(di)
            os.system("sbatch job.job")


# 7938 missing from this list below

#fills = [7776,7790,7799,7829,7878,7879,7880,7881,7902,7904,7905,7906,7907,7909,7932,7933,7934,7935,7936,7937,7939,7940,7943,7944,7945,7949,7950,7951,7952,7953,7954,7955,7956,7983,7984,7985,7986,7987,7988,8000,8002,8003,8004,8005]
fills = [7774, 7789, 7793, 7795, 7797, 7819, 7776,7749,7776,7790,7793,7795,7797,7799,7800,7880,7881,7902,7904,7905,7906,7907,7909,7932,7933,7934,7935,7936,7937,7939,7940,7943,7944,7945,7949,7950,7951,7952,7953,7954,7955,7956,7983,7984,7985,7986,7987,7988]
#fills = [7987,7988,8000,8002,8003,8004,8005]

#run simulations that might have been interrupted while running, haven't finished
for fill in fills:
    run_sims_not_finished(fill)


#Runs all simulations provided, re-run corrupted simulations
def run_failed_sims(json_file_with_sims):
    with open(json_file_with_sims, "r") as json_file:
        sim_names = json.load(json_file) 
    sim_folder = "/home/HPC/vesedlak/sim_workspace/matthew/simulations/"  
    for name in sim_names:
        sim_path = sim_folder + name
        os.chdir(sim_path)
        os.system("sbatch job.job")

failed_fills =[] #[7774, 7789, 7793, 7795, 7797, 7819, 7938]

list_of_fails = []
for fill in failed_fills:
    list_of_fails.append(f"failed_sim_heatloads_{fill}.json")

for fail in list_of_fails:
    file_loc = "/home/HPC/vesedlak/sim_workspace/matthew/config/"
    run_failed_sims(file_loc+fail)



