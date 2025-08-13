from .core import GateLayout

try:
    import qcodes as qc
except ImportError as ie:
    raise ImportError('This module requires qcodes.') from ie


class QcodesGateLayout(GateLayout):
    def __init__(self, gate_to_parameter_mapping, layout_file=None, gate_names=None,
                 gate_mask=None, background_color='#ffffff', foreground_color='tab:gray',
                 cmap='hot', v_min=-2, v_max=0, explode_factor=0.1, fignum=998, text_kwargs=None,
                 offset=(0., 0.)):
        super().__init__(layout_file, gate_names, gate_mask, background_color, foreground_color,
                         cmap, v_min, v_max, explode_factor, fignum, text_kwargs, offset)

        class MaskedGate(qc.Parameter):
            def __init__(self, name, *args, **kwargs):
                super().__init__(name, *args, **kwargs)

            def get_raw(self):
                return 0

        self.gate_to_parameter_mapping = {
            gate: gate_to_parameter_mapping.get(gate, MaskedGate(gate))
            for gate in self.gate_names
        }
        self.gate_parameters = self.gate_to_parameter_mapping.values()

    def get_voltages(self, force: bool = False):
        for i, param in enumerate(self.gate_parameters):
            if force:
                self._latest_voltages[i] = param.get()
            else:
                self._latest_voltages[i] = param.cache.get()
