import os

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextCursor, QTextBlockFormat, QColor, QPalette, QTextFormat
from PyQt6.QtWidgets import QTextEdit

import linuxcnc as emc

def is_float(string):
	try:
		float(string)
		return True
	except ValueError:
		return False

def is_int(string):
	try:
		int(string)
		return True
	except ValueError:
		return False

def all_homed(parent):
	parent.status.poll()
	return parent.status.homed.count(1) == parent.status.joints

def all_unhomed(parent):
	parent.status.poll()
	num_joints = parent.status.joints
	home_status = parent.status.homed[:num_joints]
	test_list = []
	for i in range(num_joints):
		test_list.append(0)
	test_tuple = tuple(test_list)
	return home_status == test_tuple

def home_all_check(parent):
	parent.status.poll()
	for i in range(parent.status.joints):
		if parent.inifile.find(f'JOINT_{i}', 'HOME_SEQUENCE') is None:
			return False
	return True

def set_enables(parent): # FIXME this may handle enables dunno
	print('set_enables')

	# STATE_ON
	# ALL HOMED
	# FILE LOADED

def set_homed_enable(parent):
	for item in parent.home_controls:
		getattr(parent, item).setEnabled(False)
	for item in parent.unhome_controls:
		getattr(parent, item).setEnabled(True)
	for item in parent.home_required:
		getattr(parent, item).setEnabled(True)
	if parent.status.file:
		for item in parent.run_controls:
			getattr(parent, item).setEnabled(True)

def update_jog_lb(parent):
	parent.jog_vel_lb.setText(f'{parent.jog_vel_sl.value()} {parent.units}/min')

def add_mdi(parent):
	parent.mdi_command_le.setText(f'{parent.mdi_history_lw.currentItem().text()}')

def clear_errors(parent):
	parent.errors_pte.clear()
	parent.statusbar.clearMessage()

def update_mdi(parent):
	parent.mdi_history_lw.addItem(parent.mdi_command)
	path = os.path.dirname(parent.status.ini_filename)
	mdi_file = os.path.join(path, 'mdi_history.txt')
	mdi_codes = []
	for index in range(parent.mdi_history_lw.count()):
		mdi_codes.append(parent.mdi_history_lw.item(index).text())
	with open(mdi_file, 'w') as f:
		f.write('\n'.join(mdi_codes))
	parent.mdi_command_le.setText('')
	parent.command.mode(emc.MODE_MANUAL)
	parent.command.wait_complete()
	parent.mdi_command = ''

def print_states(parent, state):
	parent.print_states = parent.print_states_cb.isChecked()

def feed_override(parent, value):
	parent.command.feedrate(float(value / 100))

def rapid_override(parent, value):
	parent.command.rapidrate(float(value / 100))

def spindle_override(parent, value):
	parent.command.spindleoverride(float(value / 100), 0)

def update_qcode_pte(parent):
	extraSelections = []
	if not parent.gcode_pte.isReadOnly():
		selection = QTextEdit.ExtraSelection()
		lineColor = QColor('yellow').lighter(160)
		selection.format.setBackground(lineColor)
		selection.format.setForeground(QColor('black'))
		selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
		selection.cursor = parent.gcode_pte.textCursor()
		selection.cursor.clearSelection()
		extraSelections.append(selection)
	parent.gcode_pte.setExtraSelections(extraSelections)
	if 'start_line_lb' in parent.children:
		cursor = parent.gcode_pte.textCursor()
		selected_block = cursor.blockNumber() # get current block number
		parent.start_line_lb.setText(f'{selected_block}')

def read_dir(parent):
	if os.path.isdir(parent.gcode_dir):
		file_list = []
		# get directories
		for item in sorted(os.listdir(parent.gcode_dir)):
			path = os.path.join(parent.gcode_dir, item)
			if os.path.isdir(path):
				file_list.append(f'{item} ...')
		# get gcode files
		for item in sorted(os.listdir(parent.gcode_dir)):
			if os.path.splitext(item)[1].lower() in parent.extensions:
				file_list.append(item)
		parent.file_lw.clear()
		parent.file_lw.addItem('Parent Directory')
		parent.file_lw.addItems(file_list)
		parent.file_lw.setMinimumWidth(parent.file_lw.sizeHintForColumn(0)+60)

def view_clear(parent):
	parent.plotter.clear_live_plotter()

def view_pan_up(parent):
	parent.view_y = parent.view_y - 10
	parent.plotter.translateOrRotate(parent.view_x, parent.view_y)

def view_pan_down(parent):
	parent.view_y = parent.view_y + 10
	parent.plotter.translateOrRotate(parent.view_x, parent.view_y)

def view_pan_left(parent):
	parent.view_x = parent.view_x - 10
	parent.plotter.translateOrRotate(parent.view_x, parent.view_y)

def view_pan_right(parent):
	parent.view_x = parent.view_x + 10
	parent.plotter.translateOrRotate(parent.view_x, parent.view_y)

def view_rotate_up(parent): # rotateView(self,vertical=0,horizontal=0)
	parent.plotter.rotateView(0, -2)

def view_rotate_down(parent): # rotateView(self,vertical=0,horizontal=0)
	parent.plotter.rotateView(0, 2)

def view_rotate_left(parent): # rotateView(self,vertical=0,horizontal=0)
	parent.plotter.rotateView(-2, 0)

def view_rotate_right(parent): # rotateView(self,vertical=0,horizontal=0)
	parent.plotter.rotateView(2, 0)

def view_zoom_in(parent):
	parent.plotter.distance = parent.plotter.distance - 1
	parent.plotter.update()

def view_zoom_out(parent):
	parent.plotter.distance = parent.plotter.distance + 1
	parent.plotter.update()

def view_p(parent):
	parent.plotter.current_view = 'p'
	parent.plotter.load()

def view_x(parent):
	parent.plotter.current_view = 'x'
	parent.plotter.set_current_view()
	#parent.plotter.load()

def view_limits(parent):
	if parent.sender().isChecked():
		parent.plotter.show_limits = True
	else:
		parent.plotter.show_limits = False
	parent.plotter.load()

def test(parent):
	if parent.plotter.metric_units:
		parent.plotter.metric_units = False
	else:
		parent.plotter.metric_units = True
	parent.plotter.load()

def view_units(parent):
	if parent.sender().isChecked():
		parent.plotter.metric_units = False
	else:
		parent.plotter.metric_units = True
	parent.plotter.load()

def view_vel(parent):
	if parent.sender().isChecked():
		parent.plotter.show_velocity = False
	else:
		parent.plotter.show_velocity = True
	parent.plotter.load()

def view_dro(parent):
	if parent.sender().isChecked():
		parent.plotter.enable_dro = False
	else:
		parent.plotter.enable_dro = True
	parent.plotter.load()




