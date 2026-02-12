import shutil
import xarray as xr

from xradio.measurement_set import (
    estimate_conversion_memory_and_cores,
    convert_msv2_to_processing_set,
    open_processing_set,
)
from xradio.schema.check import check_datatree
from xradio.testing.measurement_set.msv2_io import gen_minimal_ms, gen_test_ms


class TestEstimateConversionMemoryAndCores:
    """
    Benchmarks for estimate_conversion_memory_and_cores function
    Originally adapted from:
    https://github.com/casangi/xradio/blob/main/tests/unit/measurement_set/test_convert_msv2_to_processing_set.py
    test_estimate_conversion_memory_and_cores_minimal function
    at commit:
    b1618b0fa08a3e657dff8905eb93d298717b7ae5
    """

    version = "xradio 1.0.2"

    def setup_cache(self):
        # Generate minimal measurement set once per environment/commit
        ms_path, _ = gen_minimal_ms()
        return ms_path

    def time_estimate_no_partition(self, ms_path):
        """Benchmark memory estimation without partition scheme"""
        res = estimate_conversion_memory_and_cores(ms_path, partition_scheme=[])

    def time_estimate_field_partition(self, ms_path):
        """Benchmark memory estimation with FIELD_ID partition"""
        res = estimate_conversion_memory_and_cores(
            ms_path, partition_scheme=["FIELD_ID"]
        )

    def time_estimate_field_scan_partition(self, ms_path):
        """Benchmark memory estimation with FIELD_ID and SCAN_NUMBER partition"""
        res = estimate_conversion_memory_and_cores(
            ms_path, partition_scheme=["FIELD_ID", "SCAN_NUMBER"]
        )


class TestConvertMsv2ToProcessingSet:
    """
    Benchmarks for convert_msv2_to_processing_set function with various options
    Originally adapted from:
    https://github.com/casangi/xradio/blob/main/tests/unit/measurement_set/test_convert_msv2_to_processing_set.py
    test_convert_msv2_to_processing_set_with_other_opts function
    at commit:
    b1618b0fa08a3e657dff8905eb93d298717b7ae5
    """

    version = "xradio 1.0.2"

    out_path = "test_convert_msv2_to_proc_set_without_ps_zarr_ending"
    out_path_with_ending = out_path + ".ps.zarr"

    def setup_cache(self):
        # Generate minimal measurement set once per environment/commit
        # Use same parameters as ms_minimal_misbehaved fixture
        ms_path, _ = gen_test_ms(
            "test_msv2_minimal_required_misbehaved.ms",
            opt_tables=True,
            vlbi_tables=False,
            required_only=True,
            misbehave=True,
        )
        return ms_path

    def teardown(self, ms_path):
        """Clean up the output file after each benchmark"""
        try:
            shutil.rmtree(self.out_path_with_ending)
        except FileNotFoundError:
            pass

    def time_convert_with_field_partition(self, ms_path):
        """Benchmark MS conversion with FIELD_ID partition and write mode"""
        convert_msv2_to_processing_set(
            ms_path,
            out_file=self.out_path,
            partition_scheme=["FIELD_ID"],
            persistence_mode="w",
            parallel_mode="bogus_mode",
        )

    def time_open_processing_set(self, ms_path):
        """Benchmark opening processing set after conversion"""
        # First convert
        convert_msv2_to_processing_set(
            ms_path,
            out_file=self.out_path,
            partition_scheme=["FIELD_ID"],
            persistence_mode="w",
            parallel_mode="bogus_mode",
        )
        # Then open
        open_xdt = open_processing_set(self.out_path_with_ending, scan_intents="faulty")

    def time_check_converted_processing_set(self, ms_path):
        """Benchmark schema validation of converted processing set"""
        # Convert
        convert_msv2_to_processing_set(
            ms_path,
            out_file=self.out_path,
            partition_scheme=["FIELD_ID"],
            persistence_mode="w",
            parallel_mode="bogus_mode",
        )
        # Load and check
        ps_xdt = xr.open_datatree(self.out_path_with_ending, engine="zarr")
        check_datatree(ps_xdt)

    def time_full_workflow(self, ms_path):
        """Benchmark full workflow: convert, open, and validate"""
        # Convert
        convert_msv2_to_processing_set(
            ms_path,
            out_file=self.out_path,
            partition_scheme=["FIELD_ID"],
            persistence_mode="w",
            parallel_mode="bogus_mode",
        )
        # Open as xarray datatree
        ps_xdt = xr.open_datatree(self.out_path_with_ending, engine="zarr")
        # Validate schema
        check_datatree(ps_xdt)
        # Open with xradio function
        open_xdt = open_processing_set(self.out_path_with_ending, scan_intents="faulty")
