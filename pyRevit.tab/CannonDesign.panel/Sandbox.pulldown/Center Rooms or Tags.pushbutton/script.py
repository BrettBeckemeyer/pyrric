# coding: utf8
import rpw
from rpw import revit
from pyrevit import DB
from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, Transaction
import System
from pyrevit.forms import WPFWindow
from pyrevit import script, forms

__title__ = 'Center Rooms or Tags'
__author__ = 'Brett Beckemeyer (bbeckemeyer@cannondesign.com)'
__doc__ = 'Move room location points and / or room tags to room centers'

logger = script.get_logger()

doc = revit.doc
activeView = doc.ActiveView
activeViewId = activeView.Id

def sample_id_by_category(doc, category):
	return FilteredElementCollector(doc).OfCategory(category).FirstElementId()


class Gui(WPFWindow):
	def __init__(self, xaml_file_name):
		WPFWindow.__init__(self, xaml_file_name)

	@property
	def rb_model(self):
		return self.Model_rb.IsChecked

	@property
	def rb_active(self):
		return self.Active_rb.IsChecked

	@property
	def cb_locations(self):
		return self.locations_cb.IsChecked

	@property
	def cb_locations(self):
		return self.locations_cb.IsChecked

	@property
	def cb_tags(self):
		return self.tags_cb.IsChecked

#EDITED
	def get_rooms(self):
		if self.rb_model:
			roomCollector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms).ToElements()
		elif self.rb_active:
			roomCollector = FilteredElementCollector(doc, activeViewId).OfCategory(BuiltInCategory.OST_Rooms).ToElements()
		else:
			roomCollector = []
		return roomCollector
#/EDITED

#EDITED
	def get_tags(self):
		roomtagCollector = FilteredElementCollector(doc, activeViewId).OfCategory(BuiltInCategory.OST_RoomTags).ToElements()
		return roomtagCollector
#/EDITED

#EDITED
	def room_center_location(self, room):
		calc = DB.SpatialElementGeometryCalculator(doc)
		# Checks for valid rooms (placed)
		if calc.CanCalculateGeometry(room):
			roomSolid = calc.CalculateSpatialElementGeometry(room).GetGeometry()
			roomCentroid = roomSolid.ComputeCentroid()
			roomValid = True
		else:
			roomValid = False
		if roomValid and room.IsPointInRoom(roomCentroid):
			rP = roomCentroid - room.Location.Point
			room.Location.Move(rP)
#/EDITED

#EDITED
	def tag_to_loc(self, tag):
		tag_pt = tag.Location.Point
		tag_rm = tag.Room
		rm_pt = tag_rm.Location.Point
		tP = rm_pt - tag_pt
		tag.Location.Move(tP)
#/EDITED

	# noinspection PyUnusedLocal
	def ok_click(self, sender, e):
		with rpw.db.Transaction(doc=doc, name="RoomTools"):
			if self.rb_model or self.rb_active and self.cb_locations:
				rooms = self.get_rooms()
				if len(rooms) == 0:
					logger.info("No rooms were found")
					raise ValueError("No rooms were found in the view or model")
				else:
					for room in rooms:
						self.room_center_location(room)
			if self.rb_active and self.cb_tags:
				tags = self.get_tags()
				if len(tags) == 0:
					logger.info("No tags were found in the view")
					raise ValueError("No tags were found in the view")
				else:
					for tag in tags:
						self.tag_to_loc(tag)
		self.Close()

	# noinspection PyUnusedLocal
	def window_closed(self, sender, e):
		pass


gui = Gui("WPFWindow.xaml")
gui.ShowDialog()
