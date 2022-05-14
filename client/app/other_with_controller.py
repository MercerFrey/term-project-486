from turtle import distance
import carla
import math
from matplotlib.backend_bases import LocationEvent

from .controller import PurePursuitController


class Other(object):
    def __init__(self, location, rotation, waypoints, target_speed_km, actor_role):
        self.world = None
        self.actor = None
        self.control = None
        self.controller = None
        self.waypoints = waypoints
        self.target_speed = target_speed_km / 3.6  # km/h to m/s
        self.location = location
        self.rotation = rotation
        self.actor_role = actor_role
        self.tick_count = 0 
        self.autopilot = False


    def start(self, world):
        self.world = world
        spawn_point = carla.Transform(
            self.location, self.rotation
        )
        self.actor = self.world.spawn_hero("vehicle.audi.tt", spawn_point, role_name=self.actor_role)

        self.controller = PurePursuitController()

        self.world.register_actor_waypoints_to_draw(self.actor, self.waypoints)
        # self.actor.set_autopilot(True, world.args.tm_port)

    def tick(self, clock):
        ctrl = carla.VehicleControl()


        if self.ttc(self.actor.id + 1) < 3 or self.autopilot:
            self.autopilot = True
            self.tick_count += 1
            ctrl.throttle = 0.3
            ctrl.steer = -0.1 if self.tick_count < 5 else 0
        
        else:
            throttle, steer = self.controller.get_control(
                self.actor,
                self.waypoints,
                self.target_speed,
                self.world.fixed_delta_seconds,
            )

            ctrl.throttle = throttle
            ctrl.steer = steer


        self.actor.apply_control(ctrl)


    def destroy(self):
        """Destroy the hero actor when class instance is destroyed"""
        if self.actor is not None:
            self.actor.destroy()

    def ttc(self, actor_id):
        
        other_vehicle = self.world.world.get_actor(actor_id)
        if other_vehicle is None:
            return math.inf
        ### if the second car is moving 
        
        distance = self.actor.get_location().distance(other_vehicle.get_location())
        
        speed_difference = (self.calculate_speed(self.actor.get_velocity()) 
                            - self.calculate_speed(other_vehicle.get_velocity())
                            )
        try :
            return abs(distance / speed_difference)
        except ZeroDivisionError:
            return math.inf


    def calculate_speed(self, vehicle_speed):
        return math.sqrt(vehicle_speed.x**2 + vehicle_speed.y**2 + vehicle_speed.z**2)