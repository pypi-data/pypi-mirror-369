import os

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import hsr1


class TestDniCalculation:

    def test_calculates_dni_correctly(self):
        global_data = [200, 180, 160]
        diffuse_data = [20, 10, 160]
        sza = list(np.radians(np.array([10, 80, 20])))

        df = pd.DataFrame(columns=["global_integral", "diffuse_integral", "sza"], data = np.array([global_data, diffuse_data, sza]).T)

        print(df)

        df = hsr1.utils.HSRFunc.add_direct_normal_column_to_df(df)

        assert(abs(df["direct_normal_integral"].iloc[0] - 182.77) < 0.01)
        assert(abs(df["direct_normal_integral"].iloc[1] - 978.99) < 0.01)
        assert(abs(df["direct_normal_integral"].iloc[2] == 0))

    def test_cuttoff_works(self):
        global_data = [200, 180, 160]
        diffuse_data = [20, 10, 160]
        sza = list(np.radians(np.array([10, 80, 20])))

        df = pd.DataFrame(columns=["global_integral", "diffuse_integral", "sza"], data = np.array([global_data, diffuse_data, sza]).T)

        print(df)

        df = hsr1.utils.HSRFunc.add_direct_normal_column_to_df(df, cutoff=75)

        assert(abs(df["direct_normal_integral"].iloc[0] - 182.77) < 0.01)
        assert(abs(df["direct_normal_integral"].iloc[1] == 0))
        assert(abs(df["direct_normal_integral"].iloc[2] == 0))

    def test_dni_graphs_should_run(self):

        data_filepath = "tests/res/NOAA 2025"
        deployment_metadata_filepath = "tests/res/NOAA 2025/HSR1-009 NOAA 2025 Deployment.ini"

        database_location = "tests/temp/databases/databases/my_database.db"

        db_driver = hsr1.DBDriver(database_location)

        txt_data = hsr1.read_txt.read(data_filepath, deployment_metadata_filepath=
                                  deployment_metadata_filepath)

        db_driver.store(txt_data)

        g = hsr1.Graph(db_driver, timezone="-04:00", output_location="tests/temp/plots", block=False)
        
        g.plot_daily_line(columns=["global_integral", "diffuse_integral", "direct_normal_integral"])
        g.plot_integral()
        plt.show()

        os.remove(database_location)
