import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import LHCMeasurementTools.mystyle as ms

plt.rcParams.update({'font.size':14})

result_folder = "/eos/project/e/ecloud-simulations/vesedlak/results/"
fig_folder = "/eos/project/e/ecloud-simulations/vesedlak/figures/"

ms_size = 3
figure_size = (11.5,5)

df = pd.DataFrame.from_dict(json.load(open(result_folder + "specials_df.json","r")))
df.index = df.index.map(int)
df = df.sort_index()

d3_keys = []
for key in df.columns:
    if "SEY_" in key and "_D3B1" in key:
        print(key)
        d3_keys.append(key)

d32_keys = []
for key in df.columns:
    if "SEY_" in key and "_D3B2" in key:
        print(key)
        d32_keys.append(key)


fig1 = plt.figure(1, figsize=figure_size)
ax1 = fig1.add_subplot(111)
for key in d3_keys:
    ax1.plot(df.index, df[key],'-o', label=f"D3B1_{key[10:14]}", ms=ms_size)

ax1.legend(loc="upper left", bbox_to_anchor=(1.1,1.05), prop={'size':14})
ax1.set_xlabel("Fill", fontsize=14)
ax1.grid(visible=True)
ax1.set_ylabel("SEY", fontsize=14)
ax1.set_ylim(1.0, 2.3)
ax1.set_title("Instrumented cells D3, Beam 1")
ax1.xaxis.set_major_locator(plt.MaxNLocator(10))
fig1.subplots_adjust(left=.1, right=.76, hspace=.28, top=.95)
fig1.savefig(fig_folder+"instr_d3_b1.png")


fig2 = plt.figure(2, figsize=figure_size)
ax2 = fig2.add_subplot(111)
for key in d32_keys:
    ax2.plot(df.index, df[key],'-o', label=f"D3B2_{key[10:14]}", ms=ms_size)

ax2.legend(loc="upper left", bbox_to_anchor=(1.1,1.05), prop={'size':14})
ax2.set_xlabel("Fill", fontsize=14)
ax2.set_ylabel("SEY", fontsize=14)
ax2.set_ylim(1.0, 2.3)
ax2.grid(visible=True)
ax2.set_title("Instrumented cells D3, Beam 2")
ax2.xaxis.set_major_locator(plt.MaxNLocator(10))
fig2.subplots_adjust(left=.1, right=.76, hspace=.28, top=.95)
fig2.savefig(fig_folder+"instr_d3_b2.png")


plt.show()

