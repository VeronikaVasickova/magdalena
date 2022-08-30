import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import LHCMeasurementTools.mystyle as ms
import fills_times

plt.rcParams.update({'font.size':14})

data_folder = "/eos/project/e/ecloud-simulations/vesedlak/output/"
fig_folder = "/eos/project/e/ecloud-simulations/vesedlak/figures/"

figure_size = (11.5,5)
ms_size=3

q1 = pd.DataFrame()
q2 = pd.DataFrame()

for pair in fills_times.get_fill_time_pairs_one_time():
    df1 = pd.DataFrame.from_dict(json.load(open(data_folder + f"meas_hl_Fill{pair[0]}_T{pair[1]:.2f}.json","r")))[['special_D2B1']].dropna(how='all')
    df1 = df1.T
    df1['Fill'] = pair[0]
    df1 = df1.set_index('Fill')
    
    df2 = pd.DataFrame.from_dict(json.load(open(data_folder + f"meas_hl_Fill{pair[0]}_T{pair[1]:.2f}.json","r")))[['special_D2B2']].dropna(how='all')
    df2 = df2.T
    df2['Fill'] = pair[0]
    df2 = df2.set_index('Fill')

    q1 = pd.concat([q1,df1])
    q2 = pd.concat([q2,df2])

q1 = q1.sort_index()
q2 = q2.sort_index()

fig1 = plt.figure(1, figsize=figure_size)
ax1 = fig1.add_subplot(111)

for col in q1.columns:
    if "13L5" in col:
        continue
    ax1.plot(q1.index, q1[col],'-o', ms=ms_size, label=f"D2B1_{col[6:10]}")

ax1.legend(loc="upper left", bbox_to_anchor=(1,1), prop={'size':14})
ax1.set_xlabel("Fill", fontsize=14)
ax1.grid(visible=True)
ax1.set_ylabel("Heatload [W]", fontsize=14)
ax1.set_title("Heatloads in D2, Beam 1")
ax1.xaxis.set_major_locator(plt.MaxNLocator(10))
fig1.subplots_adjust(left=.1, right=.76, hspace=.28, top=.95)
fig1.savefig(fig_folder+"hl_instr_d2_b1.png")


fig2 = plt.figure(2, figsize=figure_size)
ax2 = fig2.add_subplot(111)

for col in q2.columns:
    ax2.plot(q2.index, q2[col],'-o', label=f"D2B2_{col[6:10]}", ms=ms_size)

ax2.legend(loc="upper left", bbox_to_anchor=(1,1), prop={'size':14})
ax2.set_xlabel("Fill", fontsize=14)
ax2.set_ylabel("Heatload [W]", fontsize=14)
ax2.grid(visible=True)
ax2.set_title("Heatloads in D2, Beam 2")
ax2.xaxis.set_major_locator(plt.MaxNLocator(10))
fig2.subplots_adjust(left=.1, right=.76, hspace=.28, top=.95)
fig2.savefig(fig_folder+"hl_instr_d2_b2.png")


plt.show()

