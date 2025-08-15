# Import packages and libraries
from pathlib import Path

# Import module and files
from fezrs.base import BaseTool
from fezrs.utils.type_handler import BandPathType


# Calculator class
class AFVICalculator(BaseTool):
    def __init__(self, nir_path: BandPathType, swir1_path: BandPathType):
        super().__init__(nir_path=nir_path, swir1_path=swir1_path)
        self.normalized_bands = self.files_handler.get_normalized_bands(
            requested_bands=["nir", "swir1"]
        )

    def _validate(self):
        pass

    def process(self):
        nir, swir1 = (self.normalized_bands[band] for band in ("nir", "swir1"))

        self._output = (nir - 0.66) * (swir1 / (nir + (0.66 * swir1)))
        return self._output

    def execute(
        self,
        output_path,
        title=None,
        figsize=(15, 10),
        show_axis=False,
        colormap="gray",
        show_colorbar=True,
        filename_prefix="Tool_output",
        dpi=1000,
        bbox_inches="tight",
        grid=True,
    ):
        return super().execute(
            output_path,
            title,
            figsize,
            show_axis,
            colormap,
            show_colorbar,
            filename_prefix,
            dpi,
            bbox_inches,
            grid,
        )


# NOTE - These block code for test the tools, delete before publish product
if __name__ == "__main__":
    nir_path = Path.cwd() / "data/NIR.tif"
    swir1_path = Path.cwd() / "data/SWIR1.tif"

    calculator = AFVICalculator(nir_path=nir_path, swir1_path=swir1_path).execute(
        output_path="./", title="AFVI output"
    )
