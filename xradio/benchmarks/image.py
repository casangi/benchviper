import numpy as np
import numpy.ma as ma
import os
import shutil
import tempfile

from xradio.image import (
    load_image,
    make_empty_aperture_image,
    make_empty_lmuv_image,
    make_empty_sky_image,
    open_image,
    write_image,
)
from xradio.image._util._casacore.common import _create_new_image as create_new_image
from xradio.testing.image import (
    create_empty_test_image,
    download_image,
    remove_path,
)


class TestLoadImage:
    """
    Benchmarks for load_image with visibility normalization images.
    Originally adapted from:
    https://github.com/casangi/xradio/blob/main/tests/unit/image/test_image.py
    TestLoadImage class
    at commit:
    HEAD
    """

    version = "xradio 1.0.2"

    def setup_cache(self):
        # perform the expensive operations once (per env, per commit), see
        # https://asv.readthedocs.io/en/stable/writing_benchmarks.html#setup-and-teardown-functions

        # originally adapted from tests/unit/image/test_image.py
        tmp_dir = tempfile.mkdtemp()
        data = np.arange(8, dtype=np.float32).reshape(4, 2, 1, 1)

        imagename = os.path.join(tmp_dir, "synthetic.sumwt")
        with create_new_image(imagename, shape=list(data.shape)) as im:
            im.put(ma.masked_array(data, np.zeros_like(data, dtype=bool)))

        mask = np.zeros_like(data, dtype=bool)
        mask[1, 0, 0, 0] = True
        masked_imagename = os.path.join(tmp_dir, "masked.sumwt")
        with create_new_image(
            masked_imagename, shape=list(data.shape), mask="MASK_0"
        ) as im:
            im.put(ma.masked_array(data, mask))

        return {
            "tmp_dir": tmp_dir,
            "imagename": imagename,
            "masked_imagename": masked_imagename,
        }

    def teardown_cache(self, cache):
        shutil.rmtree(cache["tmp_dir"], ignore_errors=True)

    def time_block_squeezes_spatial_axes(self, cache):
        """Benchmark load_image dropping singleton l/m from a visibility normalization image."""
        load_image({"visibility_normalization": cache["imagename"]})

    def time_mask_squeezes_spatial_axes(self, cache):
        """Benchmark load_image dropping singleton l/m from a masked visibility normalization image."""
        load_image({"visibility_normalization": cache["masked_imagename"]})


class TestOpenImageCasa:
    """
    Benchmarks for open_image with CASA images.
    Originally adapted from:
    https://github.com/casangi/xradio/blob/main/tests/unit/image/test_image.py
    TestOpenImageCasa class
    at commit:
    HEAD
    """

    version = "xradio 1.0.2"

    _imname = "casa_test_image.im"
    _uv_image = "complex_valued_uv.im"

    def setup_cache(self):
        # perform the expensive operations once (per env, per commit), see
        # https://asv.readthedocs.io/en/stable/writing_benchmarks.html#setup-and-teardown-functions

        # originally adapted from tests/unit/image/test_image.py
        download_image(self._imname)
        download_image(self._uv_image)
        return {"imname": self._imname, "uv_image": self._uv_image}

    def teardown_cache(self, cache):
        remove_path(cache["imname"])
        remove_path(cache["uv_image"])

    def time_open_image(self, cache):
        """Benchmark open_image on a CASA sky image with sky coordinates."""
        open_image(cache["imname"], {"frequency": 5})

    def time_open_image_no_sky(self, cache):
        """Benchmark open_image on a CASA sky image without sky coordinates."""
        open_image(cache["imname"], {"frequency": 5}, False, False)

    def time_open_uv_image(self, cache):
        """Benchmark open_image on a UV (aperture) CASA image."""
        open_image(cache["uv_image"])


