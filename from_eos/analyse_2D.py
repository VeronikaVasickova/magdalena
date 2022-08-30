import glob
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

#fethches dataframes for each fill and time
def get_rows(fill):
    with open(f'/eos/project/e/ecloud-simulations/vesedlak/results/result_sey_2D_dip_fill{fill}.json', 'r') as json_file1:
        sey_d = json.load(json_file1)
    with open(f'/eos/project/e/ecloud-simulations/vesedlak/results/result_sey_2D_quad_fill{fill}.json', 'r') as json_file2:
        sey_q = json.load(json_file2)
    with open(f'/eos/project/e/ecloud-simulations/vesedlak/results/result_err_2D_dip_left_fill{fill}.json', 'r') as json_file3:
        err_d_l = json.load(json_file3)
    with open(f'/eos/project/e/ecloud-simulations/vesedlak/results/result_err_2D_dip_right_fill{fill}.json', 'r') as json_file4:
        err_d_r = json.load(json_file4)
    with open(f'/eos/project/e/ecloud-simulations/vesedlak/results/result_err_2D_quad_left_fill{fill}.json', 'r') as json_file5:
        err_q_l = json.load(json_file5)
    with open(f'/eos/project/e/ecloud-simulations/vesedlak/results/result_err_2D_quad_right_fill{fill}.json', 'r') as json_file6:
        err_q_r = json.load(json_file6)
    #go through different kinds of devices
    big_keys = list(sey_d.keys())
    rows = {}
    for big_key in big_keys:
        rows[big_key] = get_row(sey_d, sey_q, err_d_l, err_d_r, err_q_l, err_q_r, big_key, fill)
    #need to concatenate all specials together
    new_rows = {}
    special_row = pd.DataFrame()
    for key in list(rows.keys()):
        if key in ["AVG_ARC", "half-cells"]:
            new_rows[key] = rows[key]
        elif key in ["special_D2B1", "special_D3B1", "special_D4B1", "special_Q1B1","special_D2B2", "special_D3B2", "special_D4B2", "special_Q1B2"]:
            sub_df = pd.DataFrame(rows[key], index = [fill])
            special_row = special_row.join(sub_df, how='right')
            #print(special_row)
        else:
            print(f"unknown key: {key}")
    #print(special_row)
    new_rows["special"] = special_row
    return new_rows

#returns 1 row dataframe with values for the fill and section specified
def get_row(sey_d, sey_q, err_d_l, err_d_r, err_q_l, err_q_r, big_key, fill):        
    #load data into df
    SD = pd.DataFrame(sey_d[big_key], index = [fill])
    SQ = pd.DataFrame(sey_q[big_key], index = [fill])
    EDL = pd.DataFrame(err_d_l[big_key], index = [fill])
    EDR = pd.DataFrame(err_d_r[big_key], index = [fill])
    EQL = pd.DataFrame(err_q_l[big_key], index = [fill])
    EQR = pd.DataFrame(err_q_r[big_key], index = [fill])
    #rename columns
    SD = SD.add_prefix('SEY_DIP_')
    SQ = SQ.add_prefix('SEY_QUAD_')
    EDL = EDL.add_prefix('ERR_DIP_L_')
    EDR = EDR.add_prefix('ERR_DIP_R_')
    EQL = EQL.add_prefix('ERR_QUAD_L_')
    EQR = EQR.add_prefix('ERR_QUAD_R_')
    #join dfs
    fill_df = SD.join(SQ)
    fill_df = fill_df.join(EDL)
    fill_df = fill_df.join(EDR)
    fill_df = fill_df.join(EQL)
    fill_df = fill_df.join(EQR)
    return fill_df

