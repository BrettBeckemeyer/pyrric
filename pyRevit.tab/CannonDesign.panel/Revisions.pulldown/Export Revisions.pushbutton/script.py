# -*- coding: utf-8 -*-
"""Exports Revision Cloud information to external CSV file"""
"""Updated 2018-11-29 to adapt to version 4.6"""
"""Updated 2019-01-08 to fix sheet prefix extraction"""
"""Updated 2019-02-01 to replace deprecated get_project_info"""
"""Updated 2019-03-05 to add pyrevit version checks"""
"""Updated 2019-03-08 to add unicode codec processing"""
"""Updated 2019-05-17 to catch odd Sheet Numbers"""
"""Updated 2019-06-25 to process BIM360 models"""
"""Updated 2019-06-27 to correct BIM360 active model name and added debugging output"""
"""Updated 2019-08-28 to add else to handle no links selected or cancelling dialog"""
__author__ = 'Brett Beckemeyer (bbeckemeyer@cannondesign.com)'

from pyrevit import coreutils
# 2019/03/08: Added codecs for Unicode
#from pyrevit.coreutils import os, re, shutil, codecs
import os, re, shutil, codecs
from pyrevit import revit, DB
from pyrevit.revit import query, sys
from pyrevit import script
from pyrevit import forms
import csv
from pyrevit import versionmgr



# SET DEBUGG TO TRUE FOR VERBOSE LOGGING IN CONSOLE WINDOW
debugg = False
# SET DEBUGG_OUTPUT TO FALSE TO STOP OUTPUT FOR TESTING
debugg_output = True

#2019/03/08: modified to use coreutils timer module
timer = coreutils.Timer()
#logger = script.get_logger()
# ...

#----------BASIC VARIABLE DEFINITIONS--------

# Note: at some point it would be good to add variable TYPE to variable names...
sht_placeholder = "ZZ"
rev_count = 0
sheets_count = 0
rev_count_total = 0
sheets_count_total = 0
worksharing = False
FileError = 0

# LINKED MODEL variables
lnks = [] # FEC of linked model RevitLinkInstances
ext_refs = [] # FEC of ExternalFileReferenceType.RevitLink
er_names = [] # names of selected linked models
lnkinst = [] # instances of selected linked models
lnkdocs = [] # documents of selected linked models
lnk_errors = [] # container for errors related to linked models
refcount = 0 # count of linked references
selected_extrefs = [] # holding of linked models selected from dialog

# SHEETS variables
all_sheets = [] # container to hold all sheets collected from all models
sheetsnotsorted = []
sheets_filename = []
revs_filename = []
docsheets = [] # container to hold sheets from active model

# CLOUDS variables
all_clouds = []
docclouds = []

# ITERATION variables for link processing
doclnkpath = ""
lnkfolder = ""
lnkfile = ""
isheets = []
iclouds = []
irevisions = []

# ITERATION variables for sheet processing
volx = ""
shtitem = ""
restN = ""
sheet_disc = ""
prefix = ""

# Sets variables for export filenames
backup_extension = "bak"
filename_extension = "csv"
filename_revclouds = "x_revclouds"
filename_sheets = "x_sheets"
filename_manual = "man"

# EXPORT variables
sheet_table = []
table_revclouds = []
blank = "00"
rev_cloud_sheets = []
qty = 0
addlrevs = []
revised_sheets = []
rev_sheets_file = []

""" ITERATION variables for tables
r = ''
rev = ''
revdes = ''
revdate = ''
reason = ''
rID = ''
viewno = ''
comment = ''
viewname = ''
shtnum = ''
viewname = ''
shtfile = ""
thisdoc = ""
"""

#-----------END VARIABLE DEFINITIONS----------


# 2019/03/05: Added pyrevit version checks
#-----------GET PYREVIT VERSION----------------
pyrvt_ver = versionmgr.get_pyrevit_version()
short_version = \
      '{}'.format(pyrvt_ver.get_formatted(nopatch=True))