class TestWriteImageCasa:
    """
    Benchmarks for write_image to CASA output format.
    Originally adapted from:
    https://github.com/casangi/xradio/blob/main/tests/unit/image/test_image.py
    TestWriteImageCasa class
    at commit:
    HEAD
    """

    version = "xradio 1.0.2"

    # write_image creates files on disk; number=1 ensures each sample of timing measurement
    # gets its own setup()/teardown() cycle so the output path is always clean.
    # Before measuring, asv will call the function multiple times during the warmup_time window.
    # teardown does not run between the warmup runs, therefore it needs to be set to 0.0
    # to avoid overwriting output_uv.im in time_write_image_uv
    number = 1
    warmup_time = 0

    _imname = "casa_test_image.im"
    _uv_image = "complex_valued_uv.im"

    def setup_cache(self):
        # perform the expensive operations once (per env, per commit), see
        # https://asv.readthedocs.io/en/stable/writing_benchmarks.html#setup-and-teardown-functions

        # originally adapted from tests/unit/image/test_image.py
        download_image(self._imname)
        xds = open_image(self._imname, {"frequency": 5})
        download_image(self._uv_image)
        xds_uv = open_image(self._uv_image)
        return {"xds": xds, "xds_uv": xds_uv}

    def teardown_cache(self, cache):
        remove_path(self._imname)
        remove_path(self._uv_image)

    def setup(self, cache):
        self.xds = cache["xds"]
        self.xds_uv = cache["xds_uv"]
        self.tmp_dir = tempfile.mkdtemp()


    def teardown(self, cache):
        shutil.rmtree(self.tmp_dir, ignore_errors=False)

    def time_write_image_numpy_data_var(self, cache):
        """Benchmark write_image writing a sky image with numpy data var to CASA."""
        write_image(
            self.xds,
            os.path.join(self.tmp_dir, "out.im"),
            "casa",
            overwrite=True,
        )

    def time_write_image_uv(self, cache):
        """Benchmark write_image writing a UV aperture image to CASA."""
        write_image(
            self.xds_uv,
            os.path.join(self.tmp_dir, "output_uv.im"),
            "casa",
            overwrite=False
        )

    def time_write_image_overwrite(self, cache):
        """Benchmark write_image with overwrite=True on an existing CASA image."""
        outname = os.path.join(self.tmp_dir, "overwrite.im")
        write_image(self.xds, outname, out_format="casa", overwrite=True)
        write_image(self.xds, outname, out_format="casa", overwrite=True)


class TestCasaRoundtrip:
    """
    Benchmarks for the CASA round-trip: open_image → write_image (CASA).
    Originally adapted from:
    https://github.com/casangi/xradio/blob/main/tests/unit/image/test_image.py
    TestCasaRoundtrip class
    at commit:
    HEAD

    Each benchmark performs the complete open + write in a single method,
    mirroring TestCasaRoundtrip.setup_class in the original tests which calls
    both open_image and write_image together before any assertions are made.
    """

    version = "xradio 1.0.2"
    # write_image creates files on disk; number=1 ensures each timing measurement
    # gets its own setup()/teardown() cycle so the output path is always clean.
    # warmup_time=0 prevents asv from calling the benchmark function repeatedly
    # before timing (warmup does not run setup/teardown between calls, so the
    # second warmup call would find the output file already present).
    number = 1
    warmup_time = 0

    _imname: str = "casa_test_image.im"
    _imname3: str = "no_mask.im"

    def setup_cache(self):
        # perform the expensive operations once (per env, per commit), see
        # https://asv.readthedocs.io/en/stable/writing_benchmarks.html#setup-and-teardown-functions

        # originally adapted from tests/unit/image/test_image.py
        download_image(self._imname)
        download_image(self._imname3)
        return {"imname": self._imname, "imname3": self._imname3}

    def teardown_cache(self, cache):
        remove_path(cache["imname"])
        remove_path(cache["imname3"])

    def setup(self, cache):
        self.tmp_dir = tempfile.mkdtemp()

    def teardown(self, cache):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def time_open_and_write(self, cache):
        """Benchmark full CASA round-trip: open_image → write_image (with sky coordinates)."""
        xds = open_image(cache["imname"], {"frequency": 5})
        write_image(
            xds,
            os.path.join(self.tmp_dir, "out.im"),
            out_format="casa",
            overwrite=True,
        )

    def time_open_and_write_no_sky(self, cache):
        """Benchmark full CASA round-trip: open_image → write_image (without sky coordinates)."""
        xds = open_image(cache["imname"], {"frequency": 5}, False, False)
        write_image(
            xds,
            os.path.join(self.tmp_dir, "out_no_sky.im"),
            out_format="casa",
        )

    def time_open_and_write_masking(self, cache):
        """Benchmark full CASA round-trip on a no-mask image: open_image → write_image.

        Corresponds to test_masking (case 1: no mask + no NaNs) in the original
        TestCasaRoundtrip class, using the no_mask.im (_imname3) source image.
        """
        xds = open_image(cache["imname3"])
        write_image(
            xds,
            os.path.join(self.tmp_dir, "out_masking.im"),
            out_format="casa",
        )


