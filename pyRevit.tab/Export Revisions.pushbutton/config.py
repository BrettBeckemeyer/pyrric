"""Configuration window for Export Revisions tool."""
__author__ = 'Brett Beckemeyer (bbeckemeyer@cannondesign.com)'
import os
import os.path as op

from pyrevit import forms
from pyrevit import script
from pyrevit import coreutils
from pyrevit import HOST_APP
from pyrevit.coreutils import envvars


class RevcloudConfigWindow(forms.WPFWindow):
    def __init__(self, xaml_file_name):
        forms.WPFWindow.__init__(self, xaml_file_name)

        self._config = script.get_config()

        self.proc_links.IsChecked = \
            self._config.get_option('process_links', default_value=True)

        self.proc_placeholders.IsChecked = \
            self._config.get_option('process_placeholders', default_value=True)

        self.prefix_numchars_tb.Text = \
            str(self._config.get_option('prefix_numchars', default_value='2'))

        self.sheetdiscparam_tb.Text = \
            self._config.get_option('sheetdisc_param', default_value='Sheet Discipline Number')

        self.proc_sheetdisc.IsChecked = \
            self._config.get_option('process_sheetdisc', default_value=True)

        self.sheetvolumefilterparam_tb.Text = \
            self._config.get_option('sheetfilter_param', default_value='Volume Number')

        self.sheetvolumefilter_tb.Text = \
            self._config.get_option('sheetfilter', default_value='')

        self.exportfolder_tb.Text = \
            self._config.get_option('exportfolder',
                                                default_value='Export_dynamo')

        self.filtertype_include_b.IsChecked = \
            self._config.get_option('filter_include',
                                                default_value=True)

        self.filtertype_exclude_b.IsChecked = \
            self._config.get_option('filter_exclude',
                                                default_value=False)

        self.proc_manual.IsChecked = \
            self._config.get_option('process_man', default_value=True)

        script.save_config()

    def cancel(self, sender, args):

        self.Close()

    def save_options(self, sender, args):
        self._config.process_links = self.proc_links.IsChecked
        self._config.process_placeholders = self.proc_placeholders.IsChecked
        self._config.process_sheetdisc = self.proc_sheetdisc.IsChecked
        self._config.sheetdisc_param = self.sheetdiscparam_tb.Text
        self._config.prefix_numchars = str(self.prefix_numchars_tb.Text)
        self._config.exportfolder = self.exportfolder_tb.Text
        self._config.sheetfilter = self.sheetvolumefilter_tb.Text
        self._config.sheetfilter_param = self.sheetvolumefilterparam_tb.Text
        self._config.filter_include = self.filtertype_include_b.IsChecked
        self._config.filter_exclude = self.filtertype_exclude_b.IsChecked
        self._config.process_man = self.proc_manual.IsChecked

        script.save_config()
        self.Close()

RevcloudConfigWindow('RevcloudWindow.xaml').ShowDialog()
