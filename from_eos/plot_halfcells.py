import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import LHCMeasurementTools.mystyle as ms


plt.rcParams.update({'font.size':14})

result_folder = "/eos/project/e/ecloud-simulations/vesedlak/results/"
fig_folder = "/eos/project/e/ecloud-simulations/vesedlak/figures/"

ms_size = 3
figure_size = (7.5,5)

df = pd.DataFrame.from_dict(json.load(open(result_folder + "hcells_df.json","r")))
df.index = df.index.map(int)
df = df.sort_index()

a_keys = []
for key in df.columns:
    if "SEY_" in key:
        print(key)
        a_keys.append(key)

fig1 = plt.figure(1, figsize=figure_size)
ax1 = fig1.add_subplot(111)

for key in a_keys:
    ax1.plot(df.index, df[key],'o', label=f"{key[4:7]}", ms=ms_size)

#ax1.legend(loc="upper left", bbox_to_anchor=(1.1,1.05), prop={'size':14})
ax1.set_xlabel("Fill", fontsize=14)
ax1.grid(visible=True)
ax1.set_ylabel("SEY", fontsize=14)
ax1.set_ylim(1.0, 2.3)
#ax1.set_title("Sectors")
ax1.xaxis.set_major_locator(plt.MaxNLocator(10))
#fig1.subplots_adjust(left=.1, right=.76, hspace=.28, top=.95)
fig1.savefig(fig_folder+"halfcell.png")

plt.show()

