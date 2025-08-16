import os

import hsr1
import numpy as np
import pandas as pd

class TestAodGraphs:
    def test_aod_calculations(self):
        
        data_filepath = "tests/res/NOAA 2025"
        deployment_metadata_filepath = "tests/res/NOAA 2025/HSR1-009 NOAA 2025 Deployment.ini"

        database_location = "tests/temp/databases/databases/my_database.db"

        db_driver = hsr1.DBDriver(database_location)

        txt_data = hsr1.read_txt.read(data_filepath, deployment_metadata_filepath=
                                  deployment_metadata_filepath)

        db_driver.store(txt_data)
        
        data = db_driver.load(columns=["pc_time_end_measurement", "global_spectrum", "diffuse_spectrum", "sza", "sed"])
        result = hsr1.utils.HSRFunc.calc_aod_from_df(data)
        print(result)
        print(result.columns)
        
        assert(list(result.columns) == list(["pc_time_end_measurement", "total_od", "aod_microtops", "aod_wood_2017"]))
        assert(len(result.index) == len(data.index))

        os.remove(database_location)


    def test_aod_line_graph_should_run(self):
        
        data_filepath = "tests/res/NOAA 2025"
        deployment_metadata_filepath = "tests/res/NOAA 2025/HSR1-009 NOAA 2025 Deployment.ini"

        database_location = "tests/temp/databases/databases/my_database.db"

        db_driver = hsr1.DBDriver(database_location)

        txt_data = hsr1.read_txt.read(data_filepath, deployment_metadata_filepath=
                                  deployment_metadata_filepath)

        db_driver.store(txt_data)

        g = hsr1.Graph(db_driver, timezone="-04:00", output_location="tests/temp/plots", block=True)

        g.plot_aod_day()

        os.remove(database_location)
