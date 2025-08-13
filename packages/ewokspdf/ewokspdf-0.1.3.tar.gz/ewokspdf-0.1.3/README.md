# ewokspdf

The **ewokspdf Project** is a Python library designed to provide Pair Distribution Function (PDF) analysis ewoks workflow tasks. 
The library is based on the calculations of [PDFgetX3](https://www.diffpy.org/products/pdfgetx.html) python API. The main tasks are: pattern averaging, `pdfgetx` configuration, `pdfgetx` processing and saving in box HDF5 and ASCII files.

## Installation

By default, at the ESRF, `ewokspdf` should be installed on `ewoks` workers with an Ansible script by the DAU team.

If you wish to install `ewokspdf` by yourself, you’ll need Python 3.9+ and `pip`. You can install the library directly from PyPI:

```bash
pip install ewokspdf
```

Alternatively, to install from source, clone this repository and run:

```bash
git clone https://gitlab.esrf.fr/workflow/ewoksapps/ewokspdf.git
cd ewokspdf
pip install -e .
```
`ewokspdf` has only two requirements: `ewoksxrpd` and `diffpy.pdfgetx`. `diffpy.pdgetx` can be downloaded [here](https://www.diffpy.org/products/pdfgetx.html). To install it you can run:

```bash
pip install ./diffpy.pdfgetx-VERSION.whl
```

So far, the diffpy version is 2.2.1 which supports python up to 3.10. The project is tested up to python 3.12 but the core would only work for pyton up to 3.10.

## Quickstart Guide

### Running an ewokspdf workflow


## How-To Guides

For detailed instructions on various tasks, please refer to the How-To Guides section in the documentation, which covers topics like:

- Configuration of the workflow
- Running the workflow locally
- Using the API to run specific tasks

## Documentation

Comprehensive documentation, including an API reference, tutorials, and conceptual explanations, can be found in the 
[docs directory](./doc) or online at the [ReadTheDocs page](https://ewokspdf.readthedocs.io).

## Contributing

Contributions are welcome! To contribute, please:

1. Clone the repository and create a new branch for your feature or fix.
2. Write tests and ensure that the code is well-documented.
3. Submit a merge request for review.

See the [CONTRIBUTING.md](./CONTRIBUTING.md) file for more details.

## License

This project is licensed under the MIT License. See the [LICENSE.md](./LICENSE.md) file for details.

## Support

If you have any questions or issues, please open an issue on the Gitlab repository or contact us with a [data processing request ticket](https://requests.esrf.fr/plugins/servlet/desk/portal/41).
