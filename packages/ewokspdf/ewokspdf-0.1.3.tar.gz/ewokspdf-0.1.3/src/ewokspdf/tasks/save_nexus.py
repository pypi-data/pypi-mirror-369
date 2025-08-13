import h5py
import os.path
import json
import re
import numpy as np

from silx.io.dictdump import dicttonx
from ewoksxrpd.tasks.data_access import TaskWithDataAccess

from ewokspdf.tasks.constants import SIGNAL_TYPES

try:
    from diffpy import pdfgetx

    VERSION = pdfgetx.__version__
except ImportError:
    VERSION = None


class PdfGetXSaveNexus(
    TaskWithDataAccess,
    input_names=[
        "nxdata_url",
        "results",
        "pdfgetx_options",
        "info",
    ],
    optional_input_names=["subscan"],
    output_names=["output_url"],
):
    """Saves the PDF results (iq, sq, fq, gr) in a NeXus file

    Inputs:
        - nxdata_url: .h5 path with NXData url in which the data will be saved
        - results: List of PDFGetter object with attributes defined by outputtype. Attributes are tuples with [0] X (radial) and [1] Y (intensity)
    Outputs:
        - pdfgetx_options: pdfgetx.PDFConfig object containing the configuration
    """

    def run(self):
        full_nxdata_url = self.inputs.nxdata_url
        detector_name = re.search(r"/([^/]+)_integrate/", full_nxdata_url).group(1)
        nxdata_url = re.match(r"^(.*?\.h5::/?\d+\.\d+/)", full_nxdata_url).group(1)
        results = self.inputs.results
        pdfgetx_options_dict = pdfgetx_config_as_nxdict(self.inputs.pdfgetx_options)
        nb_avg = {"nb_avg": self.inputs.info["nb_avg"]}

        collected_data = {
            signal_type: {"axes": [], "signals": []} for signal_type in SIGNAL_TYPES
        }

        for result in results:
            for signal_type, signal_quantities in SIGNAL_TYPES.items():
                axis, signal = getattr(result, signal_type)
                collected_data[signal_type]["axes"].append(axis)
                collected_data[signal_type]["signals"].append(signal)

        for signal_type in collected_data:
            collected_data[signal_type]["axes"] = np.array(
                collected_data[signal_type]["axes"]
            )
            collected_data[signal_type]["signals"] = np.array(
                collected_data[signal_type]["signals"]
            )

        with self.open_h5item(nxdata_url, mode="a", create=True) as data_parent:
            assert isinstance(data_parent, h5py.Group)
            nxprocess = data_parent.create_group(f"{detector_name}_PDF")
            nxprocess.attrs["NX_class"] = "NXprocess"

            dicttonx(
                pdfgetx_options_dict,
                data_parent.file,
                h5path=f"{nxprocess.name}",
                update_mode="modify",
            )
            dicttonx(
                nb_avg,
                data_parent.file,
                h5path=f"{nxprocess.name}/averaging_options",
                update_mode="modify",
            )
            for signal_type, signal_quantities in SIGNAL_TYPES.items():
                nxdata = nxprocess.create_group(signal_type)
                nxdata.attrs["NX_class"] = "NXdata"

                signal_dset = nxdata.create_dataset(
                    signal_type, data=collected_data[signal_type]["signals"]
                )
                nxdata.attrs["signal"] = signal_type

                signal_dset.attrs["long_name"] = signal_quantities["y"].name
                signal_dset.attrs["units"] = signal_quantities["y"].unit

                axis_name, axis_unit = (
                    signal_quantities["x"].name,
                    signal_quantities["x"].unit,
                )
                axis_dset = nxdata.create_dataset(
                    axis_name, data=collected_data[signal_type]["axes"]
                )
                axis_dset.attrs["unit"] = axis_unit
                nxdata.attrs["axes"] = axis_name

                nxprocess.attrs["default"] = signal_type

            nxprocess.parent.attrs["default"] = os.path.basename(nxprocess.name)
            self.outputs.output_url = f"silx://{nxdata_url}{detector_name}_PDF"


def pdfgetx_config_as_nxdict(obj):
    """
    Convert an object's attributes into an NXtree dictionary.

    Args:
        obj (object): The object whose attributes are to be converted.

    Returns:
        dict: An NXtree dictionary with configuration details.
    """
    if obj is None:
        raise ValueError("The object cannot be None.")

    if not hasattr(obj, "__dict__"):
        raise TypeError(
            "The provided object does not have attributes accessible via __dict__."
        )

    pdfgetx_config = {key: value for key, value in vars(obj).items()}
    print(pdfgetx_config)
    nxtree_dict = {
        "@NX_class": "NXprocess",
        "program": "pdfgetx",
        "version": VERSION,
    }
    nxtree_dict["configuration"] = {
        "@NX_class": "NXnote",
        "type": "application/json",
        "data": json.dumps(pdfgetx_config),
    }
    return nxtree_dict
