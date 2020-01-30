import numpy as np

from lsdo_utils.api import OptionsDictionary


class Powertrain(OptionsDictionary):

    def initialize(self):
        self.modules = []
        self.links = []

    def add_module(self, module):
        self.modules.append(module)

    def add_link(self, src_name, src_var_names, tgt_name, tgt_var_names):
        if isinstance(src_var_names, str):
            src_var_names = [src_var_names]
        if isinstance(tgt_var_names, str):
            tgt_var_names = [tgt_var_names]

        self.links.append((src_name, src_var_names, tgt_name, tgt_var_names))