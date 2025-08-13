from __future__ import annotations
from collections import namedtuple

PhysicalQuantity = namedtuple("PhysicalQuantity", ("name", "unit"))

CONFIG_ASCII_HEADER = """[DEFAULT]

version = diffpy.pdfgetx-2.2.1

# input and output specifications
dataformat = QA
inputfile = CeO2.dat
backgroundfile = background.xy
outputtype = fq

# PDF calculation setup
mode = xray
composition = CeO2
bgscale = 0
rpoly = 0
qmaxinst = 0
qmin = 0
qmax = 0
rmin = 0
rmax = 0
rstep = 0

# End of config --------------------------------------------------------------
"""

DATA_ASCII_HEADER = """
#### start data
#S 1
#L {} {}"""


SIGNAL_TYPES: dict[str, dict[str, PhysicalQuantity]] = {
    "iq": {
        "x": PhysicalQuantity("Q", "Å$^{-1}$"),
        "y": PhysicalQuantity("intensity", "a.u."),
    },
    "sq": {"x": PhysicalQuantity("Q", "Å$^{-1}$"), "y": PhysicalQuantity("S", "a.u.")},
    "fq": {
        "x": PhysicalQuantity("Q", "Å$^{-1}$"),
        "y": PhysicalQuantity("F", "Å$^{-1}$"),
    },
    "gr": {"x": PhysicalQuantity("r", "Å"), "y": PhysicalQuantity("G", "Å$^{-2}$")},
}

PDF_CONFIG_PARSED = {
    "dataformat": "QA",
    "backgroundfile": "./background.xy",
    "datapath": "",
    "bgscale": "1",
    "composition": "CeO2",
    "force": "yes",
    "interact": "yes",
    "mode": "xray",
    "output": "@r.@o",
    "outputtype": "iq, sq, fq, gr",
    "plot": "none",
    "qmax": "25",
    "qmaxinst": "25",
    "qmin": "1.10",
    "rmax": "30.0",
    "rmin": "0.0",
    "rpoly": "1.8",
    "rstep": "0.01",
    "wavelength": "0.1408839",
}
