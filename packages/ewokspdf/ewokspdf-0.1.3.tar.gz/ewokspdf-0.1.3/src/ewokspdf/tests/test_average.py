import os
import pytest
from silx.io.url import DataUrl
from silx.io import h5py_utils
from ewokspdf.tasks.average import PdfGetXAverage


@pytest.fixture
def data_path():
    datadir = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(
        datadir,
        "data",
        "average",
        "CeO2_processed.h5::1.1/frelon6_integrate/integrated",
    )


@pytest.fixture
def expected_shape(data_path):
    data_url = DataUrl(data_path)
    with h5py_utils.open_item(data_url.file_path(), data_url.data_path()) as NXIn:
        intensity_shape = NXIn[NXIn.attrs["signal"]].shape[0]
    return intensity_shape


def test_pdfgetx_no_averaging(data_path, expected_shape):
    average_inputs = {"nxdata_url": data_path, "average_every": 1}  # Use integer
    get_average = PdfGetXAverage(inputs=average_inputs)
    get_average.execute()
    results = get_average.get_output_values()

    assert results["intensity"].ndim == 2
    assert results["intensity"].shape[0] == expected_shape


def test_pdfgetx_average_all(data_path):
    average_inputs = {"nxdata_url": data_path, "average_every": "all"}
    get_average = PdfGetXAverage(inputs=average_inputs)
    get_average.execute()
    results = get_average.get_output_values()

    assert results["intensity"].ndim == 1


def test_pdfgetx_average_specific(data_path, expected_shape):
    for divisor in [2, 5]:
        average_inputs = {"nxdata_url": data_path, "average_every": str(divisor)}
        get_average = PdfGetXAverage(inputs=average_inputs)
        get_average.execute()
        results = get_average.get_output_values()

        assert results["intensity"].ndim == 2
        assert results["intensity"].shape[0] == expected_shape // divisor


def test_pdfgetx_average_partial(data_path, expected_shape):
    average_inputs = {"nxdata_url": data_path, "average_every": "7"}
    get_average = PdfGetXAverage(inputs=average_inputs)
    get_average.execute()
    results = get_average.get_output_values()

    expected_full_chunks = expected_shape // 7
    expected_remainder_chunk = expected_shape % 7
    expected_rows = expected_full_chunks + (1 if expected_remainder_chunk else 0)

    assert results["intensity"].ndim == 2
    assert results["intensity"].shape[0] == expected_rows
