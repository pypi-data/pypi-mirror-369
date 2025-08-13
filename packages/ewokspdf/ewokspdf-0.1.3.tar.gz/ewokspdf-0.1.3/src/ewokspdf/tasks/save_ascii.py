import os
import logging
import numpy as np
from ewokscore import Task

from ewokspdf.tasks.constants import (
    CONFIG_ASCII_HEADER,
    DATA_ASCII_HEADER,
    SIGNAL_TYPES,
)

_logger = logging.getLogger(__name__)


class PdfGetXSaveAscii(
    Task,
    input_names=["filename", "results", "info"],
    output_names=["saved", "filenames"],
):
    """Saves the PDF result (iq, sq, fq, gr) in separate ASCII files

    Inputs:
        - filename: Path to the base file used to save data.
        - results: List of PDFGetter objects with attributes for output types.
        - info: dict with unit, wavelength, and nb_avg
    Outputs:
        - saved: True if files are saved successfully.
        - filenames: List of saved filenames.
    """

    def run(self):
        filename = os.path.abspath(self.inputs.filename)
        output_dir = os.path.dirname(filename)
        os.makedirs(output_dir, exist_ok=True)

        results = self.inputs.results
        nb_avg = self.inputs.info["nb_avg"]

        self.outputs.filenames = []

        for idx, result in enumerate(results):
            for signal_type, signal_quantities in SIGNAL_TYPES.items():
                signal = getattr(result, signal_type, None)
                if signal is None or not np.any(signal):
                    _logger.debug(f"Signal '{signal_type}' is empty or missing.")
                    continue

                data = np.stack(signal, axis=1)
                config_header = self._generate_config_header(result.config, signal_type)
                data_header = DATA_ASCII_HEADER.format(
                    f"#{signal_quantities['x'].name} ({signal_quantities['x'].unit})",
                    f"#{signal_quantities['y'].name} ({signal_quantities['y'].unit})",
                )

                header = config_header + data_header
                # Incrementing save_path based on enumerate index
                if isinstance(nb_avg, list):
                    save_path = filename.replace(
                        ".h5", f"_{idx}_nb_avg{nb_avg[idx]}.{signal_type}"
                    )
                else:
                    save_path = filename.replace(
                        ".h5", f"_nb_avg{nb_avg}.{signal_type}"
                    )
                np.savetxt(save_path, data, fmt="%10.10f", header=header, comments="")
                _logger.debug(f"'{signal_type}' File saved to {save_path}")
                self.outputs.filenames.append(save_path)

        self.outputs.saved = bool(self.outputs.filenames)

    def _generate_config_header(self, config, signal_type):
        """Generate configuration header based on the signal type."""
        config.outputtypes = signal_type
        header_lines = []

        for line in CONFIG_ASCII_HEADER.splitlines():
            if "=" in line:
                key, _ = line.split("=", 1)
                key = key.strip()
                if hasattr(config, key):
                    value = getattr(config, key)
                    header_lines.append(f"{key} = {value}")
            else:
                header_lines.append(line)

        return "\n".join(header_lines) + "\n"
