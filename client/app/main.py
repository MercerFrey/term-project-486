import argparse
import pygame
import carla
import json
import math

from .hud import InfoBar
#from .hero import Hero
from .world import World
from .input_control import InputControl
from .hero_with_controller import Hero
from .other_with_controller import Other

from .color import *

def game_loop(args):
    """Initialized, Starts and runs all the needed modules for No Rendering Mode"""
    try:

        # Init Pygame
        pygame.init()
        display = pygame.display.set_mode(
            (args['width'], args['height']), pygame.HWSURFACE | pygame.DOUBLEBUF
        )

        # Place a title to game window
        pygame.display.set_caption(args['description'])

        # Show loading screen
        font = pygame.font.Font(pygame.font.get_default_font(), 20)
        text_surface = font.render("Rendering map...", True, COLOR_WHITE)
        display.blit(
            text_surface,
            text_surface.get_rect(center=(args['width'] / 2, args['height'] / 2)),
        )
        pygame.display.flip()

        # Init
        hud = InfoBar(args['width'], args['height'])
        input_control = InputControl()
        world = World(args)

        actors = scenario_reader(args['scenario'])
        # For each module, assign other modules that are going to be used inside that module
        hud.start(world)
        input_control.start(hud, world)
        world.start(input_control)

        [actor.start(world) for actor in actors]

        # Game loop
        clock = pygame.time.Clock()

        # Max acc
        max_lat_acc = 0
        lat_acc_list = []
        
        while True:
            clock.tick_busy_loop(500)

            # Tick all modules
            world.tick(clock)
            [actor.tick(clock) for actor in actors]

            # Current lateral acceleration for other1
            curr_lat_acc = lat_acceleration_calculator(actors[1].actor, world.world.get_map())
            lat_acc_list.append(curr_lat_acc)
            if curr_lat_acc > max_lat_acc:
                max_lat_acc = curr_lat_acc
    

            hud.tick(clock)
            input_control.tick(clock)

            
            # Render all modules
            display.fill(COLOR_ALUMINIUM_4)
            world.render(display)
            hud.render(display)
            input_control.render(display)

            pygame.display.flip()

    except KeyboardInterrupt:
        print("\nCancelled by user. Bye!")

    finally:
        [actor.destroy() for actor in actors if actor is not None]

        return lat_acc_list, max_lat_acc



def scenario_reader(scenario_file):
    with open(scenario_file, 'r') as f:
        scenario = json.load(f)
    actors = []
    for actor_name, attributes in scenario.items():
        actor_spawn_point_location = carla.Location(**attributes["spawn_point"]["location"])
        actor_spawn_point_rotation = carla.Rotation(**attributes["spawn_point"]["rotation"])
        
        actor_way_points = [carla.Location(**point) for point in attributes["way_points"]]
        actor_target_speed = attributes["target_speed"]["value"]

        
        actor = None
        if actor_name == "hero":
            actor = Hero(
                location = actor_spawn_point_location,
                rotation = actor_spawn_point_rotation,
                waypoints = actor_way_points,
                target_speed_km = actor_target_speed,
                actor_role = actor_name,
            )
        else:
            actor = Other(
                location = actor_spawn_point_location,
                rotation = actor_spawn_point_rotation,
                waypoints = actor_way_points,
                target_speed_km = actor_target_speed,
                actor_role = actor_name,
            )
        actors.append(actor)

    return actors

# Return current lateral acceleration according to the road.
def lat_acceleration_calculator(actor, map):

    waypoint = map.get_waypoint(actor.get_location(), project_to_road=True, lane_type=carla.LaneType.Driving)
    road_yaw = waypoint.transform.rotation.yaw
    actor_yaw = actor.get_transform().rotation.yaw

    
    curr_acc_vector = actor.get_acceleration()
    curr_lat_acc= (abs(curr_acc_vector.x * math.sin(road_yaw - actor_yaw))
                + abs(curr_acc_vector.y * math.cos(road_yaw - actor_yaw))
                )

    return curr_lat_acc


def main():
    """Parses the arguments received from commandline and runs the game loop"""

    # Define arguments that will be received and parsed
    argparser = argparse.ArgumentParser()

    argparser.add_argument(
        "--host",
        metavar="H",
        default="127.0.0.1",
        help="IP of the host server (default: 127.0.0.1)",
    )
    argparser.add_argument(
        "-p",
        "--port",
        metavar="P",
        default=2000,
        type=int,
        help="TCP port to listen to (default: 2000)",
    )
    argparser.add_argument(
        "--tm-port",
        metavar="P",
        default=8000,
        type=int,
        help="Port to communicate with TM (default: 8000)",
    )
    argparser.add_argument(
        "--timeout",
        metavar="X",
        default=2.0,
        type=float,
        help="Timeout duration (default: 2.0s)",
    )
    argparser.add_argument(
        "--res",
        metavar="WIDTHxHEIGHT",
        default="1280x720",
        help="window resolution (default: 1280x720)",
    )
    argparser.add_argument(
        "--filter",
        metavar="PATTERN",
        default="vehicle.audi.*",
        help='actor filter (default: "vehicle.audi.*")',
    )
    argparser.add_argument(
        "--scenario",
        metavar="scenario_1.json",
        default="scenario_1.json",
        help='scenario file',
    )


    # Parse arguments
    args = argparser.parse_args()
    args.description = "BounCMPE CarlaSim 2D Visualizer"
    args.width, args.height = [int(x) for x in args.res.split("x")]

    args = vars(args)
    # Run game loop
    game_loop(args)
