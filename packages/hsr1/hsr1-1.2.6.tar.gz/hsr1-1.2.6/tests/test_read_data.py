import hsr1


class TestReadData:

    def test_should_read_txt_files_correctly(self):
        
        data_filepath = "tests/res/NOAA 2025"
        deployment_metadata_filepath = "tests/res/NOAA 2025/HSR1-009 NOAA 2025 Deployment.ini"

        data = hsr1.read_txt.read(data_filepath, deployment_metadata_filepath=
                                  deployment_metadata_filepath)

        assert(type(data) == tuple)
        assert("global_spectrum" in data[0].columns)
        assert("gps_longitude" in data[1].columns)
        assert("aux_average_period" in data[2].columns)

    def test_get_hsr_path_with_normal_data(self):

        data_filepath = "tests/res/NOAA 2025"

        dates = hsr1.utils.HSRFunc.Get_hsr_Dates(data_filepath, "2025-03-20", "2025-03-21")

        assert(dates[0] == "2025-03-20" and dates[-1] == "2025-03-21")

    def test_get_hsr_path_with_just_start_date(self):

        data_filepath = "tests/res/NOAA 2025"

        dates = hsr1.utils.HSRFunc.Get_hsr_Dates(data_filepath, "2025-03-20")

        assert(dates[0] == "2025-03-20")

    def test_get_hsr_path_with_just_end_date(self):

        data_filepath = "tests/res/NOAA 2025"

        dates = hsr1.utils.HSRFunc.Get_hsr_Dates(data_filepath, end_date="2025-03-20")

        assert(dates[-1] == "2025-03-20")


    def test_get_hsr_path_with_just_none_date(self):

        data_filepath = "tests/res/NOAA 2025"

        dates = hsr1.utils.HSRFunc.Get_hsr_Dates(data_filepath, "askjdnbaskj", None)

        assert(dates[0] == "2025-03-20" and dates[-1] == "2025-03-22")
