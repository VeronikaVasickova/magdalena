import numpy as np
import matplotlib.pyplot as plt
import get_heat

magnet_dip = "ArcDipReal"
magnet_quad = "ArcQuadReal"

sey=2.1
beam=1
fill=7789
t=1.5

dip_length = 14.3*3
quad_length = 3.1

#heatload_dip = get_heat.get_simulated_heatload(magnet, sey, beam, fill, t)
#print(heatload_dip*dip_length)

seys = np.arange(1.00,2.21, 0.05)


#heatload pplot
heatload_dip = []
heatload_quad = []
total_hl =[]


for s in seys:
    hld =  get_heat.get_simulated_heatload(magnet_dip, s, beam, fill, t)
    hldl = hld*dip_length
    heatload_dip.append(hldl)
    hlq =  get_heat.get_simulated_heatload(magnet_quad, s, beam, fill, t)
    hlql = hlq*quad_length
    heatload_quad.append(hlql)
    total_hl.append(hldl+hlql)

fig1 = plt.figure()
ax1 = fig1.add_subplot(111)
ax1.plot(seys, heatload_dip, "b.-")
ax1.set_xlabel("SEY delta_max [dimensionless]")
ax1.set_ylabel("Heatload [W]")
ax1.set_title(f"Simulated heatload in dipoles, beam{beam}, fill{fill},time{t}")

fig2 = plt.figure()
ax2 = fig2.add_subplot(111)
ax2.plot(seys, heatload_quad, "b.-")
ax2.set_xlabel("SEY delta_max [dimensionless]")
ax2.set_ylabel("Heatload [W]")
ax2.set_title(f"Simulated heatload in quadrupoles, beam{beam}, fill{fill},time{t}")

fig3 = plt.figure()
ax3 = fig3.add_subplot(111)
ax3.plot(seys, total_hl, "b.-")
ax3.set_xlabel("SEY delta_max [dimensionless]")
ax3.set_ylabel("Heatload [W]")
ax3.set_title(f"Simulated heatload combined, beam{beam}, fill{fill},time{t}")


plt.show()

