"""Toggles background of views between white and non_white"""
"""Updated 2019-08-19 to add dialog for custom color selection"""

__author__ = 'Brett Beckemeyer (bbeckemeyer@cannondesign.com)'
from pyrevit import revit, DB
from pyrevit import script
from pyrevit.coreutils.ribbon import ICON_MEDIUM

# for timing -------------------------------------------------------------------
from pyrevit.coreutils import Timer
timer = Timer()
# ------------------------------------------------------------------------------

__context__ = 'zerodoc'
__title__ = 'Toggle\nBackground'

from System.Collections.Generic import List

import Autodesk.Revit.DB as DB

app = __revit__.Application

# not used ----------------------------------
#doc = __revit__.ActiveUIDocument.Document
#uidoc = __revit__.ActiveUIDocument
#app = UIApplication.Application
# --------------------------------------------

#-----------GET CONFIG DATA-------------------
my_config = script.get_config()
selected_color = my_config.get_option('selected_color', default_value=('black',0,0,0))
#selected_color_R = my_config.get_option('selected_color')[1]
#selected_color_G = my_config.get_option('selected_color')[2]
#selected_color_B = my_config.get_option('selected_color')[3]
#---------------------------------------------

if selected_color:
	selected_color_R = selected_color[1]
	selected_color_G = selected_color[2]
	selected_color_B = selected_color[3]
else:
	selected_color_R = 0
	selected_color_G = 0
	selected_color_B = 0

#----------SETUP COLORS FOR CHECKING----------
check_non_white = []
check_white = []
bg_check = []

#color_non_white = DB.Color(0,0,0)
color_non_white = DB.Color(selected_color_R,selected_color_G,selected_color_B)
color_white = DB.Color(255,255,255)

check_non_white.append(color_non_white.Red)
check_non_white.append(color_non_white.Green)
check_non_white.append(color_non_white.Blue)

check_white.append(color_white.Red)
check_white.append(color_white.Green)
check_white.append(color_white.Blue)
#---------------------------------------------
#bg_col = app.BackgroundColor
#
#bg_check.append(bg_col.Red)
#bg_check.append(bg_col.Green)
#bg_check.append(bg_col.Blue)
#---------------------------------------------

def get_bg_col(abc):
    bg_check.append(abc.Red)
    bg_check.append(abc.Green)
    bg_check.append(abc.Blue)
    return bg_check


def __selfinit__(script_cmp, ui_button_cmp, __rvt__):
    try:
        abc = app.BackgroundColor
        bg_check1 = get_bg_col(abc)
        if bg_check1 == check_white:
            #print('Background is white!')
            bg_state = True
        else:
            #print('Background is not white!')
            bg_state = False
        script.toggle_icon(bg_state)
        return True
    except:
        return False


def toggle_state():
    abc = app.BackgroundColor
    bg_check2 = get_bg_col(abc)

    if bg_check2 == check_white:
        #print('Background is white!')
        app.BackgroundColor = color_non_white
        bg_state = False
    else:
        #print('Background is not white!')
        app.BackgroundColor = color_white
        bg_state = True

    script.toggle_icon(bg_state)


if __name__ == '__main__':
    toggle_state()

# for timing -------------------------------------------------------------------
#endtime = timer.get_time()
#print(endtime)
# ------------------------------------------------------------------------------
