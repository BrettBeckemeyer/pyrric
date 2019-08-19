"""Configuration window for Background Toggle."""
__author__ = 'Brett Beckemeyer (bbeckemeyer@cannondesign.com)'
import os
import os.path as op

from pyrevit import forms
from pyrevit import script
from pyrevit import coreutils
from pyrevit import HOST_APP
from pyrevit.coreutils import envvars


class ToggleBG(forms.WPFWindow):
    def __init__(self, xaml_file_name):
        forms.WPFWindow.__init__(self, xaml_file_name)

        self._config = script.get_config()

        self.selected_color_R.Text = \
            str(self._config.get_option('selected_color_R', default_value='255'))
        self.selected_color_G.Text = \
            str(self._config.get_option('selected_color_G', default_value='255'))
        self.selected_color_B.Text = \
            str(self._config.get_option('selected_color_B', default_value='255'))

        script.save_config()

    def cancel(self, sender, args):

        self.Close()

    def save_options(self, sender, args):
        self._config.selected_color_R = self.selected_color_R.Text
        self._config.selected_color_G = self.selected_color_G.Text
        self._config.selected_color_B = self.selected_color_B.Text

        script.save_config()
        self.Close()

ToggleBG('ToggleBG.xaml').ShowDialog()



