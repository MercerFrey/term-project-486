from pydoc import visiblename
from turtle import title
import matplotlib.pyplot as plt
import numpy as np
import json

def print_plot(plot_type, filename, **kwargs):
    if plot_type != "target_speeds": 
        with open(filename, 'r') as f:
            data = np.array(json.load(f), dtype=object)

    if plot_type == "target_speeds":

        fig, axs = plt.subplots(1, 3)

        axs[0].plot(kwargs["ego_speed"], kwargs["v1_speed"], "o")
        axs[0].set(xlabel="ego_speed", ylabel="v1_speed")

        axs[1].plot(kwargs["ego_speed"], kwargs["v2_speed"], "o")
        axs[1].set(xlabel="ego_speed", ylabel="v2_speed")

        axs[2].plot(kwargs["v1_speed"], kwargs["v2_speed"], "o")
        axs[2].set(xlabel="v1_speed", ylabel="v2_speed")

        for ax in axs:
            ax.yaxis.tick_right()

        plt.tight_layout()

    elif plot_type == "max_histogram":
        fig, axs = plt.subplots(tight_layout = True)
        axs.hist(data, rwidth=0.8)
        axs.set(xlabel=r'Max Lateral Acceleration $m/s^{2}$', ylabel="Scenario Count")
        axs.grid(visible = True, color ='grey',
            linestyle ='-.', linewidth = 0.5,
            alpha = 0.6)
    
    elif plot_type == "top_5":
        fig, axs = plt.subplots(tight_layout = True)
        axs.plot(data[kwargs["index"]])
        axs.set(xlabel="Tick", ylabel=r'Lateral Acceleration $m/s^{2}$',
            title=f'Scenario {kwargs["index"]+1}')
        axs.grid(visible = True, color ='grey',
            linestyle ='-.', linewidth = 0.5,
            alpha = 0.6)
        
        ymax = max(data[kwargs["index"]])
        xmax = data[kwargs["index"]].index(ymax)
        axs.annotate(f'Max Lateral Acceleration\n{round(ymax,3)}', xy=(xmax, ymax), xytext=(xmax + 10, ymax-1))
    
    save_file = f'docs/plots/{filename.split(".")[0]}.png'
    if "index" in kwargs:
        save_file = f'{save_file.split(".")[0]}_{kwargs["index"]}.png' 

    plt.savefig(save_file)
    plt.show()

# print_plot("straight_max_lat_acc.json", "max_lat_acc_histogram")
# for i in range(5):
#     print_plot("straight_critical_lat_acc_5.json", "top_5_critical_lateral_acceleration_history", index=i)

