import numpy
import os
import pytest

from ewokspdf.tasks.config import PdfGetXConfig
from ewokspdf.tasks.processor import PdfGetXProcessor


@pytest.fixture(scope="session")
def requires_diffpy():
    try:
        import diffpy.pdfgetx  # noqa F401
    except ImportError:
        pytest.skip("requires 'diffpy'")


@pytest.fixture()
def setup_save_data(requires_diffpy):
    # Define file paths
    datadir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "data", "save")
    config_file = os.path.join(datadir, "config.cfg")
    data_file = os.path.join(datadir, "CeO2.dat")

    # Configuration inputs
    config_inputs = {"filename": config_file}

    # Load data
    data = numpy.genfromtxt(data_file, delimiter="")

    # Create PdfGetXConfig instance and execute
    get_config = PdfGetXConfig(inputs=config_inputs)
    get_config.execute()
    config = get_config.get_output_values()

    # Extract data columns
    radial = data[:, 0]
    intensity = data[:, 1]

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
    processor_outputs = pdf_processor.get_output_values()
    return processor_outputs["results"]
