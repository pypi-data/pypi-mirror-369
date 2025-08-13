import os
import pytest

from ewokspdf.tasks.config import PdfGetXConfig
from ewokspdf.tasks.constants import PDF_CONFIG_PARSED


@pytest.fixture()
def pdfgetx_config_file():
    datadir = os.path.abspath(os.path.dirname(__file__))
    filename = os.path.join(datadir, "data/config/config.cfg")
    return filename


def test_pdfgetx_config(requires_diffpy, pdfgetx_config_file):
    """Test PDFgetX parameters from file"""
    inputs = {"filename": pdfgetx_config_file}
    task = PdfGetXConfig(inputs=inputs)
    task.execute()
    actual_values = task.get_output_value("pdfgetx_options")
    expected_values = dict(PDF_CONFIG_PARSED)
    _assert_pdfgetx_parameter(actual_values, expected_values)


def test_pdfgetx_config_overwrite(requires_diffpy, pdfgetx_config_file):
    """Test PDFgetX parameters from file with overwriting"""
    inputs = {"filename": pdfgetx_config_file, "pdfgetx_options_dict": {"rmin": 1}}
    task = PdfGetXConfig(inputs=inputs)
    task.execute()
    actual_values = task.get_output_value("pdfgetx_options")
    expected_values = dict(PDF_CONFIG_PARSED)
    expected_values["rmin"] = 1
    _assert_pdfgetx_parameter(actual_values, expected_values)


def _assert_pdfgetx_parameter(actual_values, expected_values):
    for attribute, expected_value in expected_values.items():
        # Check if the attribute exists in the object
        assert hasattr(actual_values, attribute), f"Attribute '{attribute}' is missing."
        actual_value = getattr(actual_values, attribute)

        if (
            attribute == "bgscale"
        ):  # For some reasons bgscale is not a single value but parsed as a list...
            assert float(str(actual_value[0])) == float(
                expected_value
            ), f"Attribute '{attribute}' has an unexpected value: {actual_value} (expected: {expected_value})."
            continue

        if (
            attribute == "backgroundfile"
        ):  # For some reasons backgroundfile is not a single value but parsed as a list...
            assert (
                str(actual_value[0]) == expected_value
            ), f"Attribute '{attribute}' has an unexpected value: {actual_value} (expected: {expected_value})."
            continue

        if attribute == "outputtype":  # Need an extra step to convert string to list
            assert actual_value == expected_value.split(
                ", "
            ), f"Attribute '{attribute}' has an unexpected value: {actual_value} (expected: {expected_value})."
            continue

        if attribute in [
            "force",
            "interact",
        ]:  # Keys that can be yes/no are parsed as True/False #TODO Handle the case 'once' for force
            if expected_value.lower() in ["true", "yes", "on", "1"]:
                expected_value = True
            elif expected_value.lower() in ["false", "no", "off", "0"]:
                expected_value = False
            assert (
                actual_value == expected_value
            ), f"Attribute '{attribute}' has an unexpected value: {actual_value} (expected: {expected_value})."
            continue

        if (
            expected_value == "" or expected_value == "none"
        ):  # Do not consider empty keys
            continue
        elif (
            str(expected_value).replace(".", "").isnumeric()
        ):  # Check if the keys are numeric needs extra str to float step
            assert actual_value == float(
                expected_value
            ), f"Attribute '{attribute}' has an unexpected value: {float(actual_value)} (expected: {float(expected_value)})."
        else:
            assert (
                actual_value == expected_value
            ), f"Attribute '{attribute}' has an unexpected value: {actual_value} (expected: {expected_value})."