#creates big dataframes for each section, for fills and times specified
def save_dfs(fills):
    arcs_df = pd.DataFrame()
    hcells_df = pd.DataFrame()
    specials_df = pd.DataFrame()
    #need to create more dataframes when we know more categories
    for fill in fills:
        rows_dict = get_rows(fill)
        try:
            arcs_df = pd.concat([arcs_df, rows_dict["AVG_ARC"]])
            hcells_df = pd.concat([hcells_df, rows_dict["half-cells"]])
            specials_df = pd.concat([specials_df, rows_dict["special"]])
        except:
            print(f"couldn't get data for fill {fill}")
    #save dfs
    arcs_df.to_json(open("/eos/project/e/ecloud-simulations/vesedlak/results/arcs_2D_df.json","w"))
    hcells_df.to_json(open("/eos/project/e/ecloud-simulations/vesedlak/results/hcells_2D_df.json","w"))
    specials_df.to_json(open("/eos/project/e/ecloud-simulations/vesedlak/results/specials_2D_df.json","w"))

#loads data from pre-saved files and returns dataframes
def load_dfs():
    arcs = pd.read_json(r"/eos/project/e/ecloud-simulations/vesedlak/results/arcs_2D_df.json")
    hcells = pd.read_json(r"/eos/project/e/ecloud-simulations/vesedlak/results/hcells_2D_df.json")
    specs = pd.read_json(r"/eos/project/e/ecloud-simulations/vesedlak/results/specials_2D_df.json")
    return arcs, hcells, specs

def load_df(name_of_file):
    name = f"/eos/project/e/ecloud-simulations/vesedlak/results/{name_of_file}"
    df = pd.read_json(name)
    return df


#plot sey as a fcn of fill
#def plot_dfs(dfs):
#    for df in dfs:
#        df.plot(xlabel="Fill number", ylabel="SEY", title = "Evolution of SEY during scrubbing")
#        plt.legend(bbox_to_anchor=(1,1))#, loc="upper left")
#        plt.show()

#time_fill = [[7800,2.6],[7749,1.0],[7793,2.0],[7819,2.1],[7797,1.8]]
#save_dfs(time_fill)

def plot_and_save(arcs, hcells, specials, name_to_save):
    arc_seys = arcs.filter(regex='^SEY_', axis=1)
    arc_seys.plot(xlabel="Fill number", ylabel="SEY", title = "Evolution of SEY in arcs during scrubbing", 
        xticks = arc_seys.index.values.tolist(), marker='.', linestyle = 'None')
    plt.xticks(rotation = 45)
    plt.savefig(f"/eos/project/e/ecloud-simulations/vesedlak/results/Arcs_{name_to_save}.png")

    hcells_seys = hcells.filter(regex='^SEY_', axis=1)
    hcells_seys.plot(xlabel="Fill number", ylabel="SEY", title = "Evolution of SEY in halfcells during scrubbing",
        xticks = hcells_seys.index.values.tolist(), marker='.', linestyle = 'None')
    plt.xticks(rotation = 45)
    plt.savefig(f"/eos/project/e/ecloud-simulations/vesedlak/results/Halfcells_{name_to_save}.png")

    special_seys = specials.filter(regex='^SEY_', axis=1)
    special_seys.plot(xlabel="Fill number", ylabel="SEY", title = "Evolution of SEY in special cells during scrubbing",
        xticks = special_seys.index.values.tolist(), marker='.', linestyle = 'None')
    plt.xticks(rotation = 45)
    plt.savefig(f"/eos/project/e/ecloud-simulations/vesedlak/results/Specials_{name_to_save}.png")
    plt.show()
    
def plot_individuals(indiv_df,name_to_save):
    pp = PdfPages(f"/eos/project/e/ecloud-simulations/vesedlak/results/{name_to_save}.pdf")
    indiv_seys = indiv_df.filter(regex='^SEY_', axis=1)
    for col in indiv_seys.columns:
        plt.plot(indiv_seys.index.values.tolist(), indiv_seys[col],  marker='.', linestyle = 'None')
        plt.xlabel("Fill number")
        plt.ylabel("SEY")
        plt.title(f"Evolution of SEY in {col} during scrubbing")
        plt.xticks(indiv_seys.index.values.tolist(), rotation = 45)
        plt.savefig(pp, format='pdf')
        plt.close()
    pp.close()

#save_dfs([7938])
#arcs, hcells, specials = load_dfs()
#plot_individuals(specials,"sey_specials_first_5_fills")
#plot_and_save(arcs, hcells, specials, "7938_all_times")
#

