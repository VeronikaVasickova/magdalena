import glob
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

#fethches dataframes for each fill and time
def get_rows(fill, time):
    with open(f'/eos/project/e/ecloud-simulations/vesedlak/results/result_sey_sec_fill{fill}_T{time:.2f}.json', 'r') as json_file1:
        sey_dict = json.load(json_file1)
    with open(f'/eos/project/e/ecloud-simulations/vesedlak/results/result_err_sec_fill{fill}_T{time:.2f}.json', 'r') as json_file2:
        err_dict = json.load(json_file2)
    #go through different kinds of devices
    big_keys = list(sey_dict.keys())
    rows = {}
    for big_key in big_keys:
        rows[big_key] = get_row(sey_dict, err_dict, big_key, fill)
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
def get_row(sey_dict, err_dict, big_key, fill):        
    #load data into df
    sey_df = pd.DataFrame(sey_dict[big_key], index = [fill])
    err_df = pd.DataFrame(err_dict[big_key], index = [fill])
    #rename columns
    sey_df = sey_df.add_prefix('SEY_')
    err_df = err_df.add_prefix('ERR_')
    #join dfs
    fill_df = sey_df.join(err_df)
    return fill_df

#creates big dataframes for each section, for fills and times specified
def save_dfs(fill_time_pairs):
    arcs_df = pd.DataFrame()
    hcells_df = pd.DataFrame()
    specials_df = pd.DataFrame()
    #need to create more dataframes when we know more categories
    for pair in fill_time_pairs:
        rows_dict = get_rows(pair[0],pair[1])
        try:
            arcs_df = pd.concat([arcs_df, rows_dict["AVG_ARC"]])
            hcells_df = pd.concat([hcells_df, rows_dict["half-cells"]])
            specials_df = pd.concat([specials_df, rows_dict["special"]])
        except:
            print(f"couldn't get data for fill {pair[0]}, time {pair[1]}")
    #save dfs
    arcs_df.to_json(open("/eos/project/e/ecloud-simulations/vesedlak/results/arcs_df.json","w"))
    hcells_df.to_json(open("/eos/project/e/ecloud-simulations/vesedlak/results/hcells_df.json","w"))
    specials_df.to_json(open("/eos/project/e/ecloud-simulations/vesedlak/results/specials_df.json","w"))

#loads data from pre-saved files and returns dataframes
def load_dfs():
    arcs = pd.read_json(r"/eos/project/e/ecloud-simulations/vesedlak/results/arcs_df.json")
    hcells = pd.read_json(r"/eos/project/e/ecloud-simulations/vesedlak/results/hcells_df.json")
    specs = pd.read_json(r"/eos/project/e/ecloud-simulations/vesedlak/results/specials_df.json")
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

arcs, hcells, specials = load_dfs()
plot_individuals(arcs,"sey_arcs_first_3_fills")

