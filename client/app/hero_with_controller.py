from turtle import distance
import carla

from .controller import PurePursuitController


class Hero(object):
    def __init__(self, location, rotation, waypoints, target_speed_km):
        self.world = None
        self.actor = None
        self.control = None
        self.controller = None
        self.location = location
        self.rotation = rotation
        self.waypoints = waypoints
        self.target_speed = target_speed_km / 3.6  # km/h to m/s
        self.tick_count = 0

    def start(self, world):
        self.world = world
        spawn_point = carla.Transform(
            self.location, self.rotation
        )
        self.actor = self.world.spawn_hero("vehicle.audi.tt", spawn_point)

        self.controller = PurePursuitController()

        self.world.register_actor_waypoints_to_draw(self.actor, self.waypoints)
        #self.actor.set_autopilot(True, world.args.tm_port)

    def tick(self, clock):
        ctrl = carla.VehicleControl()
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

