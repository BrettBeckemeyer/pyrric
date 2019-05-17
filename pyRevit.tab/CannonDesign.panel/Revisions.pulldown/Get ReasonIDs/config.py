"""Configuration window for Get ReasonIDs tool."""
__author__ = 'Brett Beckemeyer (bbeckemeyer@cannondesign.com)'
import os
import os.path as op

from pyrevit import forms
from pyrevit import script
from pyrevit import coreutils
from pyrevit import HOST_APP
from pyrevit.coreutils import envvars


class ConfigWindow(forms.WPFWindow):
    def __init__(self, xaml_file_name):
        forms.WPFWindow.__init__(self, xaml_file_name)

        self._config = script.get_config()

        self.rundialog.IsChecked = \
            self._config.get_option('dialog', default_value=True)

        script.save_config()

    def cancel(self, sender, args):

        self.Close()

    def save_options(self, sender, args):
        self._config.dialog = self.rundialog.IsChecked


        script.save_config()
        self.Close()

ConfigWindow('dialog.xaml').ShowDialog()
