import numpy as np
import xarray as xr

from xradio.image import make_empty_sky_image
from xradio.testing.image import create_empty_test_image


def _make_valid_image_dataset():
    """Create a minimal Dataset that is valid for the ImageXds accessor.

    Built with :func:`~xradio.testing.image.create_empty_test_image`
    (``make_empty_sky_image`` factory, sky coordinates enabled) and promoted
    to an ``image_dataset`` node with a minimal ``data_groups`` mapping so
    that ImageXds methods accept it as an image node.
    """
    xds = create_empty_test_image(make_empty_sky_image, do_sky_coords=True)
    xds.attrs["type"] = "image_dataset"
    xds.attrs["data_groups"] = {
        "base": {
            "sky": "SKY",
            "flag": "FLAG_SKY",
            "description": "base image data group",
            "date": "2000-01-01T00:00:00.000",
        }
    }
    return xds


class TestImageXdsAccessor:
    """
    Benchmarks for ImageXds accessor with valid image datasets.
    Originally adapted from:
    https://github.com/casangi/xradio/blob/main/tests/unit/image/test_image_xds.py
    TestImageXdsValid class
    at commit:
    0f9957e5
    """

    version = "xradio 1.0.2"

    def setup_cache(self):
        # perform the expensive operations once (per env, per commit), see
        # https://asv.readthedocs.io/en/stable/writing_benchmarks.html#setup-and-teardown-functions

        # originally adapted from tests/unit/image/test_image_xds.py
        return _make_valid_image_dataset()

    def setup(self, xds):
        self.xds = xds
        self.xds_with_uv = xds.xr_img.add_uv_coordinates()

        # Multi-group dataset used by sel benchmarks parametrized on calling
        # convention. Built here so only the sel() call itself is timed.
        shape = (
            xds.sizes["time"],
            xds.sizes["frequency"],
            xds.sizes["polarization"],
            xds.sizes["l"],
            xds.sizes["m"],
        )
        xds_mg = xds.copy()
        xds_mg["SKY"] = xr.DataArray(
            np.zeros(shape, dtype=float),
            dims=("time", "frequency", "polarization", "l", "m"),
        )
        xds_mg["POINT_SPREAD_FUNCTION"] = xr.DataArray(
            np.zeros(shape, dtype=float),
            dims=("time", "frequency", "polarization", "l", "m"),
        )
        xds_mg.attrs["data_groups"] = {
            "base": {"sky": "SKY"},
            "psf": {"point_spread_function": "POINT_SPREAD_FUNCTION"},
        }
        self.xds_multi_group = xds_mg

    def time_xr_img_accessor_registration(self, xds):
        """Benchmark ImageXds accessor registration and meta property access."""
        _ = xds.xr_img._xds
        _ = xds.xr_img.meta

    def time_test_func(self, xds):
        """Benchmark test_func on a valid image dataset."""
        xds.xr_img.test_func()

    def time_get_lm_cell_size(self, xds):
        """Benchmark get_lm_cell_size returning the lm cell size in radians."""
        xds.xr_img.get_lm_cell_size()

    def time_add_uv_coordinates(self, xds):
        """Benchmark add_uv_coordinates attaching u and v coords to the dataset."""
        # Note: internally in the xradio image_xds source code, assign_coords is called to
        # assign u,v and it does not mutate the xr.Dataset object. The second time it
        # runs, it reassigns self.xds on the accessor instance of xds.xr.image. 
        # For timing purposes, this does not matter much here.
        xds.xr_img.add_uv_coordinates()

    def time_get_uv_in_lambda(self, xds):
        """Benchmark get_uv_in_lambda converting uv coordinates to wavelengths."""
        frequency = 1.412e9
        self.xds_with_uv.xr_img.get_uv_in_lambda(frequency)

    def time_get_reference_pixel_indices_lm(self, xds):
        """Benchmark get_reference_pixel_indices locating l=0, m=0 pixel."""
        xds.xr_img.get_reference_pixel_indices()

    def time_get_reference_pixel_indices_uv(self, xds):
        """Benchmark get_reference_pixel_indices when uv coordinates are present."""
        self.xds_with_uv.xr_img.get_reference_pixel_indices()

    def time_add_data_group(self, xds):
        """Benchmark add_data_group adding a new data group to the image dataset."""
        new_group_name = "new_group"
        new_group_spec = {"sky": "SKY_NEW"}
        xds.xr_img.add_data_group(new_group_name, new_group_spec)

    def time_sel_without_data_group_name(self, xds):
        """Benchmark sel without data_group_name delegating to xarray.Dataset.sel."""
        xds.xr_img.sel(polarization="I")

    def time_sel_with_data_group_name_kwarg(self, xds):
        """Benchmark sel(data_group_name=...) keyword-argument calling convention.

        Corresponds to pytest.param id="kwarg" in the original parametrized test.
        """
        self.xds_multi_group.xr_img.sel(data_group_name="base")

    def time_sel_with_data_group_name_indexers_dict(self, xds):
        """Benchmark sel(indexers={"data_group_name": ...}) calling convention.

        Corresponds to pytest.param id="indexers_dict" in the original parametrized test.
        """
        self.xds_multi_group.xr_img.sel(indexers={"data_group_name": "base"})
