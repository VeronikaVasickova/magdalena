import glob
import os
import json

#keep adding to an external file - list of sims that have been compied 
#check that a sim is not in the list fist and then do the other if cond


def copy_new(fills):
    config_path = "/home/HPC/vesedlak/sim_workspace/matthew/config/"
    sim_folder = "/home/HPC/vesedlak/sim_workspace/matthew/simulations/"
    finished_folder = "/home/HPC/vesedlak/sim_workspace/matthew/finished_sims/"

    for fill in fills:
        sim_name = f"LHC*Fill{fill}*"
        existing_folders = glob.glob(sim_folder+sim_name)
    
        copied_sims=[] # newly copied simulations
    
        #Open the file with names of already transferred simulations
        file_dirs = open(config_path+"copied_sims.txt", "r")
        folders =  file_dirs.read()
        transferred = folders.split(" ") #simulations that have been copied previously and written into a file
    
        #Check if a simulation is finished and copy it to the folder with finished simulations
        for fol in existing_folders:
            logfile_path = fol+"/logfile.txt"
            name = fol.split("/")[-1]
            #check if this folder has already been copied, don't do it again
            if name in transferred:
                continue 
            #check if the simulation has been finished and copy it to the tranfering directory
            if os.path.exists(logfile_path) and "3564/3565" in open(logfile_path, "r").readlines()[-1]:
                #os.system(f"mkdir {finished_folder}{name}")
                os.system(f"cp -r {fol} {finished_folder}{name}")
                copied_sims.append(name+" ") #need a space to split on later
                print(f"Copied {name}")

#copy the whole folder with finished simulations and delete them afterwards
#os.system(f"scp -r {finished_folder}* vesedlak@lxplus.cern.ch:/eos/project/e/ecloud-simulations/vesedlak/fin_sims/")
#os.system(f"rm -r {finished_folder}*")

    #Write copied folders into a file, next time this program knows that these have been transferred already
        file_with_folders = open(config_path+"copied_sims.txt", 'a') #'a' appends at the end of an existing file
        file_with_folders.writelines(copied_sims)
        file_with_folders.close()
    return

def copy_priority(fills):
    config_path = "/home/HPC/vesedlak/sim_workspace/matthew/config/"
    sim_folder = "/home/HPC/vesedlak/sim_workspace/matthew/simulations/"
    finished_folder = "/home/HPC/vesedlak/sim_workspace/matthew/finished_sims/"

    for fill in fills:
        sim_name = f"LHC*Fill{fill}*"
        existing_folders = glob.glob(sim_folder+sim_name)

        #Check if a simulation is finished and copy it to the folder with finished simulations
        for fol in existing_folders:
            logfile_path = fol+"/logfile.txt"
            name = fol.split("/")[-1]
            #check if the simulation has been finished and copy it to the tranfering directory
            if os.path.exists(logfile_path) and "3564/3565" in open(logfile_path, "r").readlines()[-1]:
                #os.system(f"mkdir {finished_folder}{name}")
                os.system(f"cp -r {fol} {finished_folder}{name}")
                print(f"Copied {name}")

def copy_re_submitted(fill):
    sim_folder = "/home/HPC/vesedlak/sim_workspace/matthew/simulations/"
    finished_folder = "/home/HPC/vesedlak/sim_workspace/matthew/finished_sims/"
    
    with open(f"/home/HPC/vesedlak/sim_workspace/matthew/config/failed_sim_heatloads_{fill}.json", "r") as json_file:
        sim_names = json.load(json_file)
    
    for name in sim_names:
        sim_path = sim_folder + name
        logfile_path = sim_path + "/logfile.txt"
        if os.path.exists(logfile_path) and "3564/3565" in open(logfile_path, "r").readlines()[-1]:
            os.system(f"cp -r {sim_path} {finished_folder}{name}")
            print(f"Copied {name}")


#list_of_fails = ["failed_sim_heatloads_7774.json","failed_sim_heatloads_7789.json","failed_sim_heatloads_7793.json","failed_sim_heatloads_7795.json","failed_sim_heatloads_7797.json","failed_sim_heatloads_7819.json"]

#fills = [7774, 7789, 7793, 7795, 7797, 7819]
fills = [7774,7789,7793,7795,7797,7800,7819,7776,7749,7790,7799,7829,7878,7879,7880,7881,7902,7904,7906,7907,7909,7932,7933,7934,7935,7936,7937,7939,7940,7943,7944,7945,7949,7950,7951,7952,7953,7954,7955,7956,7983,7984,7985,7986,7987,7988,8000,8002,8003,8004,8005]


#for fill in fills:
#    copy_re_submitted(fill)
copy_new(fills)

#failed_fills =[7774, 7789, 7793, 7795, 7797, 7819, 7938]
#high_sey_fills = [7749,7774,7776]

#copy_priority(high_sey_fills)
