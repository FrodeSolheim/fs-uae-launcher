from fsgamesys.platforms.spectrum.fusespectrumdriver import FuseSpectrumDriver


class FsFuseSpectrumDriver(FuseSpectrumDriver):
    def __init__(self, gscontext):
        super().__init__(gscontext, fsemu=True)

    def configure_input_fsemu(self):
        for port_prefix in ["spectrum_port_1_", "spectrum_port_2_"]:
            for key, value in self.options.items():
                # Just pass on all port-related keys as-is
                if key.startswith(port_prefix):
                    self.fs_fuse_options[key] = value
