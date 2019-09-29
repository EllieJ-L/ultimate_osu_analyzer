import numpy as np

from misc.geometry import *
from misc.math_utils import *
from misc.metrics import Metrics

from osu.local.beatmap.beatmap import Beatmap

from analysis.osu.std.map_data import StdMapData



class StdMapMetrics():

    '''
    Raw metrics
    '''
    @staticmethod
    def calc_tapping_intervals(hitobject_data=[]):
        t = StdMapData.start_times(hitobject_data)
        if len(t) < 2: return [], []

        dt = np.diff(t)
        return t[1:], dt


    @staticmethod
    def calc_notes_per_sec(hitobject_data=[]):
        t = StdMapData.start_times(hitobject_data)
        if len(t) < 2: return [], []

        dt = 1000/np.diff(t)
        return t[1:], dt


    @staticmethod
    def calc_distances(hitobject_data=[]):
        t = StdMapData.all_times(hitobject_data)
        p = StdMapData.all_positions(hitobject_data)
        if len(p) < 2: return [], []
        
        x, y = p[:,0], p[:,1]
        return t[1:], Metrics.dists(x, y, t)

    
    @staticmethod
    def calc_velocity(hitobject_data=[]):
        t = StdMapData.all_times(hitobject_data)
        p = StdMapData.all_positions(hitobject_data)
        if len(p) < 2: return [], []
        
        x, y = p[:,0], p[:,1]
        return t[1:], Metrics.vel_2d(x, y, t)


    @staticmethod
    def calc_velocity_start(hitobject_data=[]):
        t = StdMapData.start_times(hitobject_data)
        p = StdMapData.start_positions(hitobject_data)
        if len(p) < 2: return [], []
        
        x, y = p[:,0], p[:,1]
        return t[1:], Metrics.vel_2d(x, y, t)


    @staticmethod
    def calc_intensity(hitobject_data=[]):
        t, v   = StdMapMetrics.calc_velocity_start(hitobject_data)
        t, nps = StdMapMetrics.calc_notes_per_sec(hitobject_data)

        intensity = v*nps
        return t, intensity


    @staticmethod
    def calc_angles(hitobject_data=[]):
        t = StdMapData.all_times(hitobject_data)
        p = StdMapData.all_positions(hitobject_data)
        if len(p) < 2: return [], []

        x, y = p[:,0], p[:,1]
        return t[1:], Metrics.angle(x, y, t)

    
    @staticmethod
    def calc_xy_vel(hitobject_data=[]):
        t = StdMapData.all_times(hitobject_data)
        p = StdMapData.all_positions(hitobject_data)
        if len(p) < 2: return [], []
        
        dt = np.diff(t)
        dx = np.diff(p[:,0])
        dy = np.diff(p[:,1])

        return t[1:], dx/dt, dy/dt


    # Perpendicular intensity
    @staticmethod
    def calc_perp_int(hitobject_data=[]):
        times, rv = StdMapMetrics.calc_radial_velocity(hitobject_data)
        times, x_vel, y_vel = StdMapMetrics.calc_xy_vel(hitobject_data)

        # Construct vector angles from parametric velocities
        theta1 = np.arctan2(y_vel[1:], x_vel[1:])
        theta2 = np.arctan2(y_vel[:-1], x_vel[:-1])

        # Make stacks 0 angle change
        mask = np.where(np.logical_and(y_vel[1:] == 0, x_vel[1:] == 0))[0]
        theta1[mask] = theta1[mask - 1]

        mask = np.where(np.logical_and(y_vel[:-1] == 0, x_vel[:-1] == 0))[0]
        theta2[mask] = theta2[mask - 1]

        # Velocity in the perpendicular direction relative to current
        dy_vel = np.sin(theta2 - theta1)

        return times, rv*dy_vel[1:]


    # Linear intensity
    @staticmethod
    def calc_lin_int(hitobject_data=[]):
        times, rv = StdMapMetrics.calc_radial_velocity(hitobject_data)
        times, x_vel, y_vel = StdMapMetrics.calc_xy_vel(hitobject_data)

        # Construct vector angles from parametric velocities
        theta1 = np.arctan2(y_vel[1:], x_vel[1:])
        theta2 = np.arctan2(y_vel[:-1], x_vel[:-1])

        # Make stacks 0 angle change
        mask = np.where(np.logical_and(y_vel[1:] == 0, x_vel[1:] == 0))[0]
        theta1[mask] = theta1[mask - 1]

        mask = np.where(np.logical_and(y_vel[:-1] == 0, x_vel[:-1] == 0))[0]
        theta2[mask] = theta2[mask - 1]

        # Velocity in the parellel direction relative to current
        dx_vel = np.cos(theta2 - theta1)

        return times, rv*dx_vel[1:]
        all_times     = StdMapData.all_times(hitobject_data)
        all_positions = StdMapData.all_positions(hitobject_data)
        if len(all_positions) < 3: return [], []
        
        positions = [ Pos(*pos) for pos in all_positions ]
        angles    = [ get_angle(*param) for param in zip(positions[:-2], positions[1:-1], positions[2:]) ]

        return all_times[1:-1], angles


    @staticmethod
    def calc_acceleration(hitobject_data=[]):
        pass
        pass
        

    '''
    Response metrics
    '''
    @staticmethod
    def calc_speed_response(resolution=1, x_range=(1, 100)):
        return ([x for x in range(*x_range)], [ 1/x for x in range(*x_range) ])


    '''
    Advanced metrics
    '''
    @staticmethod
    def calc_rhythmic_complexity(hitobject_data=[]):
        def calc_harmonic(prev_note_interval, curr_note_interval, target_time, v_scale):
            if prev_note_interval == 0: print('WARNING: 0 note interval detected at ', target_time, ' ms')

            return -(v_scale/2)*math.cos((2*math.pi)/prev_note_interval*curr_note_interval) + (v_scale/2)

        def decay(interval, decay_factor):
            return math.exp(-decay_factor*interval)

        def speed(interval, speed_factor):
            return speed_factor/interval

        def calc_note(time, curr_interval, prev_interval, decay_factor, v_scale):
            return decay(curr_interval, decay_factor) * calc_harmonic(prev_interval, curr_interval, time, v_scale)

        speed_factor = 600.0
        v_factor     = 10.0
        decay_factor = 0.005

        time, intervals = StdMapMetrics.calc_tapping_intervals(hitobject_data)
        harmonics = [ calc_note(time[i], intervals[i], intervals[i - 1], decay_factor, v_factor) for i in range(1, len(intervals)) ]

        return time, [ sum(harmonics[:i])*speed(intervals[i], speed_factor) for i in range(0, len(intervals)) ]


    @staticmethod
    def calc_path_curvature(hitobjects):
        pass
    

    @staticmethod
    def calc_visual_density(hitobjects):
        pass


    '''
    Skill metrics
    '''
    @staticmethod
    def calc_speed_skill(hitobjects):
        pass

    @staticmethod
    def calc_tapping_skill(hitobjects):
        pass


    @staticmethod
    def calc_targeting_skill(hitobjects):
        pass


    @staticmethod
    def calc_agility_skill(hitobjects):
        pass