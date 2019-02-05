"""Updated version by Brett Beckemeyer on 10/31/2018 which includes config page to exlude alpha characters."""
from pyrevit import coreutils
from pyrevit import revit, DB
from pyrevit import forms
from pyrevit import script


__doc__ = 'Decreases the sheet number of the selected sheets by one. '\
          'The sheet name change will be printed if logging is set '\
          'to Verbose in pyRevit settings.'


viewtype = []
viewsheetcheck = []
selected_sheets = []

logger = script.get_logger()

#-----------GET CONFIG DATA--------------------
my_config = script.get_config()
alpha_chars = my_config.get_option('process_alpha', default_value=True)

selection = revit.get_selection()

def _inc_string(str_id, shift):
	"""Increment or decrement identifier.

	Args:
		str_id (str): identifier e.g. A310a
		shift (int): number of steps to change the identifier

	Returns:
		str: modified identifier

	Example:
		>>> _inc_or_dec_string('A319z')
		'A320a'

	alpha_chars = ""
	alpha_chars = bool("yes")
	"""

	next_str = ""
	index = len(str_id) - 1
	index2 = index
	process_index = index
	carry = shift

	"""
	if not alpha_chars:
		while index2 >= 0:
			if str_id[index2].isdigit():
				process_index = index2
				index2 = 0
			else:
				index2 -= 1
	"""

	while index >= 0:
		if process_index == index:
			process_index = index - 1
			if str_id[index].isalpha() and alpha_chars:
				curr_digit = (ord(str_id[index]) + carry)

				if str_id[index].islower():
					reset_a = 'a'
					reset_z = 'z'
				else:
					reset_a = 'A'
					reset_z = 'Z'

				if curr_digit < ord(reset_a):
					curr_digit = ord(reset_z) - ((ord(reset_a) - curr_digit) - 1)
					carry = shift
				elif curr_digit > ord(reset_z):
					curr_digit = ord(reset_a) + ((curr_digit - ord(reset_z)) - 1)
					carry = shift
					process_index = index
				else:
					carry = 0

				curr_digit = chr(curr_digit)
				next_str += curr_digit

			elif str_id[index].isdigit():

				curr_digit = int(str_id[index]) + carry
				if curr_digit > 9:
					curr_digit = 0 + ((curr_digit - 9)-1)
					carry = shift
					process_index = index
				elif curr_digit < 0:
					curr_digit = 9 - ((0 - curr_digit)-1)
					carry = shift
				else:
					carry = 0
				next_str += coreutils.safe_strtype(curr_digit)

			else:
				next_str += str_id[index]

		else:
			next_str += str_id[index]

		index -= 1

	return next_str[::-1]


shift = -1

for i in selection:
	try:
		viewsheetcheck.append(str(i.ViewType) == 'DrawingSheet')
	except:
		viewsheetcheck.append(False)
	if all(viewsheetcheck):
		selected_sheets = selection
	if not selected_sheets:
		selected_sheets = forms.select_sheets(title='Select Sheets')
	if not selected_sheets:
		script.exit()

sorted_sheet_list = sorted(selected_sheets, key=lambda x: x.SheetNumber)

if shift >= 0:
    sorted_sheet_list.reverse()

with revit.Transaction('Shift Sheets'):
    for sheet in sorted_sheet_list:
        try:
            cur_sheet_num = sheet.SheetNumber
            sheet_num_param = sheet.LookupParameter('Sheet Number')
            sheet_num_param.Set(_inc_string(sheet.SheetNumber,
                                                        shift))
            new_sheet_num = sheet.SheetNumber
            logger.info('{} -> {}'.format(cur_sheet_num, new_sheet_num))
        except Exception as shift_err:
            logger.error(shift_err)

    revit.doc.Regenerate()
