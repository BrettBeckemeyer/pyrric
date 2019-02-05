"""Configuration window for Increment Sheet Number tool."""
__author__ = 'Brett Beckemeyer (bbeckemeyer@cannondesign.com)'
import os
import os.path as op

from pyrevit import forms
from pyrevit import script
from pyrevit import coreutils
from pyrevit import HOST_APP
from pyrevit.coreutils import envvars


class SheetNoIncConfigWindow(forms.WPFWindow):
    def __init__(self, xaml_file_name):
        forms.WPFWindow.__init__(self, xaml_file_name)

        self._config = script.get_config()

        self.proc_alpha.IsChecked = \
            self._config.get_option('process_alpha', default_value=True)

        script.save_config()

    def cancel(self, sender, args):

        self.Close()

    def save_options(self, sender, args):
        self._config.process_alpha = self.proc_alpha.IsChecked


        script.save_config()
        self.Close()

SheetNoIncConfigWindow('Increment_Decrement_SheetNos.xaml').ShowDialog()
