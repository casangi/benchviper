import shutil
import xarray as xr

from xradio.measurement_set import load_processing_set
from xradio.schema.check import check_datatree
from xradio.measurement_set.processing_set_xdt import ProcessingSetXdt


class TestLoadProcessingSet:
    """
    Tests for load_processing_set using real data
    Adapted from:
    https://github.com/casangi/xradio/blob/main/tests/unit/measurement_set/test_load_processing_set.py
    at commit:
    b1618b0fa08a3e657dff8905eb93d298717b7ae5
    """

    MeasurementSet = "Antennae_North.cal.lsrk.split.ms"
    processing_set = "test_processing_set.ps.zarr"

    def setup_cache(self):
        # perform the expensive operations once (per env, per commit), see
        # https://asv.readthedocs.io/en/stable/writing_benchmarks.html#setup-and-teardown-functions

        # adapted from https://github.com/casangi/xradio/blob/main/tests/_utils/conftest.py

        # download MS from cloudflare using helper module
        from toolviper.utils.data import download

        download(file=self.MeasurementSet)

        # Convert MS to processing set
        from xradio.measurement_set import convert_msv2_to_processing_set

        ps_path = self.processing_set

        convert_msv2_to_processing_set(
            in_file=self.MeasurementSet,
            out_file=self.processing_set,
            partition_scheme=[],
            main_chunksize=0.01,
            pointing_chunksize=0.00001,
            pointing_interpolate=True,
            ephemeris_interpolate=True,
            use_table_iter=False,
            overwrite=True,
            parallel_mode="none",
        )

    def time_check_datatree(self):
        """Test that the converted MS to PS complies with the datatree schema checker"""
        ps_xdt = load_processing_set(self.processing_set)
        issues = check_datatree(ps_xdt)
        # The check_datatree function returns a SchemaIssues object, not a string

    def time_basic_load(self):
        """Test basic loading of processing set without parameters"""
        ps_xdt = load_processing_set(self.processing_set)

    def time_selective_loading(self):
        """Test loading with selection parameters"""
        # First load normally to get MS names
        full_ps = load_processing_set(self.processing_set)

        # Check MS names are the expected ones
        ms_basename = "Antennae_North.cal.lsrk.split"
        expected_names = [f"{ms_basename}_{i}" for i in range(4)]  # 0 to 3
        ms_names = list(full_ps.children.keys())

        assert len(ms_names) == len(
            expected_names
        ), "Number of measurement sets doesn't match"
        for ms_name, expected_name in zip(sorted(ms_names), sorted(expected_names)):
            assert (
                ms_name == expected_name
            ), f"Expected {expected_name} but got {ms_name}"

        # Test loading with selection parameters
        sel_parms = {ms_name: {"time": slice(0, 10)}}
        ps_xdt = load_processing_set(self.processing_set, sel_parms=sel_parms)

    def time_data_group_selection(self):
        """Test loading with specific data group"""
        ps_xdt = load_processing_set(self.processing_set, data_group_name="base")

    def time_variable_selection(self):
        """Test loading with specific variables included/excluded"""
        # Test including specific variables
        include_vars = ["VISIBILITY"]
        ps_xdt = load_processing_set(
            self.processing_set,
            include_variables=include_vars,
        )

        # Test dropping specific variables
        drop_vars = ["WEIGHT"]
        ps_xdt = load_processing_set(self.processing_set, drop_variables=drop_vars)

    def time_sub_datasets(self):
        """Test loading with and without sub-datasets"""
        # Test with sub-datasets
        _ps_with_subs = load_processing_set(self.processing_set, load_sub_datasets=True)

        # Test without sub-datasets
        ps_without_subs = load_processing_set(
            self.processing_set, load_sub_datasets=False
        )


