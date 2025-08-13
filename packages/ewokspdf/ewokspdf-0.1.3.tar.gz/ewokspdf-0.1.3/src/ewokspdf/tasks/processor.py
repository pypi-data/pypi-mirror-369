from ewokscore import Task

try:
    from diffpy import pdfgetx
except ImportError:
    pdfgetx = None


class PdfGetXProcessor(
    Task,
    input_names=[
        "radial",
        "intensity",
        "info",
        "pdfgetx_options",
    ],
    output_names=[
        "results",
        "info",
        "pdfgetx_options",
    ],
):
    """Extracts the PDF signal from provided intensities and radial

    Inputs:
        - radial: 1D array
        - intensity: 1D or 2D array
        - info: dict with unit, wavelength, and nb_avg
        - pdfgetx_options: PDFConfig object
    Outputs:
        - results: List od PDFGetter object with attributes defined by outputtype. Attributes are tuples with [0] X (radial) and [1] Y (intensity)
        - info: dict with unit, wavelength, and nb_avg
        - pdfgetx_options: PDFConfig object
    """

    def run(self):
        cfg = self.inputs.pdfgetx_options
        if pdfgetx is None:
            raise ImportError(
                "diffpy.pdfgetx couldn't be imported, please download and install it from here: https://inventions.techventures.columbia.edu/technologies/xpdfsuite-an-end-to--M11-120/licenses/113"
            )
        worker = pdfgetx.PDFGetter(cfg)
        radial = self.inputs.radial
        intensity = self.inputs.intensity
        results = list()
        if intensity.ndim == 1:
            worker(radial, intensity)
            results.append(worker.copy())
        elif intensity.ndim == 2:
            for i in range(intensity.shape[0]):
                worker(radial, intensity[i, :])
                results.append(worker.copy())
        else:
            raise ValueError(f"Dimension {intensity.ndim} is not supported")
        self.outputs.results = results
        self.outputs.info = self.inputs.info
        self.outputs.pdfgetx_options = cfg
