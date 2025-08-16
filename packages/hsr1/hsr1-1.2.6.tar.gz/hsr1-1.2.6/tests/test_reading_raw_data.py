import os

import hsr1


class TestRawDatabase:
    def test_can_read_raw_data_and_store(self):
        data_filepath = "tests/res/NOAA 2025"
        deployment_metadata_filepath = "tests/res/NOAA 2025/HSR1-009 NOAA 2025 Deployment.ini"

        database_location = "tests/temp/databases/my_database.db"

        db_driver = hsr1.DBDriver(database_location)

        data, deployment_metadata = hsr1.read_txt.read_raw_txt(data_filepath, deployment_metadata_filepath=
                                  deployment_metadata_filepath)
        db_driver.store_raw(data, deployment_metadata)

        assert(os.path.exists(database_location))
        assert(os.path.getsize(database_location) > 100)

        os.remove(database_location)
        assert(not os.path.exists(database_location))
