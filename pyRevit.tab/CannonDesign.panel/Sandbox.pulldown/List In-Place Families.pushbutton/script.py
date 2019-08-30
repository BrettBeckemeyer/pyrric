# -*- coding: utf-8 -*-
"""Handling In-Place Families"""

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
debugg = True
# ...

#----------BASIC VARIABLE DEFINITIONS--------
export_folder = 'C:\Temp'
export_extension = 'in-place.csv'


#-----------END VARIABLE DEFINITIONS----------


# 2019/03/05: Added pyrevit version checks
#-----------GET PYREVIT VERSION----------------
pyrvt_ver = versionmgr.get_pyrevit_version()
short_version = \
      '{}'.format(pyrvt_ver.get_formatted(nopatch=True))
vv = short_version.split(".")
pyrvt_ver_main = int(vv[0])
pyrvt_ver_min = int(vv[1])


#----------CONSOLE WINDOW AND ELEMENT STYLES--------

console = script.get_output()
console.set_height(480)
console.lock_size()


report_title = 'In-Place Families'
report_date = coreutils.current_date()
# 2/1/2019: added query method to replace deprecated revit.get_project_info()
try:
	report_project = revit.query.get_project_info().name
except:
	report_project = revit.get_project_info().name

print(report_project)


# setup element styling
console.add_style(
    'table { border-collapse: collapse; width:100% }'
    'table, th, td { border-bottom: 1px solid #aaa; padding: 5px;}'
    'th { background-color: #545454; color: white; }'
    'tr:nth-child(odd) {background-color: #f2f2f2}'
    )

#--------END CONSOLE AND STYLES-----------------------


try:
	docpath = revit.query.get_central_path(doc=revit.doc)
except:
	try:
		docpath = DB.ModelPathUtils.ConvertModelPathToUserVisiblePath(revit.doc.GetWorksharingCentralModelPath())
	except:
		docpath = revit.doc.PathName

# Split file path
(docfolder, docfile) = os.path.split(docpath)


export_filename = docfile + "_" + export_extension
export_file = os.path.join(export_folder, export_filename)


family_instances = DB.FilteredElementCollector(revit.doc).OfClass(DB.FamilyInstance).ToElements()
fams_filtered = set()
instances_filtered = []

table = []
table.append(["Element ID","Name","Tranform X","Transform Y","Transform Z","Transform Determinant","Location Point","Rotation","Facing Flipped","Facing Orientation", "Hand Flipped", "Hand Orientation"])

counter = 0

for index, i in enumerate(family_instances):
	i_fam = i.Symbol.Family
	#print(i_fam)
	#print(i_fam.Name)
	if (i_fam.IsInPlace):
		fams_filtered.add(i_fam)
		instances_filtered.append(i)
		counter = counter + 1
		i_id = i.Id.ToString()
		i_name = i.Name
		i_tX = i.GetTransform().BasisX.ToString()
		i_tY = i.GetTransform().BasisY.ToString()
		i_tZ = i.GetTransform().BasisZ.ToString()
		i_tD = i.GetTransform().Determinant
		i_lP = i.Location.Point.ToString()
		i_lR = i.Location.Rotation
		i_FFlip = i.FacingFlipped
		i_FO = i.FacingOrientation.ToString()
		i_HFlip = i.HandFlipped
		i_HO = i.HandOrientation.ToString()
		table.append([i_id, i_name, i_tX, i_tY, i_tZ, i_tD, i_lP, i_lR, i_FFlip, i_FO, i_HFlip, i_HO]) 
		#print(i_fam.Name)

print('# of In-Place Families: ' + str(len(fams_filtered)))
print('# of In-Place Instances: ' + str(len(instances_filtered)))

#print(table)

# Check if file exists and make copy
#if os.path.isfile(export_file):
#	print("\nExport file found...")
#	shutil.copy(export_file, os.path.join(docfolder, export_folder, (filename_sheets + "." + backup_extension)))
#	print("...backed up file.")
#else:
#	print("Sheets export file not found, new file will be created.")

# Write CSV output
try:
	with codecs.open(export_file, 'w+', encoding='utf-8') as f:
		print("\nWriting export...")
		print(export_file)
		writer = csv.writer(f, lineterminator='\n')
		writer.writerows(table)
		print("...done.")
except IOError as e:
	#console.close()
	print("I/O error({0}): {1}".format(e.errno, e.strerror))
	#FileError = 1
	sys.exit()
except: #handle other exceptions
	#console.close()
	print("\nUnexpected error writing to Sheets export file: ", sys.exc_info()[0])
	#FileError = 1
	sys.exit()


"""
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
"""