class TestProcessingSetXdtWithData:
    """
    Benchmarks for ProcessingSetXdt using real data
    Adapted from:
    https://github.com/casangi/xradio/blob/main/tests/unit/measurement_set/test_processing_set_xdt.py
    TestProcessingSetXdtWithData class
    at commit:
    b1618b0fa08a3e657dff8905eb93d298717b7ae5
    """

    MeasurementSet = "Antennae_North.cal.lsrk.split.ms"
    processing_set = "test_processing_set_xdt.ps.zarr"

    def setup_cache(self):
        # perform the expensive operations once (per env, per commit), see
        # https://asv.readthedocs.io/en/stable/writing_benchmarks.html#setup-and-teardown-functions

        # adapted from https://github.com/casangi/xradio/blob/main/tests/_utils/conftest.py

        # download MS from cloudflare using helper module
        from toolviper.utils.data import download

        download(file=self.MeasurementSet)

        # Convert MS to processing set
        from xradio.measurement_set import convert_msv2_to_processing_set

        ps_path = self.processing_set

        convert_msv2_to_processing_set(
            in_file=self.MeasurementSet,
            out_file=self.processing_set,
            partition_scheme=[],
            main_chunksize=0.01,
            pointing_chunksize=0.00001,
            pointing_interpolate=True,
            ephemeris_interpolate=True,
            use_table_iter=False,
            overwrite=True,
            parallel_mode="none",
        )

    def time_summary(self):
        """Benchmark the summary method on a real processing set"""
        ps_xdt = load_processing_set(self.processing_set)
        ps_xdt.xr_ps.summary()

    def time_summary_ordered(self):
        """Benchmark the summary method with first_columns parameter"""
        ps_xdt = load_processing_set(self.processing_set)
        ps_xdt.xr_ps.summary(first_columns=["spw_name", "scan_name"])

    def time_get_max_dims(self):
        """Benchmark getting maximum dimensions from a processing set"""
        ps_xdt = load_processing_set(self.processing_set)
        ps_xdt.xr_ps.get_max_dims()

    def time_get_freq_axis(self):
        """Benchmark getting frequency axis from a processing set"""
        ps_xdt = load_processing_set(self.processing_set)
        ps_xdt.xr_ps.get_freq_axis()

    def time_query_by_name(self):
        """Benchmark querying a processing set by name"""
        ps_xdt = load_processing_set(self.processing_set)
        ms_names = list(ps_xdt.children.keys())
        ps_xdt.xr_ps.query(name=ms_names[0])

    def time_query_by_data_group(self):
        """Benchmark querying a processing set by data group"""
        ps_xdt = load_processing_set(self.processing_set)
        ps_xdt.xr_ps.query(data_group_name="base")

    def time_get_combined_field_and_source_xds(self):
        """Benchmark getting combined field and source dataset from a processing set"""
        ps_xdt = load_processing_set(self.processing_set)
        ps_xdt.xr_ps.get_combined_field_and_source_xds()

    def time_get_combined_antenna_xds(self):
        """Benchmark getting combined antenna dataset from a processing set"""
        ps_xdt = load_processing_set(self.processing_set)
        ps_xdt.xr_ps.get_combined_antenna_xds()


class TestProcessingSetXdtWithEphemerisData:
    """
    Benchmarks for ProcessingSetXdt using real ephemeris data
    Adapted from:
    https://github.com/casangi/xradio/blob/main/tests/unit/measurement_set/test_processing_set_xdt.py
    TestProcessingSetXdtWithEphemerisData class
    at commit:
    b1618b0fa08a3e657dff8905eb93d298717b7ae5
    """

    MeasurementSet = "ALMA_uid___A002_X1003af4_X75a3.split.avg.ms"
    processing_set = "test_processing_set_xdt_ephemeris.ps.zarr"

    def setup_cache(self):
        # perform the expensive operations once (per env, per commit), see
        # https://asv.readthedocs.io/en/stable/writing_benchmarks.html#setup-and-teardown-functions

        # adapted from https://github.com/casangi/xradio/blob/main/tests/_utils/conftest.py

        # download MS from cloudflare using helper module
        from toolviper.utils.data import download

        download(file=self.MeasurementSet)

        # Convert MS to processing set
        from xradio.measurement_set import convert_msv2_to_processing_set

        ps_path = self.processing_set

        convert_msv2_to_processing_set(
            in_file=self.MeasurementSet,
            out_file=self.processing_set,
            partition_scheme=[],
            main_chunksize=0.01,
            pointing_chunksize=0.00001,
            pointing_interpolate=True,
            ephemeris_interpolate=True,
            use_table_iter=False,
            overwrite=True,
            parallel_mode="none",
        )

    def time_check_datatree(self):
        """Benchmark that the converted MS to PS complies with the datatree schema checker"""
        ps_xdt = load_processing_set(self.processing_set)
        check_datatree(ps_xdt)

    def time_get_combined_field_and_source_xds_ephemeris(self):
        """Benchmark getting combined field and source dataset with ephemeris from a processing set"""
        ps_xdt = load_processing_set(self.processing_set)
        ps_xdt.xr_ps.get_combined_field_and_source_xds_ephemeris()

    def time_field_offset_calculation(self):
        """Benchmark that field offsets are correctly calculated"""
        ps_xdt = load_processing_set(self.processing_set)
        field_source_xds = ps_xdt.xr_ps.get_combined_field_and_source_xds_ephemeris()
        field_offset = field_source_xds["FIELD_OFFSET"]

    def time_time_interpolation(self):
        """Benchmark that time interpolation works correctly for ephemeris data"""
        ps_xdt = load_processing_set(self.processing_set)
        field_source_xds = ps_xdt.xr_ps.get_combined_field_and_source_xds_ephemeris()
