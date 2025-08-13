import numpy as np
import json
import logging
from ewokscore import Task
from silx.io.url import DataUrl
from silx.io import h5py_utils

_logger = logging.getLogger(__name__)


class PdfGetXAverage(
    Task,
    input_names=[
        "nxdata_url",
    ],
    optional_input_names=[
        "average_every",
    ],
    output_names=[
        "radial",
        "intensity",
        "info",
    ],
):
    """Average a list of 1D XRPD patterns from provided output of IntegrateBlissScan

    Inputs:
        - nxdata_url: .h5 path with NXData url
        - average_every: how many rows to average over;
            - 'all' for all rows,
            - '1' for no averaging,
            - or any integer divisor of the total number of rows
    Outputs:
        - radial: 1D array
        - intensity: 1D or 2D array based on average_every
        - info: dict with radial_units and wavelength
    """

    def run(self):
        valid_strings = ["all"]
        minimum_valid_integer = 1

        nxdata_url = DataUrl(self.inputs.nxdata_url)

        average_every = "all"
        if self.inputs.average_every:
            average_every = self.inputs.average_every

        if isinstance(average_every, str):
            if average_every.isnumeric():
                average_every = int(average_every)
            elif average_every in valid_strings:
                pass
            else:
                average_every = None

        if average_every not in valid_strings and not (
            isinstance(average_every, int) and average_every >= minimum_valid_integer
        ):
            message = "average_every must be 'all', 1, or a positive integer"
            _logger.error(message)
        else:
            message = "Valid average_every received."
            _logger.info(message)

        with h5py_utils.open_item(
            nxdata_url.file_path(), nxdata_url.data_path()
        ) as NXIn:
            intensity = NXIn[NXIn.attrs["signal"]][:]
            radial = NXIn[NXIn.attrs["axes"][1]][:]
            info = json.loads(NXIn.parent["configuration/data"][()])
        if intensity.ndim == 1:
            pass
        elif intensity.ndim == 2:
            if average_every == 1:
                info["nb_avg"] = 1
                pass
            elif average_every == "all":
                info["nb_avg"] = intensity.shape[0]
                intensity = np.mean(intensity, axis=0)
            else:
                if intensity.shape[0] % average_every != 0:
                    message = "The last chunk is shorter than the others!"
                    _logger.warning(message)
                chunks = list()
                nb_avg = list()
                for i in range(0, intensity.shape[0], average_every):
                    chunk = intensity[i : average_every + i]
                    nb_avg.append(len(chunk))
                    chunks.append(np.mean(chunk, axis=0))
                info["nb_avg"] = nb_avg
                intensity = np.array(chunks)
        else:
            message = "intensity dimension %s not supported" % intensity.ndim
            _logger.warning(message)
            raise ValueError(message)

        self.outputs.intensity = intensity
        self.outputs.radial = radial
        self.outputs.info = info
