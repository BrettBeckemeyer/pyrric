# -*- coding: utf-8 -*-
"""Exports Area information to external CSV file"""

__author__ = 'Brett Beckemeyer (bbeckemeyer@cannondesign.com)'

from pyrevit import coreutils
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

#----------FUTURE FUNCTIONALITY--------
# In the future, a config dialog should be added to include a shared parameter
# Until that is functional, this parameter will contain the name of the shared
# parameter to include. If no parameter by that name exists, it is not included.
sp1_name = ''

#----------BASIC VARIABLE DEFINITIONS--------

# Note: at some point it would be good to add variable TYPE to variable names...
sht_placeholder = "ZZ"
rev_count = 0
areas_count = 0
rev_count_total = 0
areas_count_total = 0
worksharing = False
FileError = 0

export_folder = 'Export_dynamo'

# LINKED MODEL variables
lnks = [] # FEC of linked model RevitLinkInstances
links_running = 0
ext_refs = [] # FEC of ExternalFileReferenceType.RevitLink
er_names = [] # names of selected linked models
lnkinst = [] # instances of selected linked models
lnkdocs = [] # documents of selected linked models
lnk_errors = [] # container for errors related to linked models
refcount = 0 # count of linked references
selected_extrefs = [] # holding of linked models selected from dialog

# AREAS variables
all_areas = [] # container to hold all areas collected from all models
areassnotsorted = []
areas_filename = []
revs_filename = []
docareas = [] # container to hold areas from active model

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


# Sets variables for export filenames
backup_extension = "bak"
filename_extension = "csv"
filename_areas = "areas"

# EXPORT variables
area_table = []
blank = "00"
qty = 0


#-----------END VARIABLE DEFINITIONS----------


#-----------GET PYREVIT VERSION----------------
pyrvt_ver = versionmgr.get_pyrevit_version()
short_version = \
      '{}'.format(pyrvt_ver.get_formatted(nopatch=True))
vv = short_version.split(".")
pyrvt_ver_main = int(vv[0])
pyrvt_ver_min = int(vv[1])

#-----------DIALOG FOR SHARED PARAM------------
sp1_name = \
	forms.GetValueWindow.show(
		'hello',
		value_type = 'string',
		prompt='Shared Parameter Name: (leave blank for none)',
		default='',
		)


#----------CONSOLE WINDOW AND ELEMENT STYLES--------

console = script.get_output()
console.set_height(480)
console.lock_size()


report_title = 'Area Export'
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
		proj_folder_param = revit.doc.GetElement(DB.GlobalParametersManager.FindByName(revit.doc, "Project Folder"))
		proj_folder = proj_folder_param.GetValue().Value
		path_add = 'E_WORKING\\E.01 Design\\E.01.1 BIM\\Current Model'
		docpath = os.path.join(proj_folder, path_add, docfile)
	except:
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
if worksharing:
	#------GET REVIT LINKS AS INSTANCES----------------
	try:
		lnks = DB.FilteredElementCollector(revit.doc).OfClass(DB.RevitLinkInstance)
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
		
		if refcount > 0:
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
		if BIMCloud:
			for lnk in lnks:
				nm = lnk.Name.split(":")[0].strip()
				er_names.append(nm)
		
		#------GET LINK DOCS, CHECK IF LOADED----------
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


#-------EXTRACT ELEMENTS FROM ACTIVE MODEL---------------
print("Collecting elements from active model...")

# Extract sheets from DOCUMENT
docareas = DB.FilteredElementCollector(revit.doc)\
                    .OfCategory(DB.BuiltInCategory.OST_Areas)\
                    .WhereElementIsNotElementType()\
                    .ToElements()
if docareas:
	try:
		areas_count = len(docareas)
	except: len([ docareas ])
	for i in range(areas_count):
		areas_filename.append(docfile)
	all_areas.extend(docareas)
	if debugg: print("DEBUG: areas extracted")
	print(str(areas_count) + " areas extracted")
	areas_count_total = areas_count
	areas_count = 0
else:
	print("\nNo areas in active model")


