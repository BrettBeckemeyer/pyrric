# pyrric (CannonDesign pyRevit Extensions)

A set of Extensions for Autodesk Revit scripted to work within the pyRevit ecosystem

Prerequisite: pyRevit must be installed from https://github.com/eirannejad/pyRevit
Credits / Contributors: Ehsan Iran-Nejad (pyRevit)
Maintainted by: 	Sean Park (spark@cannondesign.com), 
​				Brett Beckemeyer (bbeckemeyer@cannondesign.com)

EXTENSIONS
-------

00_NEW EXTENSIONS-------------------New pyRevit extensions created for pyrric

```
Toggle BG.pushbutton------------Toggle the view background between white and a
								secondary color
Revisions.pulldown:
	Export Revisions.pushbutton-----Export Revision Cloud data (plus sheets) to .CSV 
									files for external workflows
	Get ReasonIDs.pushbutton--------Displays the project's list of Reason IDs.

Sandbox.pulldown: (added Sandbox for items in development)
	Areas Export.pushbutton---------Exports area data from multiple linked models to a
									.CSV file
	Center Rooms or Tags.pushbutton-Centers room location points and / or room tags
									across active view or entire model
```

01_FIXES FOR EXISTING EXTENSIONS----Updates to original pyRevit extensions

	Set Revisions on Sheets.pushbutton--Allows for selecting sheets on project browser
	Increment Sheet Numbers.pushbutton--Has setting to exclude alpha characters
	Decrement Sheet Numbers.pushbutton--Has setting to exclude alpha characters
	Generate Revision Report.pushbutton-Fixed to work with "by sheet" numbering

NOTES
-----
For installations instructions, usage notes, etc - see the readme.md file in each extension's subfolder.

Created: 27/07/2018
Last Updated: 19/08/2019