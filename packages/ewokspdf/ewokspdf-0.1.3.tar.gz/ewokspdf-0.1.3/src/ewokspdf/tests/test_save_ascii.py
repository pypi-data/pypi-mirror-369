import os
import pytest
import numpy as np
from ewokspdf.tasks.save_ascii import PdfGetXSaveAscii
from ewokspdf.tasks.constants import SIGNAL_TYPES
from ewokspdf.tasks.config import PdfGetXConfig
from ewokspdf.tasks.average import PdfGetXAverage
from ewokspdf.tasks.processor import PdfGetXProcessor
from silx.io.url import DataUrl
from silx.io import h5py_utils


@pytest.fixture()
def setup_data(requires_diffpy):
    # Define file paths
    datadir = os.path.join(os.path.dirname(__file__), "data", "average")
    configdir = os.path.join(os.path.dirname(__file__), "data", "processor")
    config_file = os.path.join(configdir, "config.cfg")

    # Configuration inputs
    config_inputs = {"filename": config_file}
    get_config = PdfGetXConfig(inputs=config_inputs)
    get_config.execute()
    config = get_config.get_output_values()

    def get_scan_data(scan, average_every):
        nxdata_url = os.path.join(
            datadir, "CeO2_processed.h5::1.1/frelon6_integrate/integrated"
        )
        get_average = PdfGetXAverage(
            inputs={"nxdata_url": nxdata_url, "average_every": average_every}
        )
        get_average.execute()
        average_result = get_average.get_output_values()

        radial = average_result["radial"]
        intensity = average_result["intensity"]

        processor_inputs = {
            "radial": radial,
            "intensity": intensity,
            "info": {"unit": "q_A^-1"},
            "pdfgetx_options": config["pdfgetx_options"],
        }
        pdf_processor = PdfGetXProcessor(inputs=processor_inputs)
        pdf_processor.execute()
        outputs = pdf_processor.get_output_values()

        # Load true data
        true_data = {}
        for signal_type in SIGNAL_TYPES.keys():
            data_url = DataUrl(
                os.path.join(
                    configdir,
                    f"CeO2_PDF_processed.h5::{scan}/frelon6_PDF/{signal_type}",
                )
            )
            with h5py_utils.open_item(
                data_url.file_path(), data_url.data_path()
            ) as NXIn:
                true_data[signal_type] = [
                    NXIn[NXIn.attrs["axes"]][:],
                    NXIn[NXIn.attrs["signal"]][:],
                ]
        return outputs, true_data

    return get_scan_data


@pytest.mark.parametrize("scan, average_every", [("1.1", "all"), ("2.1", 30)])
def test_pdfgetx_save_ascii(scan, average_every, setup_data, tmp_path):
    """
    Test the PdfGetXSaveAscii task using data from the setup pipeline.
    Validate that ASCII data matches the reference data in the NX file.
    """
    # Get processed results and true data from setup_data fixture
    get_scan_data = setup_data
    outputs, true_data = get_scan_data(scan, average_every)

    filename = tmp_path / "output_file.h5"
    save_task = PdfGetXSaveAscii(
        inputs={
            "filename": str(filename),
            "results": outputs["results"],
            "info": {"nb_avg": average_every},
        }
    )
    save_task.execute()

    # Retrieve filenames of saved ASCII files
    save_outputs = save_task.get_output_values()
    saved_files = save_outputs["filenames"]

    assert save_outputs["saved"] is True, "Files were not saved successfully."
    assert len(saved_files) > 0, "No files were saved."

    # Validate each signal type
    for idx, result in enumerate(outputs["results"]):
        for signal_type in SIGNAL_TYPES.keys():
            # Identify the corresponding ASCII file for the signal type
            expected_file = next(
                (
                    f
                    for f in saved_files
                    if signal_type in f and f"_nb_avg{average_every}" in f
                ),
                None,
            )
            assert (
                expected_file is not None
            ), f"File for signal '{signal_type}' not found."

            # Load data from the saved ASCII file
            saved_data = np.loadtxt(expected_file, comments="#", skiprows=26)

            # Get true data from NeXus (NX) file
            true_signal_x, true_signal_y = true_data[signal_type]
            true_signal_x = (
                true_signal_x[idx] if len(true_signal_x.shape) > 1 else true_signal_x
            )
            true_signal_y = (
                true_signal_y[idx] if len(true_signal_y.shape) > 1 else true_signal_y
            )

            # Compare ASCII data with NeXus data
            np.testing.assert_allclose(
                saved_data[:, 0],
                true_signal_x,
                rtol=1e-6,
                err_msg=f"Mismatch in {signal_type} x-axis data.",
            )
            np.testing.assert_allclose(
                saved_data[:, 1],
                true_signal_y,
                atol=1e-6,
                err_msg=f"Mismatch in {signal_type} y-axis data.",
            )