class TestZarrRoundtrip:
    """
    Benchmarks for the zarr round-trip: open_image (CASA) → write_image (zarr) → open_image (zarr).
    Originally adapted from:
    https://github.com/casangi/xradio/blob/main/tests/unit/image/test_image.py
    TestZarrRoundtrip class
    at commit:
    HEAD

    Each benchmark performs write_image and the subsequent open_image in the
    same method, mirroring how the original TestZarrRoundtrip.setup_class calls
    write_image then open_image together, and TestZarrRoundtrip.test_beam does
    the same within a single test method.
    """

    version = "xradio 1.0.2"
    # write_image creates files on disk; number=1 ensures each timing measurement
    # gets its own setup()/teardown() cycle so the output path is always clean.
    # warmup_time=0 prevents asv from calling the benchmark function repeatedly
    # before timing (warmup does not run setup/teardown between calls, so the
    # second warmup call would find the output file already present).
    number = 1
    warmup_time = 0

    _imname = "casa_test_image.im"
    _zarr_beam_test = "bench_beam_test.zarr"

    def setup_cache(self):
        # perform the expensive operations once (per env, per commit), see
        # https://asv.readthedocs.io/en/stable/writing_benchmarks.html#setup-and-teardown-functions

        # originally adapted from tests/unit/image/test_image.py
        from xradio.testing.image.generators import make_beam_fit_params

        download_image(self._imname)
        xds = open_image(self._imname, {"frequency": 5})
        xds_with_beam = xds.assign(BEAM_FIT_PARAMS=make_beam_fit_params(xds))
        xds_with_beam["BEAM_FIT_PARAMS"].attrs["units"] = "rad"
        write_image(xds_with_beam, self._zarr_beam_test, out_format="zarr", overwrite=True)
        bds = open_image(self._zarr_beam_test)
        return {
            "imname": self._imname,
            "zarr_beam_test": self._zarr_beam_test,
            "xds": xds,
            "bds": bds,
        }

    def teardown_cache(self, cache):
        remove_path(cache["imname"])
        remove_path(cache["zarr_beam_test"])

    def setup(self, cache):
        self.xds = cache["xds"]
        self.bds = cache["bds"]
        self.tmp_dir = tempfile.mkdtemp()

    def teardown(self, cache):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def time_zarr_roundtrip(self, cache):
        """Benchmark write_image (zarr) + open_image (zarr) for a CASA-derived dataset."""
        zarr_out = os.path.join(self.tmp_dir, "out.zarr")
        write_image(self.xds, zarr_out, out_format="zarr")
        open_image(zarr_out)

    def time_zarr_roundtrip_beam_test(self, cache):
        """Benchmark write_image (zarr) + open_image (zarr) using a pre-built beam-parameter store.

        Corresponds to test_beam in the original TestZarrRoundtrip class, using the
        bench_beam_test.zarr (_zarr_beam_test) source created in setup_cache.
        """
        beam_test_out = os.path.join(self.tmp_dir, "out_beam_test.zarr")
        write_image(self.bds, beam_test_out, out_format="zarr")
        open_image(beam_test_out)


class TestWriteImageZarr:
    """
    Benchmarks for write_image to zarr format with UV (aperture) images.
    Originally adapted from:
    https://github.com/casangi/xradio/blob/main/tests/unit/image/test_image.py
    TestWriteImageZarr class
    at commit:
    HEAD
    """

    version = "xradio 1.0.2"
    # write_image creates files on disk; number=1 ensures each timing measurement
    # gets its own setup()/teardown() cycle so the output path is always clean.
    # warmup_time=0 prevents asv from calling the benchmark function repeatedly
    # before timing (warmup does not run setup/teardown between calls, so the
    # second warmup call would find the output file already present).
    number = 1
    warmup_time = 0

    _uv_image = "complex_valued_uv.im"

    def setup_cache(self):
        # perform the expensive operations once (per env, per commit), see
        # https://asv.readthedocs.io/en/stable/writing_benchmarks.html#setup-and-teardown-functions

        # originally adapted from tests/unit/image/test_image.py
        download_image(self._uv_image)
        xds_uv = open_image({"APERTURE": self._uv_image})
        return {"uv_image": self._uv_image, "xds_uv": xds_uv}

    def teardown_cache(self, cache):
        remove_path(cache["uv_image"])

    def setup(self, cache):
        self.xds_uv = cache["xds_uv"]
        self.tmp_dir = tempfile.mkdtemp()

    def teardown(self, cache):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def time_write_uv_image_zarr(self, cache):
        """Benchmark write_image writing a UV aperture image to zarr."""
        write_image(
            self.xds_uv,
            os.path.join(self.tmp_dir, "out_uv.zarr"),
            "zarr",
        )


