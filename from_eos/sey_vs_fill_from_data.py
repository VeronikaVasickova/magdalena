import create_sim_heatload_db 
import sey_sections
import analyse_sections
import fills_times
import os
import numpy as np
import sey_2D_sections

#after results have been copied to fin_sims, run this and get plots
def get_sey_vs_fill_from_data(fill_time_pairs, err_for_measured_hl_in_percent, name_of_saved_graphs):
    for ii,pair in enumerate(fill_time_pairs):
        if pair[0] == 7938:
            continue
        create_sim_heatload_db.get_heatloads(pair[0])
        os.system(f"python measure_heatload_new.py --fill {pair[0]}  --t_obs_h {pair[1]} ")
        sey_sections.create_sey_db(pair[1], pair[0], err_for_measured_hl_in_percent)
        print(f'Created SEY database for fill {pair[0]}, time {pair[1]}, {ii}/{np.shape(fill_time_pairs)[0]}')
    analyse_sections.save_dfs(fill_time_pairs)


fill_time_pairs = fills_times.get_fill_time_pairs_one_time()
#fill_time_pairs = [[7749,1.0],[7774,1.6],[7776,3.1]]
get_sey_vs_fill_from_data(fill_time_pairs, 10, "run3")

def get_sey_vs_fill_from_sim_db(fill_time_pairs, err_for_measured_hl_in_percent, name_of_saved_graphs):
    for ii,pair in enumerate(fill_time_pairs):
        os.system(f"python measure_heatload_new.py --fill {pair[0]}  --t_obs_h {pair[1]} ")
        sey_sections.create_sey_db(pair[1], pair[0], err_for_measured_hl_in_percent)
        print(f'Created SEY database for fill {pair[0]}, time {pair[1]}, {ii}/{np.shape(fill_time_pairs)[0]}')
    analyse_sections.save_dfs(fill_time_pairs)
    arcs, hcells, specials = analyse_sections.load_dfs()
    #the plot should be in a diff script
    analyse_sections.plot_and_save(arcs, hcells, specials, name_of_saved_graphs)

#fill_time_pairs = fills_times.get_fill_time_pairs_one_time()
#get_sey_vs_fill_from_sim_db(fill_time_pairs, 10, "try2")


def get_2D_sey_from_sim_db(fill, times, err_for_measured_hl_in_percent):
    for time in times:
        os.system(f"python measure_heatload_new.py --fill {fill}  --t_obs_h {time} ")
    sey_2D_sections.main_2D_database(fill,  times, err_for_measured_hl_in_percent)

#fill = 7938
#times = fills_times.get_fill_time_dict()[fill]
#get_2D_sey_from_sim_db(fill, times, 10)
