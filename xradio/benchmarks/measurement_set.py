import shutil
import xarray as xr

from xradio.measurement_set import load_processing_set
from xradio.schema.check import check_datatree


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

    def time_test_check_datatree(self):
        """Test that the converted MS to PS complies with the datatree schema checker"""
        ps_xdt = load_processing_set(self.processing_set)
        issues = check_datatree(ps_xdt)
        # The check_datatree function returns a SchemaIssues object, not a string

    def time_test_basic_load(self):
        """Test basic loading of processing set without parameters"""
        ps_xdt = load_processing_set(self.processing_set)

    def time_test_selective_loading(self):
        """Test loading with selection parameters"""
        # First load normally to get MS names
        full_ps = load_processing_set(self.processing_set)

        # Check MS names are the expected ones
        ms_basename = "Antennae_North.cal.lsrk.split"
        expected_names = [f"{ms_basename}_{i}" for i in range(4)]  # 0 to 3
        ms_names = list(full_ps.children.keys())

        # Test loading with selection parameters
        sel_parms = {ms_name: {"time": slice(0, 10)}}
        ps_xdt = load_processing_set(self.processing_set, sel_parms=sel_parms)

    def time_test_data_group_selection(self):
        """Test loading with specific data group"""
        ps_xdt = load_processing_set(self.processing_set, data_group_name="base")

    def time_test_variable_selection(self):
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

    def test_sub_datasets(self):
        """Test loading with and without sub-datasets"""
        # Test with sub-datasets
        _ps_with_subs = load_processing_set(self.processing_set, load_sub_datasets=True)

        # Test without sub-datasets
        ps_without_subs = load_processing_set(
            self.processing_set, load_sub_datasets=False
        )
