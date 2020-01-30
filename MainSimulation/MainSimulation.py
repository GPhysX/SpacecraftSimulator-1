
from Spacecraft.Spacecraft import Spacecraft
from Dynamics.SimTime import SimTime
from initial_config import initial_config
from Dynamics.SpacecraftOrbit.MainOrbit import MainOrbit
from Dynamics.CelestialBody.Ephemeris import Ephemeris
from Dynamics.SpacecraftAttitude.MainAttitude import MainAttitude

import numpy as np
import pandas as pd
import datetime

twopi       = 2.0 * np.pi
deg2rad     = np.pi / 180.0
rad2deg     = 1 / deg2rad


class MainSimulation(MainOrbit, MainAttitude, SimTime):
    def __init__(self, initial_properties = initial_config()):

        self.main_spacecraft  = Spacecraft(initial_properties[1], None)

        SimTime.__init__(self, initial_properties[0])
        MainAttitude.__init__(self, initial_properties[1])
        MainOrbit.__init__(self, initial_properties[2], self.main_spacecraft.orbit_dynamics)

        self.earth = Ephemeris()
        date = datetime.datetime.now()
        self.filename = date.strftime('%Y-%m-%d %H-%M-%S')
        self.pos    = [0, 0, 0]
        self.vel    = [0, 0, 0]
        self.quat   = [0, 0, 0]
        self.omega  = [1, 0, 0, 0]
        self.long   = 0
        self.lat    = 0
        self.alt    = 0

    def run_simulation(self):
        self.set_propagator()
        # Loop
        self.reset_countTime()
        while self.maincountTime <= self.endsimTime:
            self.progressionsimTime()
            array_time, str_time = self.get_array_time()

            if self.orbit_update_flag:
                self.pos, self.vel = self.update_orbit(array_time)
                self.lat, self.long, self.alt = self.orbit_propagate.TransECItoGeo()
                self.orbit_update_flag = False

            if self.attitude_update_flag:
                self.quat, self.omega = self.update_attitude()
                self.attitude_update_flag = False

            if self.log_flag:
                self.main_spacecraft.update_spacecraft_dynamics(self.pos,
                                                                self.vel,
                                                                self.quat,
                                                                self.omega,
                                                                self.lat,
                                                                self.long,
                                                                self.alt)
                self.main_spacecraft.update_spacecraft_state(str_time, self.maincountTime)
                self.earth.gst_Update(self.orbit_propagate.current_side)
                self.log_flag = False

            # update time
            self.updateSimtime()

        # Data report to create dictionary
        self.main_spacecraft.create_data()

        # Save Dataframe pandas in csv file
        self.save_data()
        print('Finished')

    def save_data(self):
        master_data = {**self.main_spacecraft.master_data_satellite, **self.earth.gst}
        database = pd.DataFrame(master_data, columns=master_data.keys())
        print(database)

        database.to_csv("./Data/logs/"+self.filename+".csv", index=False, header=True)
        print("Data created")