vv = short_version.split(".")
pyrvt_ver_main = int(vv[0])
pyrvt_ver_min = int(vv[1])


#-----------GET CONFIG DATA--------------------

my_config = script.get_config()
process_links = my_config.get_option('process_links', default_value=True)
sheets_process_placeholder = my_config.get_option('process_placeholders', default_value=True)
prefix_numchars = str(my_config.get_option('prefix_numchars', default_value='2'))
sheetdisc_param = my_config.get_option('sheetdisc_param', default_value='Sheet Discipline Number')
process_sheetdisc = my_config.get_option('process_sheetdisc', default_value=True)
sheetfilter_exclude = my_config.get_option('filter_exclude', default_value=False)
sheetfilter_include = my_config.get_option('filter_include', default_value=True)
sheetfilter_param = my_config.get_option('sheetfilter_param', default_value='Volume Number')
# 2019-06-18: removed default value for sheetfilter so empty value does not get filtered
sheetfilter = my_config.get_option('sheetfilter', default_value='')
process_manual = my_config.get_option('process_man', default_value=True)

# check if sheetfilter is empty, then set to ZZ placeholder value
if not (sheetfilter and sheetfilter.strip()):
	sheetfilter = sht_placeholder

export_folder = my_config.get_option('exportfolder', default_value='Export_dynamo')

# sheetfilter_type to 1 for include, 0 for exclude
if sheetfilter_include:
	sheetfilter_type = 1
else:
	sheetfilter_type = 0

#--------------END CONFIG---------------------------


#----------CONSOLE WINDOW AND ELEMENT STYLES--------

console = script.get_output()
console.set_height(480)
console.lock_size()


report_title = 'Revision Export'
report_date = coreutils.current_date()
# 2/1/2019: added query method to replace deprecated revit.get_project_info()
try:
	report_project = revit.query.get_project_info().name
except:
	report_project = revit.get_project_info().name

# setup element styling
console.add_style(
    'table { border-collapse: collapse; width:100% }'
    'table, th, td { border-bottom: 1px solid #aaa; padding: 5px;}'
    'th { background-color: #545454; color: white; }'
    'tr:nth-child(odd) {background-color: #f2f2f2}'
    )

#--------END CONSOLE AND STYLES-----------------------

#--------CHECK FOR BIM360 MODEL-----------------------
# 2019-06-24: Added check for BIM360 models
filter = "BIM 360:"
if filter in revit.doc.PathName:
	BIMCloud = True
	if debugg: print("DEBUG: This is a cloud-based model!")
	(discard, docfile) = os.path.split(revit.doc.PathName)
	if debugg: print("DEBUG: docfile is: " + docfile)
else:
	BIMCloud = False
#-----------------------------------------------------


#-----RETURN DOCUMENT FOLDER AND FILENAME-------------

# Get full path of current document
# 2019-06-24: changed path finding to use pyrevit built-in tools
if forms.check_workshared(doc=revit.doc):
	if debugg: print("DEBUG: Worksharing is enabled")
	worksharing = True
	if not BIMCloud:
		try:
			docpath = revit.query.get_central_path(doc=revit.doc)
		except:
			docpath = DB.ModelPathUtils.ConvertModelPathToUserVisiblePath(revit.doc.GetWorksharingCentralModelPath())
else:
	worksharing = False
	if debugg: print("DEBUG: Worksharing is not enabled")
if BIMCloud:
	try: 
		# 2019-06-25: Attempts to read "Project Folder" global parameter value and use it for docfolder
		proj_folder_param = revit.doc.GetElement(DB.GlobalParametersManager.FindByName(revit.doc, "Project Folder"))
		proj_folder = proj_folder_param.GetValue().Value
		path_add = 'E_WORKING\\E.01 Design\\E.01.1 BIM\\Current Model'
		docpath = os.path.join(proj_folder, path_add, docfile)
	except:
		# 2019-06-25: if no global parameter "Project Folder" exists, use C:\Temp for output
		docpath = 'c:\\Temp\\blank.txt'
if not docpath:
	docpath = revit.doc.PathName

