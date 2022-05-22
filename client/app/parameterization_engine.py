from smt.sampling_methods import Random
import numpy as np
import matplotlib.pyplot as plt
import json
import argparse

import run_simulation
import print_plot 

# pick 25 appropriate samples from 100 samples.
def sample_25_with_limits(xlimits):
    sample_size = 100
    sampling = Random(xlimits=xlimits)
    x = sampling(sample_size)

    return x[abs(x[:, 0] - x[:, 1] < 5)][:25]


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


def write_scenario_speeds(scenario_filename, scenario, speed_list):
    for i in range(len(speed_list)):
        scenario["hero"]["target_speed"]["value"] = speed_list[i][0]
        scenario["other1"]["target_speed"]["value"] = speed_list[i][1]
        scenario["other2"]["target_speed"]["value"] = speed_list[i][2]

        write_to_json(scenario, "par/par_{}_{}.json".format(scenario_filename, i))

def main(): 
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "--scenario",
        metavar="straight",
        default="straight",
        help="Straight or curved (default: straight)",
    )
    
    scenario_type = argparser.parse_args().scenario
    print(scenario_type)
    
    args = {
        'host': '127.0.0.1',
        'port': 2000,
        'tm_port': 8000, 
        'timeout': 2.0, 
        'res': '1280x720', 
        'filter': 'vehicle.audi.*', 
        'scenario': 'curved.json', 
        'description': 'BounCMPE CarlaSim 2D Visualizer',
        'width': 1280,
        'height': 720
        }


    scenario, xlimits = read_scenario_speeds(f'{scenario_type}.json')
    samples = sample_25_with_limits(xlimits)

    ego_speed = samples[:, 0]
    v1_speed = samples[:, 1]
    v2_speed = samples[:, 2]
    

    #write_scenario_speeds(scenario_type, scenario, samples)
    
    #args["filename"] = f'{scenario_type}.json'
    #run_simulation.game_loop(args)


    # print plots and save them
    # no file for target speeds
    print_plot.print_plot("target_speeds", f'{scenario_type}_target_speeds.json',
                ego_speed=ego_speed,
                v1_speed=v1_speed,
                v2_speed=v2_speed)
    print_plot.print_plot("max_histogram", f'{scenario_type}_max_lat_acc.json')
    for i in range(5):
        print_plot.print_plot("top_5", f'{scenario_type}_critical_lat_acc_5.json', index=i)


main()