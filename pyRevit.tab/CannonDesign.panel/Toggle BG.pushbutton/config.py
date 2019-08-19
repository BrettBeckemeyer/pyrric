"""Configuration window for Background Toggle."""
__author__ = 'Brett Beckemeyer (bbeckemeyer@cannondesign.com)'
import os
import os.path as op
#import Tkinter

from pyrevit import forms
from pyrevit import script
from pyrevit import coreutils
from pyrevit import HOST_APP
from pyrevit.coreutils import envvars

#from pyrevit import Tkinter
#from Tkinter import *
#from tkColorChooser import askcolor



"""class getColor():
    def __init__(self):
        #color = askcolor()[0]
        color = forms.select_swatch.show(title="Select alternate background color")

        self._config = script.get_config()

        self.selected_color = self._config.get_option('selected_color', default_value=(255,255,255))

        script.save_config()

    def cancel(self, sender, args):

        self.Close()

    def save_options(self, sender, args):
        self._config.selected_color = color

        script.save_config()
        self.Close()
"""
color = forms.select_swatch(title="Select alternate background color")

if not (color is None):
	_config = script.get_config()
	_config.selected_color = color
	script.save_config()