# Split file path
(docfolder, docfile) = os.path.split(docpath)
if debugg: print("docfolder: " + docfolder)
#------------------------------------------------------


#------BEGIN DICTIONARY OF LINK NAME, DOC--------------

#---structure to be: Linkname:Linkdoc for each file
lnk_data = {}
lnk_data[docfile] = revit.doc
#---next step is to append each linked model to list

#------------------------------------------------------


#------DEFINE BLANK AND EMPTY--------------------------	
class BlankObj:
	def __repr__(self):
		return ""

blank = BlankObj()
empty = "$"
#------------------------------------------------------

#-------PROCESS LINKS AND FILL DICTIONARY--------------
# 2019-06-24: added check for BIM360
if process_links and worksharing:
	#------GET REVIT LINKS AS INSTANCES----------------
	try:
		lnks = DB.FilteredElementCollector(revit.doc).OfClass(DB.RevitLinkInstance)
		#ext_refs = query.get_links(DB.ExternalFileReferenceType.RevitLink)
		# 2019-06-24: if model is cloud-based, set ext_refs to empty
		if not BIMCloud:
			ext_refs = query.get_links(DB.ExternalFileReferenceType.RevitLink)
		else:
			ext_refs = []
		if debugg:
			print("ext_refs: " )
			print(ext_refs)
	except:
		worksharing = False
		print("No linked models to process.")
		console.insert_divider()
	
	if lnks and worksharing:
		refcount = len(ext_refs)
		
#2019-03-06: Fixed refcount for greater than 0, instead of 1 and deleted refcount == 1
#2019-06-24: Empty ext_refs (resulting from cloud-based model) keeps the dialog boxes from appearing
		if refcount > 0:
#2018-11-29: Added try/except to catch new 4.6 terminology
#2019/03/05: Added pyrevit version checks
			if (pyrvt_ver_main >= 5) or ((pyrvt_ver_main == 4) and (pyrvt_ver_min >= 5)):
				selected_extrefs = \
					forms.SelectFromList.show(
						ext_refs,
						title='Select Links to Include',
						width=500,
						button_name='OK',
						multiselect=True
						)
			else:
				selected_extrefs = \
					forms.SelectFromCheckBoxes.show(
						ext_refs,
						title='Select Links to Include',
						width=500,
						button_name='OK',
						checked_only=True
						)
		if selected_extrefs:
			#------DIALOG BOX TO RELOAD LINKS------------
			res = forms.alert('Reload Revit links?',
							yes=True, no=True, ok=False)
			for extref in selected_extrefs:
				er_names.append(extref.name)
				if res:
					try:
						ext_error = False
						extref.reload()
					except:
						ext_error = True
					if ext_error:
						res2 = forms.alert('Link(s) cannot be reloaded. To reload these links, close other models that contain the links. \nDo you wish to continue without reloading?', yes=True, no=True, ok=False)
						if not res2:
							console.close()
							sys.exit()
# 2019-08-28 Added else to handle no links selected or cancelling dialog
		else:
			#------DIALOG BOX TO EXPORT SINGLE MODEL------------
			res = forms.alert('No linked models selected, export from active model only?',
							yes=True, no=True, ok=False)
			if not res:
				console.close()
				sys.exit()
		# 2019-06-24: if cloud-based model, include all links (since dialog boxes do not work)
		if BIMCloud:
			for lnk in lnks:
				nm = lnk.Name.split(":")[0].strip()
				er_names.append(nm)
		
		#------GET LINK DOCS, CHECK IF LOADED----------
		# 2019-06-24: Added yes/no to dialog
		# 2019-06-24: Addition of BIMCloud here forces all links to be processed for cloud-based models
		if selected_extrefs or BIMCloud: 
			for lnk in lnks:
				nm = lnk.Name.split(":")[0].strip()
				if debugg: print("DEBUG: link name: " + nm)
				if nm in er_names:
					ddoc = lnk.GetLinkDocument()
					if not ddoc:
						lnk_errors.append(nm + ", ")
					else:
						lnkinst.append(lnk)
						lnkdocs.append(ddoc)
			if len(lnk_errors) > 0:
				rel = forms.alert('Link(s) unloaded: ' + str(lnk_errors) + '.\n\nDo you want to continue without processing these links?', ok=False, no=True, yes=True)
				if not rel:
					console.close()
					sys.exit()
		else:
			selected_extrefs = []
			lnks = []
			process_links = False


