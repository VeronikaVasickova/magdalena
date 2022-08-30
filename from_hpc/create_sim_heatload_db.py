import os
import get_heat
import json


sims = os.listdir("/home/HPC/vesedlak/sim_workspace/matthew/simulations")

hl_dict = {}

short_dict = {7774 : 1.60, 7789 : 1.5 , 7793 : 2 , 7795 : 2.3,7797 : 1.8, 7800 : 2.6 , 7819 : 2.1 }

for ii, sim in enumerate(sims):
    split_name = sim.split("_")
    if split_name[0] !="LHC":
        continue
    magnet = split_name[1]
    sey = float(split_name[3][-4:])
    beam = int(split_name[4][-1])
    if beam != 1:
        continue
    fill = int(split_name[6][-4:])
    t_obs = float(split_name[7][1:-1])
    #print(magnet, sey, beam,  fill, t_obs)
    if t_obs != short_dict[fill]:
        continue
    hl = get_heat.get_simulated_heatload(magnet, sey, beam, fill, t_obs)
    hl_dict[sim] = hl
    print(f"{ii}/{len(sims)}")


json.dump(hl_dict, open("sim_heatloads.json","w"), sort_keys=True, indent=4)

    