print("...done.")
console.insert_divider()
#--------------------------------------------------------
if debugg: print(worksharing)
if worksharing:
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
			iareas = DB.FilteredElementCollector(doclnk).OfCategory(DB.BuiltInCategory.OST_Areas).WhereElementIsNotElementType().ToElements()
		except:
			iareas = []
		
		if iareas:
			try:
				areas_count = len(iareas)
			except: 
				areas_count = len([ iareas ])
			all_areas.extend(iareas)
			for s in range(areas_count):
				areas_filename.append(lnkfile)
		
	#	sheetsnotsorted.extend(isheets)
		print(lnkfile + " processed with:" + str(areas_count) + ' areas.')
		areas_count_total = areas_count_total + areas_count
		links_running = index+1
	print(str(links_running) + " Total links processed.")
	console.insert_divider()
	#-------------------------------------------------------
else:
	print("LINKS NOT PROCESSED!")
	print("Check that links are loaded and link worksets are loaded / enabled.")
	console.insert_divider()

def unicode_to_ascii(data):
	if isinstance(data, unicode):
		data_encoded = data.encode('utf-8')
		data_cleaned = re.sub(r'[^\x00-\x7f]',r'',data_encoded)
		return data_cleaned.encode("ascii")
	else:
		return data


#-------CREATE EXPORT TABLE FOR SHEETS-----------

print("\nAssembling Areas table for export...")
area_table = []
# create sheet table structure
area_table.append(["File","Area Number","Area Name","Scheme","Area","Perimeter","Level",sp1_name])
# script-wide parameters for sheets

# iterate over all sheets
for index, element_area in enumerate(all_areas):
	# reset parameters
	dfname = ""
	areaname = ""
	areano = ""
	areascheme = ""
	areasize = ""
	perimeter = ""
	arealevel = ""
	thisdoc = element_area.Document
	
	if debugg:
		print('\n')
		print(element_area)
	
	areasize = element_area.Area
	
	if areasize:
		dfname = (os.path.split(thisdoc.PathName)[1])
		areaname = (element_area.get_Parameter(DB.BuiltInParameter.ROOM_NAME).AsString())
		#areaname = element_area.LookupParameter("Name").AsString
		areano = (element_area.get_Parameter(DB.BuiltInParameter.ROOM_NUMBER).AsString())
		areascheme = (element_area.AreaScheme.Name)
		perimeter = element_area.Perimeter
		try:
			arealevel = element_area.Level.Name
		except:
			arealevel = ""
		try:
			sp1 = element_area.LookupParameter(sp1_name).AsString()
			area_table.append([dfname,areano,areaname,areascheme,areasize,perimeter,arealevel,sp1])
		except:
			area_table.append([dfname,areano,areaname,areascheme,areasize,perimeter,arealevel])


print("...done.")
#-------------------------------------------------

#-------DEBUG TABLE---------------------------------
if debugg:
	noareassno = False
	areasno = True
	if len(area_table) > 500:
		areasno = forms.alert('Greater than 500 areas, display results?', yes=True, no=True, ok=False)
	else:
		noareassno = True
	if areasno or noareasno: 
		print('\nDEBUG: Areas Table')
		for row in area_table:
			print('DEBUG: ' + str(row))


console.insert_divider()

#-------FILE WRITING---------------------------------
# Create export paths
export_areas = os.path.join(docfolder, export_folder, (filename_areas + "." + filename_extension))

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

# Check if file exists and make copy
if os.path.isfile(export_areas):
	print("\nAreas export file found...")
	shutil.copy(export_areas, os.path.join(docfolder, export_folder, (filename_areas + "." + backup_extension)))
	print("...backed up file.")
else:
	print("Areas export file not found, new file will be created.")

# Write CSV output for Sheets
# 2019/03/08: Added codecs for Unicode
try:
	with codecs.open(export_areas, 'w+', encoding='utf-8') as f:
		print("\nWriting Areas export...")
		print(export_areas)
		writer = csv.writer(f, lineterminator='\n')
		writer.writerows(area_table)
		print("...done.")
except IOError as e:
	#console.close()
	print("I/O error({0}): {1}".format(e.errno, e.strerror))
	FileError = 1
	#sys.exit()
except: #handle other exceptions
	#console.close()
	print("\nUnexpected error writing to Areas export file: ", sys.exc_info()[0])
	FileError = 1
	#sys.exit()


# Zero out tables
area_table = []


console.insert_divider()
console.hide()
console.show()
#------------------------------------------------

#--------PRINT SUMMARY---------------------------
print(str(areas_count_total) + " areas exported")
print(" ")

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
