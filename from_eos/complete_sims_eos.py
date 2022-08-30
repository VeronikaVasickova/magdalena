import glob
import os


#checks how many simulations of each fill have finished, and also writes out which haven't
def find_incomplete_sims(fill):
    sim_name = f"LHC*Fill{fill}*"
    sim_folder = "/eos/project/e/ecloud-simulations/vesedlak/fin_sims/"
    existing_folders = glob.glob(sim_folder+sim_name)
    #total = len(existing_folders)

    counter = 0

    for fol in existing_folders:
        logfile_path = fol+"/logfile.txt"
        if os.path.exists(logfile_path) and "3564/3565" in open(logfile_path, "r").readlines()[-1]:
            counter = counter+1
        else:
            print(f"{fol} is not finished")
    print(f"Completed {counter} simulations for fill number {fill}")


fills = [7774,7789,7793,7795,7797,7800,7819,7776,7749,7938, 7790,7799,7829,7878,7879,7880,7881,7902,7904,7905,7906,7907,7909,7932,7933,7934,7935,7936,7937,7939,7940,7943,7944,7945,7949,7950,7951,7952,7953,7954,7955,7956,7983,7984,7985,7986,7987,7988,8000,8002,8003,8004,8005]

for fill in fills:
    find_incomplete_sims(fill)
