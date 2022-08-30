import os
import glob
import get_heat
import json
import numpy as np



def get_heatloads(fill):
    hl_dict = {}
    fails=[]#simulations that have nan heatload
    #discard_vals = [] #simulations where one is nan -> both magnets and beams nedd to be discarded
    sim_folder = "/eos/project/e/ecloud-simulations/vesedlak/fin_sims/"
    existing_folders = glob.glob(sim_folder+f"LHC*{fill}*")
    sims = []
    for fol in existing_folders:
        sims.append(fol.split("/")[-1])
    
    for ii, sim in enumerate(sims):
        split_name = sim.split("_")
        if split_name[0] !="LHC":
            continue
        if fill != int(split_name[6][-4:]):
            continue
        magnet = split_name[1]
        sey = float(split_name[3][-4:])
        beam = int(split_name[4][-1])
        t_obs = float(split_name[7][1:-1])
        hl = get_heat.get_simulated_heatload(magnet, sey, beam, fill, t_obs)
        #hl_dict[sim] = hl
        if np.isnan(hl):
            fails.append(sim)
            hl_dict[sim] = -1000
        else:
            hl_dict[sim] = hl

        print(f"{ii}/{len(sims)}")

    json.dump(hl_dict, open(f"/eos/project/e/ecloud-simulations/vesedlak/output/sim_heatloads_{fill}.json","w"), sort_keys=True, indent=4)
    json.dump(fails, open(f"/eos/project/e/ecloud-simulations/vesedlak/output/failed_sim_heatloads_{fill}.json","w"), sort_keys=True, indent=4)
    
#for fill in [7938]:
#    get_heatloads(fill)

#get_heatloads(7749)