#-------EXTRACT ELEMENTS FROM ACTIVE MODEL---------------
print("Collecting elements from active model...")

# Extract sheets from DOCUMENT
docsheets = DB.FilteredElementCollector(revit.doc)\
                    .OfCategory(DB.BuiltInCategory.OST_Sheets)\
                    .WhereElementIsNotElementType()\
                    .ToElements()
if docsheets:
	try:
		sheets_count = len(docsheets)
	except: len([ docsheets ])
	for i in range(sheets_count):
		sheets_filename.append(docfile)
	all_sheets.extend(docsheets)
	if debugg: print("DEBUG: sheets extracted")
	print(str(sheets_count) + " sheets extracted")
	sheets_count_total = sheets_count
	sheets_count = 0
else:
	print("\nNo sheets in active model")


# collect clouds from DOCUMENT
docclouds = DB.FilteredElementCollector(revit.doc)\
               .OfCategory(DB.BuiltInCategory.OST_RevisionClouds)\
               .WhereElementIsNotElementType()\
               .ToElements()

if docclouds:
	try:
		rev_count = len(docclouds)
	except: len([ docclouds ])
	all_clouds.extend(docclouds)
	for i in range(rev_count):
		revs_filename.append(docfile)
	if debugg: print("DEBUG: revclouds extracted")
	print(str(rev_count) + " revclouds extracted")
	rev_count_total = rev_count
	rev_count = 0
else:
	print("\nNo revclouds in active model")

 
# collect revisions from DOCUMENT
all_revisions = []

docrevs = DB.FilteredElementCollector(revit.doc)\
                  .OfCategory(DB.BuiltInCategory.OST_Revisions)\
                  .WhereElementIsNotElementType()\
                  .ToElements()
if docrevs:
	all_revisions.extend(docrevs)