class TestOpenImageFits:
    """
    Benchmarks for open_image with FITS images.
    Originally adapted from:
    https://github.com/casangi/xradio/blob/main/tests/unit/image/test_image.py
    TestOpenImageFits class
    at commit:
    HEAD
    """

    version = "xradio 1.0.2"

    _infits = "test_image.fits"

    def setup_cache(self):
        # perform the expensive operations once (per env, per commit), see
        # https://asv.readthedocs.io/en/stable/writing_benchmarks.html#setup-and-teardown-functions

        # originally adapted from tests/unit/image/test_image.py
        download_image(self._infits)
        return {"infits": self._infits}

    def teardown_cache(self, cache):
        remove_path(cache["infits"])

    def time_open_image_fits(self, cache):
        """Benchmark open_image reading a FITS image with sky coordinates."""
        open_image(cache["infits"], {"frequency": 5}, do_sky_coords=True)

    def time_open_image_fits_no_sky(self, cache):
        """Benchmark open_image reading a FITS image without sky coordinates."""
        open_image(cache["infits"], {"frequency": 5}, do_sky_coords=False)

    def time_open_image_fits_compute_mask_true(self, cache):
        """Benchmark open_image reading a FITS image with compute_mask=True.

        Corresponds to pytest.param id="compute_mask_true" in the original parametrized test.
        """
        open_image(cache["infits"], {"frequency": 5}, compute_mask=True)

    def time_open_image_fits_compute_mask_false(self, cache):
        """Benchmark open_image reading a FITS image with compute_mask=False.

        Corresponds to pytest.param id="compute_mask_false" in the original parametrized test.
        """
        open_image(cache["infits"], {"frequency": 5}, compute_mask=False)


class TestMakeEmptyImages:
    """
    Benchmarks for make_empty_sky_image, make_empty_aperture_image,
    and make_empty_lmuv_image factory functions.
    Originally adapted from:
    https://github.com/casangi/xradio/blob/main/tests/unit/image/test_image.py
    TestMakeEmptyImages class
    at commit:
    HEAD
    """

    version = "xradio 1.0.2"

    def time_make_empty_sky(self):
        """Benchmark make_empty_sky_image with sky coordinates.

        Corresponds to MAKE_EMPTY_CASES entry name="sky" in the original parametrized test.
        """
        create_empty_test_image(make_empty_sky_image, True)

    def time_make_empty_sky_no_coords(self):
        """Benchmark make_empty_sky_image without sky coordinates.

        Corresponds to MAKE_EMPTY_CASES entry name="sky_no_coords" in the original parametrized test.
        """
        create_empty_test_image(make_empty_sky_image, False)

    def time_make_empty_aperture(self):
        """Benchmark make_empty_aperture_image.

        Corresponds to MAKE_EMPTY_CASES entry name="aperture" in the original parametrized test.
        """
        create_empty_test_image(make_empty_aperture_image, None)

    def time_make_empty_lmuv(self):
        """Benchmark make_empty_lmuv_image with sky coordinates.

        Corresponds to MAKE_EMPTY_CASES entry name="lmuv" in the original parametrized test.
        """
        create_empty_test_image(make_empty_lmuv_image, True)

    def time_make_empty_lmuv_no_coords(self):
        """Benchmark make_empty_lmuv_image without sky coordinates.

        Corresponds to MAKE_EMPTY_CASES entry name="lmuv_no_coords" in the original parametrized test.
        """
        create_empty_test_image(make_empty_lmuv_image, False)
