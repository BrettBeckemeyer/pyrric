# -*- coding: utf-8 -*-
"""Displays the Project-specific Reason IDs from the Change Tracking File"""
__author__ = 'Brett Beckemeyer (bbeckemeyer@cannondesign.com)'

from pyrevit import coreutils
from pyrevit import revit, DB
from pyrevit.revit import query
from pyrevit import script
from pyrevit import forms
import os, shutil, csv, re, sys
from timeit import default_timer as timer
import operator # used for itemgetter for sorting
from pyrevit import HOST_APP

from collections import OrderedDict
#from collections import namedtuple
#from itertools import imap


debugg = False

rundialog = True

#start = timer()
#logger = script.get_logger()
# ...

#-----------GET CONFIG DATA-------------------------
my_config = script.get_config()
rundialog = my_config.get_option('dialog', default_value=True)
#---------------------------------------------------

#------CREATE CONSOLE WINDOW------------------------
if debugg or not rundialog:
    console = script.get_output()
    console.set_height(480)
    console.lock_size()
    
    report_title = 'Revision Cloud'
    report_date = coreutils.current_date()
    report_project = revit.query.get_project_info().name
    
# setup element styling
    console.add_style(
        'table { border-collapse: collapse; width:100% }'
        'table, th, td { border-bottom: 1px solid #aaa; padding: 5px;}'
        'th { background-color: #545454; color: white; }'
        'tr:nth-child(odd) {background-color: #f2f2f2}'
        )
#-----------------------------------------------------

class ReasonIDs:
    def __init__(self):
        if rundialog:
            Mark = self._dia_Mark()
#           CommentX = self._dia_Desc()
            if Mark:
                script.clipboard_copy(Mark)
            if debugg:
                    print("Mark: ")
                    print(Mark)
        else:
            reason_list = self._reason_list()
            reason_table_header = "| Reason Code        | Reason ID           | Description                         |\n" \
                                  "|:------------------:|:-------------------:|:------------------------------------|\n"
            reason_table_template = "|{code}|{id}|{desc}|\n"
            reason_table = reason_table_header
            for x in reason_list:
                reason_table += reason_table_template.format(code=x[0],
                                               id=x[1],
                                               desc=x[2])
            console.print_md(reason_table)


    def _dia_Mark(self):
        #-----DIALOG TO ASSIGN MARK (REASON ID)---------------
        AA = forms.SelectFromList.show(
              self._reason_list(),
              title='Reason ID',
              group_selector_title='Reason Code:',
              multiselect=False
        )
        if AA:
            BB = AA.split("-")[0]
        else:
            BB = ""
        return BB


#    def _dia_Desc(self):
#        #-----DIALOG TO ASSIGN DESCRIPTION--------------------
#        StringX = forms.ask_for_string(
#            default='type description here',
#            prompt='Description of Change',
#            title='Description'
#        )
#        return StringX

    def _get_doc_folder(self):
        #-----RETURN DOCUMENT FOLDER AND FILENAME-------------
        # Get full path of current document
        try:
            docpath = DB.ModelPathUtils.ConvertModelPathToUserVisiblePath(revit.doc.GetWorksharingCentralModelPath())
        except:
            docpath = revit.doc.PathName

        # Split file path
        (docfolder, docfile) = os.path.split(docpath)
        #------------------------------------------------------

        if debugg: print(docfolder)

        return docfolder

    def _get_file_table(self):
        export_folder = "Export_dynamo"
        filename_reasons = "x_reasons"
        filename_extension = "csv"
        backup_extension = "bak"

        # Check if export folder exists and make it if not
        docfolder = self._get_doc_folder()
        directory = os.path.join(docfolder,export_folder)
        if not os.path.exists(directory):
            os.makedirs(directory)

        reasons_file = os.path.join(docfolder, export_folder, (filename_reasons + "." + filename_extension))

        # Check if file exists and make copy
        if os.path.isfile(reasons_file):
            if debugg: print "\nReasons file found..."
            reasons_file_copy = os.path.join(docfolder, export_folder, (filename_reasons + "_" + HOST_APP.username + "." + backup_extension))
            shutil.copy(reasons_file, reasons_file_copy)
            if debugg: print "...backed up file."
        else:
            print "Reasons export file not found."
            sys.exit()

        return reasons_file_copy

    def _reason_list(self):
        reasons_file_copy = self._get_file_table()

        with open(reasons_file_copy, 'r') as csvfile:
            dialect = csv.Sniffer().sniff(csvfile.read(1024))
            csvfile.seek(0)
            reader = csv.reader(csvfile, dialect)
            lines = list(reader)
            if debugg:
                print("lines:")
                print(lines)
            # filter out zz99 (first line), change to 'zz.99' to filter out 2-digit codes
            # lines2 = [x for x in lines if not 'zz.99' in x]
            filters_exclude = ["'zz.99","'zz99"]
            lines2 = []
            for x in lines:
                if any(item in filters_exclude for item in x):
                    continue
                lines2.append(x)
            if debugg:
                print("lines2:")
                print(lines2)
            # get list of categories (cat_list) and quantity (cat_count) from filtered list
            cat_list_long = []
            for l in lines2:
                cat_list_long.append(l[4])
            cat_list = list(set(cat_list_long))
            cat_list.sort()
            cat_count = len(cat_list)
            if debugg:
                print(cat_list)
                print("Quantity: " + str(cat_count))
            # create blank dictionary and populate the dictionary
            unordered_dict = {}
            table_output = []
            for index, c in enumerate(cat_list):
                mini_list = []
                #grouped_list.append(c)
                listx = [y for y in lines2 if c in y]
                #listx.sort()
                for item in listx:
                    mini_list.append(item[3] + "-" + item[5])
                    table_output.append([item[4],item[3],item[5]])
                unordered_dict.update({c:mini_list})
            # sorting of dictionary begins below
            if rundialog:
                output = OrderedDict(sorted(unordered_dict.items(), key=lambda t: t[0]))
            else:
                output = table_output
            if debugg: print(output)
        return output
 

ReasonIDs()
