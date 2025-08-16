import os

import pandas as pd

import hsr1


class TestUnalignedDataOnDailyPlots:
    def test_should_plot_correctly_with_regular_data(self):
        
        data_filepath = "tests/res/NOAA 2025"
        deployment_metadata_filepath = "tests/res/NOAA 2025/HSR1-009 NOAA 2025 Deployment.ini"

        database_location = "tests/temp/databases/databases/my_database.db"

        db_driver = hsr1.DBDriver(database_location)

        txt_data = hsr1.read_txt.read(data_filepath, deployment_metadata_filepath=
                                  deployment_metadata_filepath)

        db_driver.store(txt_data)

        g = hsr1.Graph(db_driver, timezone="00:00", output_location="tests/temp/plots", block=True)

        g.daily_integrals()

        os.remove(database_location)
    

    def test_should_plot_non_minute_aligned_data_with_gaps(self):
        db_loc = "dev/res/databases/"

        db_name = db_loc+"unaligned.db"

        location = {"lat":53.1, "lon":1.6, "alt":0}

        if os.path.exists(db_name):
            print("overwriting database")
            os.remove(db_name)

        dataset = hsr1.synthetic_dataset.SyntheticDataset(start_date="2024-01-10 00:00:00+00:00",
                                                         end_date="2024-01-10 23:59:00+00:00",
                                                         latitude=location["lat"],
                                                         longitude=location["lon"],
                                                         altitude=location["alt"])
        dataset.generate_spectral_data("1min")
        dataset.generate_accessory_data("10s")
        dataset.generate_system_data_accessory()
        dataset.generate_deployment_metadata("dev/res/HSR1-009 NOAA 2025 Deployment.ini")

        dataset.generate_custom_column("spectral_data", 
                                       ["global_integral", "diffuse_integral"], 
                                       dataset.pvlib_integral_static)

        dfs = dataset.get_dfs()

        spectral_df = dfs[0]
        spectral_df["pc_time_end_measurement"] = (pd.DatetimeIndex(spectral_df["pc_time_end_measurement"])+pd.Timedelta(1, "s")).astype(str)
        x = pd.DatetimeIndex(spectral_df["pc_time_end_measurement"]).hour != 12

        spectral_df = spectral_df.loc[x, :]
        dfs[0] = spectral_df

        db = hsr1.DBDriver(db_name)
        db.store(dfs)

        g = hsr1.Graph(db)
        g.daily_integrals()
        g.daily_temps()

        os.remove(db_name)
