import numpy as np

from astroviper.core.imaging.fft import fft_lm_to_uv
from astroviper.core.imaging.ifft import ifft_uv_to_lm


class TestFFTiFFT:
    """
    Benchmarks for FFT and iFFT array operations.
    Originally adapted from and extended to add more image sizes:
    https://github.com/casangi/astroviper/blob/main/tests/unit/core/imaging/test_fft_ifft.py
    """

    version = "astroviper 0.0.30"

    params = [128, 256, 512]
    param_names = ["image_size"]

    def setup(self, image_size):
        self.axes = (0, 1)

        self.sky_center = np.zeros((image_size, image_size))
        self.sky_center[image_size // 2, image_size // 2] = 1

        self.sky_offset = np.zeros((image_size, image_size))
        self.sky_offset[50, 40] = 1

        self.aperture_center = fft_lm_to_uv(self.sky_center, self.axes)
        self.aperture_offset = fft_lm_to_uv(self.sky_offset, self.axes)

    def time_fft_center_point(self, image_size):
        fft_lm_to_uv(self.sky_center, self.axes)

    def time_ifft_center_point(self, image_size):
        ifft_uv_to_lm(self.aperture_center, self.axes)

    def time_round_trip_center_point(self, image_size):
        aperture_uv = fft_lm_to_uv(self.sky_center, self.axes)
        ifft_uv_to_lm(aperture_uv, self.axes)

    def time_fft_offset_point(self, image_size):
        fft_lm_to_uv(self.sky_offset, self.axes)

    def time_ifft_offset_point(self, image_size):
        ifft_uv_to_lm(self.aperture_offset, self.axes)

    def time_round_trip_offset_point(self, image_size):
        aperture_uv = fft_lm_to_uv(self.sky_offset, self.axes)
        ifft_uv_to_lm(aperture_uv, self.axes)

