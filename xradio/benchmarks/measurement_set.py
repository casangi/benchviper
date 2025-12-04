import shutil
import xarray as xr

from xradio.measurement_set import load_processing_set
from xradio.schema.check import check_datatree
from xradio.measurement_set.processing_set_xdt import ProcessingSetXdt
from xradio.testing.measurement_set.msv2_io import (
    gen_minimal_ms,
    build_processing_set_from_msv2,
    build_minimal_msv4_xdt
)
from xradio.testing.measurement_set.io import download_measurement_set



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

        # adapted from https://github.com/casangi/xradio/blob/main/tests/unit/measurement_set/conftest.py

        ms_path = download_measurement_set(self.MeasurementSet)

        # Convert MS to processing set
        ps_path = self.processing_set

        build_processing_set_from_msv2(
            in_file=ms_path,
            out_file=self.processing_set,
            partition_scheme=[],
            overwrite=True,
            parallel_mode="none",
            main_chunksize=0.01,
            pointing_chunksize=0.00001,
            pointing_interpolate=True,
            ephemeris_interpolate=True,
            use_table_iter=False,
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

    def time_include_variable(self):
        """Test loading with specific variables included"""
        # Test including specific variable
        include_vars = ["VISIBILITY"]
        ps_xdt = load_processing_set(
            self.processing_set,
            include_variables=include_vars,
        )

    def time_drop_variable(self):
        """Test loading with specific variables dropped"""
        # Test dropping specific variable
        drop_vars = ["WEIGHT"]
        ps_xdt = load_processing_set(self.processing_set, drop_variables=drop_vars)

    def time_sub_datasets_true(self):
        """Test loading with sub-datasets"""
        # Test with sub-datasets
        _ps_with_subs = load_processing_set(self.processing_set, load_sub_datasets=True)

    def time_sub_datasets_false(self):
        """Test loading without sub-datasets"""
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

        ms_path = download_measurement_set(self.MeasurementSet)

        # Convert MS to processing set
        ps_path = self.processing_set

        build_processing_set_from_msv2(
            in_file=ms_path,
            out_file=self.processing_set,
            partition_scheme=[],
            overwrite=True,
            parallel_mode="none",
            main_chunksize=0.01,
            pointing_chunksize=0.00001,
            pointing_interpolate=True,
            ephemeris_interpolate=True,
            use_table_iter=False,
        )

        # Load the PS in cache to use in every test case
        return load_processing_set(self.processing_set)

    def time_summary(self, ps_xdt):
        """Benchmark the summary method on a real processing set"""
        # ps_xdt = load_processing_set(self.processing_set)
        ps_xdt.xr_ps.summary()

    def time_summary_ordered(self, ps_xdt):
        """Benchmark the summary method with first_columns parameter"""
        # ps_xdt = load_processing_set(self.processing_set)
        ps_xdt.xr_ps.summary(first_columns=["spw_name", "scan_name"])

    def time_get_max_dims(self, ps_xdt):
        """Benchmark getting maximum dimensions from a processing set"""
        # ps_xdt = load_processing_set(self.processing_set)
        ps_xdt.xr_ps.get_max_dims()

    def time_get_freq_axis(self, ps_xdt):
        """Benchmark getting frequency axis from a processing set"""
        # ps_xdt = load_processing_set(self.processing_set)
        ps_xdt.xr_ps.get_freq_axis()

    def time_query_by_name(self, ps_xdt):
        """Benchmark querying a processing set by name"""
        # ps_xdt = load_processing_set(self.processing_set)
        ms_names = list(ps_xdt.children.keys())
        ps_xdt.xr_ps.query(name=ms_names[0])

    def time_query_by_data_group(self, ps_xdt):
        """Benchmark querying a processing set by data group"""
        # ps_xdt = load_processing_set(self.processing_set)
        ps_xdt.xr_ps.query(data_group_name="base")

    def time_get_combined_field_and_source_xds(self, ps_xdt):
        """Benchmark getting combined field and source dataset from a processing set"""
        # ps_xdt = load_processing_set(self.processing_set)
        ps_xdt.xr_ps.get_combined_field_and_source_xds()

    def time_get_combined_antenna_xds(self, ps_xdt):
        """Benchmark getting combined antenna dataset from a processing set"""
        # ps_xdt = load_processing_set(self.processing_set)
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

        ms_path = download_measurement_set(self.MeasurementSet)

        # Convert MS to processing set
        ps_path = self.processing_set

        build_processing_set_from_msv2(
            in_file=ms_path,
            out_file=self.processing_set,
            partition_scheme=[],
            overwrite=True,
            parallel_mode="none",
            main_chunksize=0.01,
            pointing_chunksize=0.00001,
            pointing_interpolate=True,
            ephemeris_interpolate=True,
            use_table_iter=False,
        )

        # Load the PS in cache to use in every test case
        return load_processing_set(self.processing_set)

    def time_check_datatree(self, ps_xdt):
        """Benchmark that the converted MS to PS complies with the datatree schema checker"""
        # ps_xdt = load_processing_set(self.processing_set)
        check_datatree(ps_xdt)

    def time_get_combined_field_and_source_xds_ephemeris(self, ps_xdt):
        """Benchmark getting combined field and source dataset with ephemeris from a processing set"""
        # ps_xdt = load_processing_set(self.processing_set)
        ps_xdt.xr_ps.get_combined_field_and_source_xds_ephemeris()

    def time_time_interpolation(self, ps_xdt):
        """Benchmark that time interpolation works correctly for ephemeris data"""
        # ps_xdt = load_processing_set(self.processing_set)
        field_source_xds = ps_xdt.xr_ps.get_combined_field_and_source_xds_ephemeris()


class TestMeasurementSetXdtWithData:
    """
    Benchmarks for MeasurementSetXdt using real data
    Adapted from:
    https://github.com/casangi/xradio/blob/main/tests/unit/measurement_set/test_measurement_set_xdt.py
    at commit:
    b1618b0fa08a3e657dff8905eb93d298717b7ae5

    """

    def setup_cache(self):
        ms_path, _ = gen_minimal_ms()
        msv4_path = build_minimal_msv4_xdt(
            ms_path,
            partition_kwargs={
                "DATA_DESC_ID": [0],
                "OBS_MODE": ["CAL_ATMOSPHERE#ON_SOURCE"],
            },
        )
        return xr.open_datatree(msv4_path, engine="zarr")

    def setup(self, msv4_xdt):
        # Store the cached MSv4 XDT
        self.msv4_xdt = msv4_xdt
        self.ms_xdt = self.msv4_xdt.xr_ms

    def time_add_data_group_with_defaults(self, _msv4_xdt):
        """Benchmark adding a data group with defaults"""
        self.ms_xdt.add_data_group("test_added_data_group_with_defaults")

    def time_add_data_group_with_values(self, _msv4_xdt):
        """Benchmark adding a data group with parameter values"""
        self.ms_xdt.add_data_group(
            "test_added_data_group_with_param_values",
            correlated_data="VISIBILITY",
            weight="EFFECTIVE_INTEGRATION_TIME",
            flag="FLAG",
            uvw="UVW",
            field_and_source_xds="field_and_source_base_xds",
            date_time="today, now",
            description="a test data group",
            data_group_dv_shared_with="base",
        )

    def time_get_field_and_source_xds(self, _msv4_xdt):
        """Benchmark getting field and source XDS"""
        self.ms_xdt.get_field_and_source_xds()

    def time_get_field_and_source_xds_with_group(self, _msv4_xdt):
        """Benchmark getting field and source XDS with data group"""
        self.ms_xdt.get_field_and_source_xds(data_group_name="base")

    def time_get_partition_info_default(self, _msv4_xdt):
        """Benchmark getting partition info with defaults"""
        self.ms_xdt.get_partition_info()

    def time_get_partition_info_with_group(self, _msv4_xdt):
        """Benchmark getting partition info with data group"""
        self.ms_xdt.get_partition_info(data_group_name="base")

    def time_sel_with_data_group(self, _msv4_xdt):
        """Benchmark selecting with data group"""
        self.ms_xdt.sel(data_group_name="base")

    def time_sel_polarization(self, _msv4_xdt):
        """Benchmark selecting with polarization"""
        self.ms_xdt.sel(polarization="XX")
