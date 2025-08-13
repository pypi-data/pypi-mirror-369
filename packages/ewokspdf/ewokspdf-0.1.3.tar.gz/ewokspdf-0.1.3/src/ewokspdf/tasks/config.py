from ewokscore import Task

try:
    from diffpy import pdfgetx
except ImportError:
    pdfgetx = None


class PdfGetXConfig(
    Task,
    optional_input_names=["filename", "pdfgetx_options_dict"],
    output_names=["pdfgetx_options"],
):
    """Parse pdfgetx config parameters"""

    def run(self):
        if pdfgetx is None:
            raise RuntimeError("requires 'diffpy'")
        pdfgetx_options = self.merged_pdfgetx_config()
        self.outputs.pdfgetx_options = pdfgetx_options

    def merged_pdfgetx_config(self):
        """Merge pdfgetx options in this order of priority:

        - filename (lowest priority)
        - pdfgetx_options (highest priority)
        """
        if self.inputs.filename:
            options = pdfgetx.loadPDFConfig(self.inputs.filename)
        else:
            options = pdfgetx.PDFConfig()
        pdfgetx_options = self.get_input_value("pdfgetx_options_dict", dict())
        for key, value in pdfgetx_options.items():
            setattr(options, key, value)
        return options
