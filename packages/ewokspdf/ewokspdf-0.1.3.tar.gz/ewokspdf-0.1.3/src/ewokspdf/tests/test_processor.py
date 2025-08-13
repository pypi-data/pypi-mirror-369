import os
import pytest
import numpy as np
from silx.io.url import DataUrl
from silx.io import h5py_utils

from ewokspdf.tasks.config import PdfGetXConfig
from ewokspdf.tasks.average import PdfGetXAverage
from ewokspdf.tasks.processor import PdfGetXProcessor

from ewokspdf.tasks.constants import SIGNAL_TYPES


@pytest.fixture()
def setup_data(requires_diffpy):
    # Define file paths
    datadir = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "data", "average"
    )
    configdir = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "data", "processor"
    )
    config_file = os.path.join(configdir, "config.cfg")

    # Configuration inputs
    config_inputs = {"filename": config_file}

    # Create PdfGetXConfig instance and execute
    get_config = PdfGetXConfig(inputs=config_inputs)
    get_config.execute()
    config = get_config.get_output_values()

    def get_scan_data(scan, average_every):
        # Average inputs
        nxdata_url = os.path.join(
            datadir, "CeO2_processed.h5::1.1/frelon6_integrate/integrated"
        )

        # Create PdfGetXAverage instance and execute
        get_average = PdfGetXAverage(
            inputs={"nxdata_url": nxdata_url, "average_every": average_every}
        )
        get_average.execute()
        average_result = get_average.get_output_values()

        radial = average_result["radial"]
        intensity = average_result["intensity"]

        # Processor inputs
        processor_inputs = {
            "radial": radial,
            "intensity": intensity,
            "info": {"unit": "q_A^-1"},
            "pdfgetx_options": config["pdfgetx_options"],
        }

        # Create PdfGetXProcessor instance and execute
        pdf_processor = PdfGetXProcessor(inputs=processor_inputs)
        pdf_processor.execute()
        outputs = pdf_processor.get_output_values()

        # Load true data
        true_data = {}
        for signal_type in SIGNAL_TYPES.keys():
            # Construct the data URL
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


def assert_data_close(outputs, true_data):
    result_list = outputs["results"]
    for idx, result_obj in enumerate(result_list):
        for signal_type in SIGNAL_TYPES.keys():
            computed_data = getattr(result_obj, signal_type)
            true_signal_data = true_data[signal_type]
            np.testing.assert_allclose(
                computed_data[0], np.squeeze(true_signal_data[0][idx]), rtol=1e-6
            )
            np.testing.assert_allclose(
                computed_data[1], np.squeeze(true_signal_data[1][idx]), atol=1e-6
            )


@pytest.mark.parametrize("scan, average_every", [("1.1", "all"), ("2.1", 30)])
def test_data_for_multiple_scans(scan, average_every, setup_data):
    # Get the function from the fixture
    get_scan_data = setup_data
    # Call the function with the parameters
    outputs, true_data = get_scan_data(scan, average_every)

    # Test iq, sq, fq, and gr by comparing the computed and true data
    assert_data_close(outputs, true_data)
