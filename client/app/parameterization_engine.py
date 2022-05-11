from smt.sampling_methods import Random
import numpy as np
import matplotlib.pyplot as plt
import json
import argparse
import subprocess

# pick 25 appropriate samples from 100 samples.
def sample_25_with_limits(xlimits):
    sample_size = 100
    sampling = Random(xlimits=xlimits)
    x = sampling(sample_size)

    return x[abs(x[:, 0] - x[:, 1] < 5)][:25]

def plot(ego_speed, v1_speed, v2_speed):
    
    fig, axs = plt.subplots(1, 3)

    axs[0].plot(ego_speed, v1_speed, "o")
    axs[0].set(xlabel="ego_speed", ylabel="v1_speed")

    axs[1].plot(ego_speed, v2_speed, "o")
    axs[1].set(xlabel="ego_speed", ylabel="v2_speed")

    axs[2].plot(v1_speed, v2_speed, "o")
    axs[2].set(xlabel="v1_speed", ylabel="v2_speed")

    for ax in axs:
        ax.yaxis.tick_right()

    plt.tight_layout()
    plt.show()

# read scenario_1.json and collects the min max values
def read_scenario_speeds(filename):
    with open(filename, 'r') as f:
        scenario = json.load(f)

    xlimits = np.array([])
    for _, attributes in scenario.items():
        temp = [attributes["target_speed"]["min"], attributes["target_speed"]["max"]]
        
        if xlimits.size == 0:
            xlimits = np.append(xlimits, temp)
        else:
            xlimits = np.vstack((xlimits, temp))
    
    return scenario, xlimits


def write_to_json(new_scenario, filename):
    with open(filename, 'w') as f:
        json.dump(new_scenario, f, indent=4)


def write_scenario_speeds(scenario, speed_list):
    for i in range(len(speed_list)):
        scenario["hero"]["target_speed"]["value"] = speed_list[i][0]
        scenario["other1"]["target_speed"]["value"] = speed_list[i][1]
        scenario["other2"]["target_speed"]["value"] = speed_list[i][2]

        write_to_json(scenario, "par/par_scenario_{}.json".format(i))

def main():
    argparser = argparse.ArgumentParser()

    argparser.add_argument(
        "--filename",
        metavar="f",
        default="scenario_1.json",
        help="scenario file that will be parameterized",
    )

    args = argparser.parse_args()

    scenario, xlimits = read_scenario_speeds(args.filename)
    samples = sample_25_with_limits(xlimits)

    ego_speed = samples[:, 0]
    v1_speed = samples[:, 1]
    v2_speed = samples[:, 2]
    
    plot(ego_speed, v1_speed, v2_speed)
    write_scenario_speeds(scenario, samples)
    
    for i in range(25):
        try:
            p = subprocess.Popen("python client/run.py --scenario par/par_scenario_{}.json".format(i), shell=True)
            p.wait()
        except Exception as e:
            pass
main()