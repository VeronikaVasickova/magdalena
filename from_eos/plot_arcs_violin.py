import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import LHCMeasurementTools.mystyle as ms
import seaborn as sns

plt.rcParams.update({'font.size':14})

result_folder = "/eos/project/e/ecloud-simulations/vesedlak/results/"
fig_folder = "/eos/project/e/ecloud-simulations/vesedlak/figures/"

ms_size = 3
figure_size = (9,6)

df = pd.DataFrame.from_dict(json.load(open(result_folder + "hcells_2D_df.json","r")))
df.index = df.index.map(int)
df = df.sort_index()
df = df.T
df = df.rename(columns = {7938 : 'SEY'})
df['Arc'] = np.nan
df['Device'] = np.nan

counter_12 = 0
counter_23 = 0
counter_34 = 0
counter_45 = 0
counter_56 = 0
counter_67 = 0
counter_78 = 0
counter_81 = 0
cells_12 = 0
cells_23 = 0
cells_34 = 0
cells_45 = 0
cells_56 = 0
cells_67 = 0
cells_78 = 0
cells_81 = 0



for key in df.index:
    print(key)
    if "SEY_" in key and "DIP" in key and ("R1" in key or "L2" in key):
        df.loc[key,'Arc'] = 'Arc 12'
        df.loc[key,'Device'] = 'Dipole'
        cells_12 +=1
    if "SEY_" in key and "DIP" in key and ("R2" in key or "L3" in key):
        df.loc[key,'Arc'] = 'Arc 23'
        df.loc[key,'Device'] = 'Dipole'
        cells_23 +=1
    if "SEY_" in key and "DIP" in key  and ("R3" in key or "L4" in key):
        df.loc[key,'Arc'] = 'Arc 34'
        df.loc[key,'Device'] = 'Dipole'
        cells_34 +=1
    if "SEY_" in key and "DIP" in key and ("R4" in key or "L5" in key):
        df.loc[key,'Arc'] = 'Arc 45'
        df.loc[key,'Device'] = 'Dipole'
        cells_45 +=1
    if "SEY_" in key and "DIP" in key and ("R5" in key or "L6" in key):
        df.loc[key,'Arc'] = 'Arc 56'
        df.loc[key,'Device'] = 'Dipole'
        cells_56 +=1
    if "SEY_" in key and "DIP" in key and ("R6" in key or "L7" in key):
        df.loc[key,'Arc'] = 'Arc 67'
        df.loc[key,'Device'] = 'Dipole'
        cells_67 +=1
    if "SEY_" in key and "DIP" in key and ("R7" in key or "L8" in key):
        df.loc[key,'Arc'] = 'Arc 78'
        df.loc[key,'Device'] = 'Dipole'
        cells_78 +=1
    if "SEY_" in key and "DIP" in key and ("R8" in key or "L1" in key):
        df.loc[key,'Arc'] = 'Arc 81'
        df.loc[key,'Device'] = 'Dipole'
        cells_81 +=1
    if "SEY_" in key and "QUAD" in key and ("R1" in key or "L2" in key):
        df.loc[key,'Arc'] = 'Arc 12'
        df.loc[key,'Device'] = 'Quadrupole'
        if df.loc[key, 'SEY'] > 1.7 :
            counter_12 +=1
    if "SEY_" in key and "QUAD" in key and ("R2" in key or "L3" in key):
        df.loc[key,'Arc'] = 'Arc 23'
        df.loc[key,'Device'] = 'Quadrupole'
        if df.loc[key, 'SEY'] > 1.7 :
            counter_23 +=1
    if "SEY_" in key and "QUAD" in key  and ("R3" in key or "L4" in key):
        df.loc[key,'Arc'] = 'Arc 34'
        df.loc[key,'Device'] = 'Quadrupole'
        if df.loc[key, 'SEY'] > 1.7 :
            counter_34 +=1
    if "SEY_" in key and "QUAD" in key and ("R4" in key or "L5" in key):
        df.loc[key,'Arc'] = 'Arc 45'
        df.loc[key,'Device'] = 'Quadrupole'
        if df.loc[key, 'SEY'] > 1.7 :
            counter_45 +=1
    if "SEY_" in key and "QUAD" in key and ("R5" in key or "L6" in key):
        df.loc[key,'Arc'] = 'Arc 56'
        df.loc[key,'Device'] = 'Quadrupole'
        if df.loc[key, 'SEY'] > 1.7 :
            counter_56 +=1
    if "SEY_" in key and "QUAD" in key and ("R6" in key or "L7" in key):
        df.loc[key,'Arc'] = 'Arc 67'
        df.loc[key,'Device'] = 'Quadrupole'
        if df.loc[key, 'SEY'] > 1.7 :
            counter_67 +=1
    if "SEY_" in key and "QUAD" in key and ("R7" in key or "L8" in key):
        df.loc[key,'Arc'] = 'Arc 78'
        df.loc[key,'Device'] = 'Quadrupole'
        if df.loc[key, 'SEY'] > 1.7 :
            counter_78 +=1
    if "SEY_" in key and "QUAD" in key and ("R8" in key or "L1" in key):
        df.loc[key,'Arc'] = 'Arc 81'
        df.loc[key,'Device'] = 'Quadrupole'
        if df.loc[key, 'SEY'] > 1.7 :
            counter_81 +=1


