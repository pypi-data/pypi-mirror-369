import os

import pandas as pd

import hsr1


class TestDatabase:
    def test_can_create_database(self):
        data_filepath = "tests/res/NOAA 2025"
        deployment_metadata_filepath = "tests/res/NOAA 2025/HSR1-009 NOAA 2025 Deployment.ini"

        database_location = "tests/temp/databases/my_database.db"

        db_driver = hsr1.DBDriver(database_location)

        data = hsr1.read_txt.read(data_filepath, deployment_metadata_filepath=
                                  deployment_metadata_filepath)
        db_driver.store(data)

        assert(os.path.exists(database_location))
        assert(os.path.getsize(database_location) > 100)

        os.remove(database_location)
        assert(not os.path.exists(database_location))

    
    def test_can_read_from_database(self):
        data_filepath = "tests/res/NOAA 2025"
        deployment_metadata_filepath = "tests/res/NOAA 2025/HSR1-009 NOAA 2025 Deployment.ini"

        database_location = "tests/temp/databases/databases/my_database.db"

        db_driver = hsr1.DBDriver(database_location)

        txt_data = hsr1.read_txt.read(data_filepath, deployment_metadata_filepath=
                                  deployment_metadata_filepath)
        print(txt_data)

        db_driver.store(txt_data)

        db_data = db_driver.load()

        assert(type(db_data) == pd.DataFrame)
        assert("pc_time_end_measurement" in db_data.columns)
        
        assert("global_integral" in db_data.columns)
        assert("diffuse_integral" in db_data.columns)
        assert("global_spectrum" in db_data.columns)

        assert(txt_data[0]["global_spectrum"].equals(db_data["global_spectrum"]))
        

    def test_can_plot_all_graphs(self):
        
        data_filepath = "tests/res/NOAA 2025"
        deployment_metadata_filepath = "tests/res/NOAA 2025/HSR1-009 NOAA 2025 Deployment.ini"

        database_location = "tests/temp/databases/databases/my_database.db"

        db_driver = hsr1.DBDriver(database_location)

        txt_data = hsr1.read_txt.read(data_filepath, deployment_metadata_filepath=
                                  deployment_metadata_filepath)

        db_driver.store(txt_data)

        g = hsr1.Graph(db_driver, timezone="-04:00", output_location="tests/temp/plots", block=False)
        g.plot_accessory()
        g.plot_aod_day()
        g.plot_dips_summary()
        
        g.plot_gps()
        g.plot_integral()
        g.plot_spectrum_day()
        g.plot_aod_day()

        assert(True)
