import os

fills = [7880,7881,7902,7904,7905]

for fill in fills:
    os.system(f"rm -r /home/HPC/vesedlak/sim_workspace/matthew/simulations/*{fill}*")
    print(f"Removing fill {fill}")
