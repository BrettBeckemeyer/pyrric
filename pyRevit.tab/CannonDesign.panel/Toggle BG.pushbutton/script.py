"""Toggles background of views between white and non_white"""
"""Updated 2019-08-19 to add dialog for custom color selection"""
"""Updated 2019-09-10 to deal with hex colors"""

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

def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

def get_bg_col(abc):
    bg_check.append(abc.Red)
    bg_check.append(abc.Green)
    bg_check.append(abc.Blue)
    return bg_check

#-----------GET CONFIG DATA-------------------
my_config = script.get_config()
selected_color = my_config.get_option('selected_color', default_value=('black',0,0,0))
#---------------------------------------------

selected_color_R = 0
selected_color_G = 0
selected_color_B = 0

if selected_color:
	#print(selected_color[:1])
	if selected_color[:1] == "#":
		selected_color = hex_to_rgb(selected_color)
		#print(selected_color)
		num = 0
	else:
		num = 1
	selected_color_R = selected_color[num]
	num = num+1
	selected_color_G = selected_color[num]
	num = num+1
	selected_color_B = selected_color[(num)]


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
