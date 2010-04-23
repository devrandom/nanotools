# LICENSE: GPLv3 ( http://www.gnu.org/licenses/gpl.html )
#
# A standalone script for importing Ipo (animation) curves from
# CSV files.
#
# Miron Cuperman <c1.nano@niftybox.net>

import Blender

from pprint import pformat
from Blender import *
from Blender.Draw import *
import bpy
import os
import re
from zipfile import ZipFile

def importIpo(ob, input_f):
  comma_re = re.compile(r"\,\s*")
  myIpo = bpy.data.ipos.new('ipo' + ob.getName().strip(), 'Object')

  
  # Create LocX, LocY, and LocZ Ipo curves in our new Curve Object
  # and store them so we can access them later
  ipo_x = myIpo.addCurve('LocX')
  ipo_y = myIpo.addCurve('LocY')
  ipo_z = myIpo.addCurve('LocZ')
  frame = 1
  while True:
    line = input_f.readline()
    if line == "":
      break
    data = comma_re.split(line)
    ipo_x.append((frame, data[1]))
    ipo_y.append((frame, data[2]))
    ipo_z.append((frame, data[3]))
    frame = frame + 1
  ob.setIpo(myIpo)

def do_import(file):
  Blender.Window.WaitCursor(1)

  z = ZipFile(file)
  line_re = re.compile('\r?\n')

  for ob in Object.Get():
    name = ob.getName()
    try:
      file = z.open("atom_" + name.strip() + ".csv")
      print "Importing ", name
      importIpo(ob, file)
    except KeyError:
      pass

  Blender.Window.WaitCursor(0)

def gui():
  Button('Import',1, 40, 40, 155, 19)
  Button('Cancel',2, 195, 40, 155, 19)

def event(evt, val):
  if (evt == ESCKEY and not val): Exit()

def bevent(evt):
  if evt == 2: Exit()
  elif evt == 1: 
    Blender.Window.FileSelector(do_import, 'ZIP of CSV files')

Register(gui, event, bevent)
Blender.Redraw()