print(f'Arc 12: number of cells {cells_12}, quadrupoles with SEY > 1.7 {counter_12}')
print(f'Arc 23: number of cells {cells_23}, quadrupoles with SEY > 1.7 {counter_23}')
print(f'Arc 34: number of cells {cells_34}, quadrupoles with SEY > 1.7 {counter_34}')
print(f'Arc 45: number of cells {cells_45}, quadrupoles with SEY > 1.7 {counter_45}')
print(f'Arc 56: number of cells {cells_56}, quadrupoles with SEY > 1.7 {counter_56}')
print(f'Arc 67: number of cells {cells_67}, quadrupoles with SEY > 1.7 {counter_67}')
print(f'Arc 78: number of cells {cells_78}, quadrupoles with SEY > 1.7 {counter_78}')
print(f'Arc 81: number of cells {cells_81}, quadrupoles with SEY > 1.7 {counter_81}')



fig1 = plt.figure(1, figsize=figure_size)
ax1 = fig1.add_subplot(111)

ax1.grid(visible=True, axis='y')

ax1 = sns.violinplot(x='Arc', y='SEY', hue='Device', data=df, split=True, order=['Arc 12','Arc 23','Arc 34','Arc 45','Arc 56','Arc 67','Arc 78','Arc 81'],
        scale='count', scale_hue=False, bw=.02, pallete='bright', inner=None)
ax1.legend(loc="upper center", prop={'size':14}, ncol=2, bbox_to_anchor=(0.5,1.0))
#ax1.grid(visible=True, axis='y')
ax1.set_ylim(0.95,2.4)
#fig1.subplots_adjust(left=.1, right=.76, hspace=.28, top=.95)

plt.show()

#fig1 = plt.figure(1, figsize=figure_size)
#ax1 = fig1.add_subplot(111)

#data12 = []
#for key in a_keys:
#    ax1.plot(df.index, df[key],'o', label=f"{key[4:7]}", ms=ms_size)

#ax1.violinplot([s12_keys,s23_keys,s34_keys,s45_keys,s56_keys,s67_keys,s78_keys,s81_keys])

#ax1.legend(loc="upper left", bbox_to_anchor=(1.1,1.05), prop={'size':14})
#ax1.set_xlabel("Sectors", fontsize=14)
#ax1.grid(visible=True)
#ax1.set_ylabel("SEY", fontsize=14)
#ax1.set_ylim(1.0, 2.3)
#ax1.set_title("Sectors")
#ax1.xaxis.set_major_locator(plt.MaxNLocator(10))
#fig1.subplots_adjust(left=.1, right=.76, hspace=.28, top=.95)
fig1.savefig(fig_folder+"violin_arcs.png")

#plt.show()