print("...done.")
console.insert_divider()
#--------------------------------------------------------
if debugg: print(worksharing)
if process_links and worksharing:
	#-------COLLECT ELEMENTS FROM LINKED MODELS--------------
	print("\nCollecting elements from linked models...")

	# ITERATE THROUGH LINKS AND GATHER ELEMENTS
	for index, doclnk in enumerate(lnkdocs):
		doclnkpath = ""
		lnkfolder = ""
		lnkfile = ""
		# Get full path of current document
		if not BIMCloud:
			doclnkpath = DB.ModelPathUtils.ConvertModelPathToUserVisiblePath(doclnk.GetWorksharingCentralModelPath())
		else:
			doclnkpath = doclnk.PathName
		# Split file path
		(lnkfolder, lnkfile) = os.path.split(doclnkpath)
		
		# Add to the link data array
		lnk_data[lnkfile] = doclnk
			
		try:
			isheets = DB.FilteredElementCollector(doclnk).OfCategory(DB.BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().ToElements()
			iclouds = DB.FilteredElementCollector(doclnk).OfCategory(DB.BuiltInCategory.OST_RevisionClouds).WhereElementIsNotElementType().ToElements()
			irevisions = DB.FilteredElementCollector(doclnk).OfCategory(DB.BuiltInCategory.OST_Revisions).WhereElementIsNotElementType().ToElements()
		except:
			isheets = []
			iclouds = []
			irevisions = []
		
		if isheets:
			try:
				sheets_count = len(isheets)
			except: 
				sheets_count = len([ isheets ])
			all_sheets.extend(isheets)
			for s in range(sheets_count):
				sheets_filename.append(lnkfile)
		if iclouds:
			try:
				rev_count = len(iclouds)
			except: 
				rev_count = len([ iclouds ])
			all_clouds.extend(iclouds)
			for i in range(rev_count):
				revs_filename.append(lnkfile)
		if irevisions:
			all_revisions.extend(irevisions)
		
	#	sheetsnotsorted.extend(isheets)
		print(lnkfile + " processed with:" + str(sheets_count) + ' sheets, and ' + str(rev_count) + ' revisions.')
		sheets_count_total = sheets_count_total + sheets_count
		rev_count_total = rev_count_total + rev_count
		links_running = index+1
	print(str(links_running) + " Total links processed.")
	console.insert_divider()
	#-------------------------------------------------------
else:
	print("LINKS NOT PROCESSED!")
	print("Check that links are loaded and link worksets are loaded / enabled.")
	console.insert_divider()

#SORT FOR SHEETS - REMOVED BECAUSE BREAKS FILENAME RETRIEVAL
# all_sheets = sorted(sheetsnotsorted, key=lambda x: x.SheetNumber)

def unicode_to_ascii(data):
	if isinstance(data, unicode):
		data_encoded = data.encode('utf-8')
		data_cleaned = re.sub(r'[^\x00-\x7f]',r'',data_encoded)
		return data_cleaned.encode("ascii")
	else:
		return data

class RevisedSheet:
    def __init__(self, rvt_sheet):
        self._rvt_sheet = rvt_sheet
        self._find_all_clouds()
        self._find_all_revisions()

    def _find_all_clouds(self):
        ownerview_ids = [self._rvt_sheet.Id]
        ownerview_ids.extend(self._rvt_sheet.GetAllViewports())
        self._clouds = []
        for rev_cloud in all_clouds:
            if rev_cloud.OwnerViewId in ownerview_ids:
                self._clouds.append(rev_cloud)

    def _find_all_revisions(self):
        self._revisions = set([cloud.RevisionId for cloud in self._clouds])
        #self._addl_rev_ids = []
        self._addl_rev_ids = self._rvt_sheet.GetAdditionalRevisionIds()
        #print str(len(self._addl_rev_ids))

    @property
    def sheet_number(self):
        return self._rvt_sheet.SheetNumber

    @property
    def sheet_name(self):
        return self._rvt_sheet.Name

    @property
    def cloud_count(self):
        return len(self._clouds)

    @property
    def rev_count(self):
        return len(self._revisions)

    def get_clouds(self):
        return self._clouds

    def get_comments(self):
        all_comments = set()
        for cloud in self._clouds:
            comment = cloud.LookupParameter('Comments').AsString()
            if not coreutils.is_blank(comment):
                all_comments.add(comment)
        return all_comments

    def get_marks(self):
        all_marks = set()
        for cloud in self._clouds:
            mark = cloud.LookupParameter('Mark').AsString()
            if not coreutils.is_blank(mark):
                all_marks.add(mark)
        return all_marks

    def get_param(el, par):
        val = el.LookupParameter(par).AsString()
        return val

    def get_addl_revs(self):
        return self._addl_rev_ids

# REMOVED THIS DEFINITION BECAUSE BREAKS IF NUMBERING IS BY SHEET
#   def get_revision_numbers(self):
#       return self._rev_numbers


#-------CREATE EXPORT TABLE FOR SHEETS-----------

print("\nAssembling Sheets table for export...")

# create sheet table structure
sheet_table.append(["Sheet Number","Sheet Name","Volume","Prefix","Sequence","Sheet Discipline"])
# script-wide parameters for sheets

try:
	numchars = int(prefix_numchars)
except:
	numchars = 2
replacement = ''

# set parameter defaults prior to iteration
sheet_process = True

# iterate over all sheets
for index, sheet in enumerate(all_sheets):
	# if config option to process placeholder sheets selected, then set sheet_process param on all sheets regardless
	if sheets_process_placeholder:
		sheet_process = True
	# otherwise, check to see if sheet can be printed (not placeholder)
	else:
		sheet_process = sheet.CanBePrinted
	
	if sheet_process:
		# reset parameters
		volx = ""
		shtitem = ""
		restN = ""
		sheet_disc = ""
		prefix = ""
		
		try:
			# get the value of the parameter used for volume definition
			sheetfilter_value = sheet.LookupParameter(sheetfilter_param).AsString()
			# if this parameter is not empty, set volume number to this value
			if sheetfilter_value <> None:
				volx = sheetfilter_value
			# otherwise, if the parameter is empty, set sheetfilter_value to match placeholder and keep volx blank
			else:
				sheetfilter_value = sht_placeholder
		# if parameter itself does not exist, allow user to ignore filtering or exit
		except:
			#no_filter_param = forms.alert('Sheet parameter asked to filter by does not exist. Do you wish to ignore filter?', yes=True, no=False)
			#if no_filter_param:
			sheetfilter = sht_placeholder
			#else:
				#console.close()
				#sys.exit()
		
		# if sheetfilter value is set to placeholder (meaning blank), then set sheetfilter_value to placeholder as well (no filtering)
		if sheetfilter == sht_placeholder:
			sheetfilter_value = sht_placeholder
		
		# checks filter and filter type to determine whether to process or not
		if ((sheetfilter in sheetfilter_value) and (sheetfilter_type == 1)) or ((sheetfilter not in sheetfilter_value) and (sheetfilter_type == 0)):
			shtitem = sheet.get_Parameter(DB.BuiltInParameter.SHEET_NUMBER).AsString()
			shtitem = unicode_to_ascii(shtitem)
			# extract alpha characters from left of sheet number, if exist, as prefix - remainder set as restN
			try:
				restN = re.sub('[^0-9]','', shtitem[:numchars]) + shtitem[numchars:]
				prefix = re.sub('[^A-Z]','', shtitem[:numchars])
			except:
				restN = shtitem
				prefix = ""
			
			# check if first character of restN is not alphanumeric, if so strip it out
			# 17-05-2019: added trap to catch empty restN
			try:
				if not (restN[0].isalpha() or restN[0].isdigit()):
					restN = restN[1:]
					#if debugg: print(restN[1:] + " updated")
			except:
				continue
			if process_sheetdisc:
				try:
					sheet_disc = sheet.LookupParameter(sheetdisc_param).AsString()
				except:
					sheet_disc = sheet_disc
			
			sheet_table.append([shtitem,sheet.Name,volx,prefix,restN,sheet_disc])
			#revised_sheets.append(RevisedSheet(sheet))
			revised_sheets.append(sheet)
			rev_sheets_file.append(sheets_filename[index])

#		revised_sheets.append(RevisedSheet(sheet))
print("...done.")
#-------------------------------------------------

#-------DEBUG TABLE---------------------------------
if debugg:
	nosheetsno = False
	if len(sheet_table) > 500:
		sheetsno = forms.alert('Greater than 500 sheets, display results?', yes=True, no=True, ok=False)
	else:
		nosheetsno = True
	if sheetsno or nosheetsno: 
		print('\nDEBUG: Sheets Table')
		for row in sheet_table:
			print('DEBUG: ' + str(row))


console.insert_divider()

#------ASSEMBLE TABLE OF REVISIONS FOR EXPORT-----
print("\nAssembling Revision Clouds table for export...")

table_revclouds.append(["Sheet Number","Sheet Qty","Filename","Element ID","View Name","Reason Code","ID","View Number","Comment","Revision Description","Revision Date"])

if debugg: print('DEBUG: \nRevisions manually assigned to sheets:')
#	Iterate through all sheets and get manually placed revisions
if process_manual:
	for index, rev_sheet in enumerate(revised_sheets):
		shtnum = unicode_to_ascii(rev_sheet.SheetNumber)
		#shtnum = unicode_to_ascii(rev_sheet.sheet_number)
		shtfile = rev_sheets_file[index]
		
		#for shtfile, d in lnk_data.items():
			#thisdoc = d
		thisdoc = lnk_data.get(shtfile, "")
		
		# Get manually placed Revisions and iterate through
		try:
			#addlrevs = rev_sheet.get_addl_revs()
			addlrevs = rev_sheet.GetAdditionalRevisionIds()
			if debugg and addlrevs: print('DEBUG: ' + shtnum + ' additional revisions found')
			for x in addlrevs:
				r = thisdoc.GetElement(x)
				rev = rev_sheet.Id.ToString()
				revdes = r.Description
				revdate = r.RevisionDate
				reason = "00"
				rID = "00"
				viewno = ''
				comment = ''
				viewname = shtnum + " - " + rev_sheet.Name
				table_revclouds.append([shtnum, qty, shtfile, rev, viewname, reason, rID, viewno, comment, revdes, revdate])
		except:
			#if debugg: print("no additional revision")
			print("No additional revision")


console.insert_divider()

for index, rc in enumerate(all_clouds):
	rev = rc.Id.ToString()
	shtnum = ''
	viewname = ''
	shtfile = revs_filename[index]
	
	thisdoc = lnk_data.get(shtfile, "")
	
	if rev not in rev_cloud_sheets:
	#if True:
		reason = ''
		rID = ''
		qty = 0
		view = thisdoc.GetElement(rc.OwnerViewId)
		if view:
			viewz = []
			viewname = view.ViewName
			viewz.extend(rc.GetSheetIds())
			qty = len(viewz)
			if qty == 1:
				sheetview = thisdoc.GetElement(viewz[0])
				shtnum = sheetview.get_Parameter(DB.BuiltInParameter.SHEET_NUMBER).AsString()
				shtnum = unicode_to_ascii(shtnum)
				#if debugg: print 'Revclouds found not through sheet collector: ' + shtnum
#			for index2, v in enumerate(viewz):
#				if index2 == 0:
#					#print v
#					sheetview = thisdoc.GetElement(v)
#					shtnum = sheetview.SheetNumber
#					#console.insert_divider()
#				else:
#					next
			viewz = []
		else:
			viewname = ''
			shtnum = ''

		mark = rc.LookupParameter('Mark').AsString()
		
		#	Mark extraction to reason & ID
		if mark:
			if '.' in mark or ':' in mark:
				temp = mark.replace(":", ".").split(".")
				reason = temp[0].rjust(2,'0')
				rID = reason + "." + (temp[1].rjust(2,'0'))
			else:
				reason = mark
				rID = reason + "." + "00"
		#	End Mark extraction

		comments = rc.LookupParameter('Comments').AsString()

		#	Comments extraction to viewno, comment		
		#	if comment exists (not empty)
		if comments:
		#	if comments has colon or vertical separator
			if '|' in comments[:9] or ':' in comments[:9]:
				temp1 = comments[:9].replace(":", "|")
				temp2 = comments[9:]
		#	if comments has period
			else:
				if '.' in comments[:9]:
					temp1 = comments[:9].replace(".", "|")
					temp2 = comments[9:]
		#	if comments is blank (empty)
				else:
					temp1 = '-' + '|'
					temp2 = comments
			temp = (temp1 + temp2).split("|")
			viewno = temp[0]
			comment = temp[1].strip()
		else:
			viewno = '-'
			comment = ''
		#	End Comments extraction

		revdes = rc.LookupParameter('Revision Description').AsString()
		revdate = rc.LookupParameter('Revision Date').AsString()
		
		table_revclouds.append([shtnum, qty, shtfile, rev, viewname, reason, rID, viewno, comment, revdes, revdate])

#-------DEBUG TABLE---------------------------------
if debugg:
	norevcloudsno = False
	revclouds_len = len(table_revclouds)
	if revclouds_len > 1000:
		revcloudsno = forms.alert('Greater than 1000 revclouds, display results?', yes=True, no=True, ok=False)
	else:
		norevcloudsno = True
	if revcloudsno or norevcloudsno:
		print('DEBUG: Revclouds Export table:')
		for row in table_revclouds:
			print('DEBUG: ' + row)

#-------ZERO OUT LISTS------------------------------
all_sheets = []
all_clouds = []
all_revisions = []
sheetsnotsorted = []
sheets_filename = []
revs_filename = []
rev_cloud_sheets = []
addlrevs = []
revised_sheets = []
rev_sheets_file = []
all_marks = []
all_comments = []
#----------------------------------------------------

#-------FILE WRITING---------------------------------
# Create export paths
# 2019.03.05: Below used to add filename if no linked files selected
#if not process_links:
#	filename_revclouds = filename_revclouds + "_" + docfile
#	filename_sheets = filename_sheets + "_" + docfile
export_revclouds = os.path.join(docfolder, export_folder, (filename_revclouds + "." + filename_extension))
export_sheets = os.path.join(docfolder, export_folder, (filename_sheets + "." + filename_extension))

# Check if export folder exists and make it if not
directory = os.path.join(docfolder,export_folder)
try:
	if not os.path.exists(directory):
		os.makedirs(directory)
except: #handle other exceptions
	#console.close()
	FileError = 1
	print("\nUnexpected error creating directory: ", directory)
	#sys.exit()

# 2019-06-27: Added check for debugg_output to stop output sequence for testing
if debugg_output:
	# Check if file exists and make copy
	if os.path.isfile(export_revclouds):
		print("\nRevision Cloud export file found...")
		shutil.copy(export_revclouds, os.path.join(docfolder, export_folder, (filename_revclouds + "." + backup_extension)))
		print("...backed up file.")
	else:
		print "\nRevision Cloud export file not found, new file will be created."

	# Write CSV output for Revision Clouds
	# 2019/03/08: Added codecs for Unicode
	try:
		with codecs.open(export_revclouds, 'w+', encoding='utf-8') as f:
			print("\nWriting Revision Cloud export to: ")
			print(export_revclouds)
			writer = csv.writer(f, lineterminator='\n')
			writer.writerows(table_revclouds)
			print("...done.")
	except IOError as e:
		#console.close()
		print("I/O error({0}): {1}".format(e.errno, e.strerror))
		FileError = 1
		#sys.exit()
	except: #handle other exceptions
		#console.close()
		print("\nUnexpected error writing to Revision Cloud export file: ", sys.exc_info()[0])
		FileError = 1
		#sys.exit()

	console.insert_divider()

	# Check if file exists and make copy
	if os.path.isfile(export_sheets):
		print("\nSheets export file found...")
		shutil.copy(export_sheets, os.path.join(docfolder, export_folder, (filename_sheets + "." + backup_extension)))
		print("...backed up file.")
	else:
		print("Sheets export file not found, new file will be created.")

	# Write CSV output for Sheets
	# 2019/03/08: Added codecs for Unicode
	try:
		with codecs.open(export_sheets, 'w+', encoding='utf-8') as f:
			print("\nWriting Sheets export...")
			print(export_sheets)
			writer = csv.writer(f, lineterminator='\n')
			writer.writerows(sheet_table)
			print("...done.")
	except IOError as e:
		#console.close()
		print("I/O error({0}): {1}".format(e.errno, e.strerror))
		FileError = 1
		#sys.exit()
	except: #handle other exceptions
		#console.close()
		print("\nUnexpected error writing to Sheets export file: ", sys.exc_info()[0])
		FileError = 1
		#sys.exit()
else:
	a = "a"

# Zero out tables
table_revclouds = []
sheet_table = []


console.insert_divider()
console.hide()
console.show()
#------------------------------------------------

#--------PRINT SUMMARY---------------------------
print(str(sheets_count_total) + " sheets exported")
print(str(rev_count_total) + " revclouds exported")
print(" ")

#2019/03/08: modified to use coreutils timer module
end = timer.get_time()
m, s = divmod(end, 60)
h, m = divmod(m, 60)

print("Elapsed time: %d:%02d:%02d" % (h, m, s))

if FileError == 1:
	print "\nEXPORT NOT COMPLETED!"
	print "\nProblem(s) creating or updating files or folders"
else:
	if not debugg_output:
		print "\nDEBUG: EXPORT NOT COMPLETED!"
		print "\nDEBUG: Set debugg_output to True"
	else:
		print "\nExport complete, this window may be closed."