"""Toggles background of views between white and black"""

__author__ = 'Brett Beckemeyer (bbeckemeyer@cannondesign.com)'
from pyrevit import revit, DB
from pyrevit import script
from pyrevit.coreutils.ribbon import ICON_MEDIUM

# for timing -------------------------------------------------------------------
from pyrevit.coreutils import Timer
timer = Timer()
# ------------------------------------------------------------------------------


from System.Collections.Generic import List

import Autodesk.Revit.DB as DB

app = __revit__.Application

# not used ----------------------------------
#doc = __revit__.ActiveUIDocument.Document
#uidoc = __revit__.ActiveUIDocument
#app = UIApplication.Application
# --------------------------------------------

#----------SETUP COLORS FOR CHECKING----------
check_black = []
check_white = []
bg_check = []

color_black = DB.Color(0,0,0)
color_white = DB.Color(255,255,255)

check_black.append(color_black.Red)
check_black.append(color_black.Green)
check_black.append(color_black.Blue)

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
        if bg_check1 == check_black:
            #print('Background is black!')
            bg_state = False
        elif bg_check1 == check_white:
            #print('Background is not white!')
            bg_state = True
        else:
            exit()
        script.toggle_icon(bg_state)
        return True
    except:
        return False


def toggle_state():
    abc = app.BackgroundColor
    bg_check2 = get_bg_col(abc)

    if bg_check2 == check_black:
        #print('Background is black!')
        app.BackgroundColor = color_white
        bg_state = True
    elif bg_check2 == check_white:
        #print('Background is not black!')
        app.BackgroundColor = color_black
        bg_state = False
    else:
        exit()

    script.toggle_icon(bg_state)


if __name__ == '__main__':
    toggle_state()

# for timing -------------------------------------------------------------------
#endtime = timer.get_time()
#print(endtime)
# ------------------------------------------------------------------------------
