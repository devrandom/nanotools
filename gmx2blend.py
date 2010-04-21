# Gromacs PDB animation to Blender 3d Model Converter
#
# LICENSE: GPLv3 ( http://www.gnu.org/licenses/gpl.html )
#
# Miron Cuperman <c1.nano@niftybox.net>
# Tom Moore <http://machine-phase.blogspot.com/>
#
# Instructions:
#   * Copy proteindb.py to ~/.blender/scripts
#   * Create a directory for per-frame pdb files and name it the same as the
#   structure (e.g. "c60")
#   * Each per-frame pdb file should be named with the frame number and ".pdb"
#   extension. e.g. "1.pdb" through "999.pdb" and placed in the "c60" directory
#   * Run the script, choose your structure file (e.g. "c60.pdb")
#   * Advancing the frames will animate the structure
#   * To create the pdb frames from GROMACS, use the trjconv program:
#          trjconv -s <structure> -f traj.trr -o .pdb -sep
# 
# Modes: 
# 	1. Ball
# 		creates a ball model with overlapping spheres when using the standard parameters
#		the ball sizes can be adjusted by choosing a constant scaling factor (atom scale)
#		as well as a constant summand (atom sum) that is added to the ball size. 
#		With atom scale = 1	and atom sum = 0 one will get the covalent radius for any atom defined.
#		With atom scale = 0 and atom sum > 0 the model will have uniform ball sizes.
#	2. Sticks
#		creates a stick model. 
#		The stick diameter can be chosen here (Stick Thickness).
#		Until now the regular stick mode (as well as stick and ball) does only work for less than 
#		10000 atoms.
#	3. Sticks and Balls
#		A combination of ball and stick mode. When using standard parameters the atoms are scaled 
#		down a little bit.
#
# Model refinement:
#	The refinement of spheres and sticks can be chosen. With higher values the model becomes more 
#   detailed.
#
# Loosely based on:
#
# pdb Molecule 2 Blender 3d Model Converter by Malte Reimold 2006
#

import Blender
from Blender import *
from Blender.Draw import *
from pprint import pprint
from math import *
import bpy
import os
import re
import sys
from pprint import pprint
from proteindb import *

editmode = Window.EditMode()
if editmode: Window.EditMode(0)
scene = Blender.Scene.GetCurrent()

matlist = str(Material.Get ())

def material(type):
	mat_name = 'atom_' + type
	try:
		return Material.Get(mat_name)
	except:
		pass
	mat = Material.New(mat_name)

	if type == 'C':
		mat.R = 0.8
		mat.G = 0.8
		mat.B = 0.8

	elif type == 'H':
		mat = Material.New('H')
		mat.R = 0.6
		mat.G = 0.6
		mat.B = 0.6
		
	elif type == 'B':
		mat = Material.New('B')
		mat.R = 0.8
		mat.G = 0.6
		mat.B = 0.1
		
	elif type == 'P':
		mat = Material.New('P')
		mat.R = 0.9
		mat.G = 0.95
		mat.B = 0.1
		
	elif type == 'N':
		mat = Material.New('N')
		mat.R = 0.2
		mat.G = 0.1
		mat.B = 0.9
		
	elif type == 'O':
		mat = Material.New('O')
		mat.R = 1.0
		mat.G = 0.2
		mat.B = 0.1
		
	elif type == 'sticks':
		mat = Material.New('sticks')
		mat.R = 0.8
		mat.G = 0.8
		mat.B = 0.8
	else:
		mat = Material.New('anyatom')
		mat.R = 0.8
		mat.G = 1.0
		mat.B = 1.0
		
	return mat

def ball_mesh(type):
	global scatom, sumatom, refineballs, refinesticks
	mesh_name = "atom_" + type
	try:
		return Mesh.Get(mesh_name)
	except:
		pass
	me = Mesh.New(mesh_name)
	# Ball erstellen
	a = 0.0000	
	b = 0.0000
	vcount = 0
	da = 360.00 / refineballs.val
	db = 360.00 / refineballs.val
	#da = 30.0
	#db = 30.0
	dx = 0.0
	dy = 0.0
	dz = 0.0
	pi = asin(1)
	mat = material(type)
	if type == "C":	
		radius = 0.772
	elif type == "H": 
		radius = 0.373
	elif type == "B": 
		radius = 0.83
	elif type == "N": 
		radius = 0.71
	elif type == "O": 
		radius = 0.604
	elif type == "P": 
		radius = 0.93
	else: 
		radius = 0.8
		
	me.materials = [mat]
	
	radius = radius * scatom.val + sumatom.val
	
	
	# erster Punkt
	me.verts.extend(0, 0, radius)
	a = a + da
	
	# Kappe
		
	while b < 360:
		dz = radius*cos(a/90*pi)
		dx = radius*sin(a/90*pi)*sin(b/90*pi)
		dy = radius*sin(a/90*pi)*cos(b/90*pi)
		b = b + db
		me.verts.extend(dx, dy, dz)
		vcount = vcount + 1
		if vcount > 1:
			me.faces.extend([me.verts[0],me.verts[vcount],me.verts[vcount-1]])
	
	me.faces.extend([me.verts[0],me.verts[1],me.verts[vcount]])
	
	b = 0.00
	kcount = 0
	vvcount = 0
	a = a + da
	
	
	while a < 180:
		while b < 360:
			dz = radius*cos(a/90*pi)
			dx = radius*sin(a/90*pi)*sin(b/90*pi)
			dy = radius*sin(a/90*pi)*cos(b/90*pi)
			me.verts.extend(dx, dy, dz)
			vcount = vcount + 1
			vvcount = vvcount + 1
			if vvcount > 1:
				me.faces.extend([me.verts[vcount],me.verts[vcount-1],me.verts[vcount-int(360/db)-1],me.verts[vcount-int(360/db)]])
				if b == 360-db:
					me.faces.extend([me.verts[vcount],me.verts[vcount-int(360/db)],me.verts[vcount-2*int(360/db)+1],me.verts[vcount-int(360/db)+1]])
			b = b + db
		kcount = kcount + 1
		b = 0
		vvcount = 0
		a = a + da
		
	me.verts.extend(0, 0, -radius)
	vcount = vcount + 1
	b = 0
	while b < 360-db:
		me.faces.extend([me.verts[vcount],me.verts[vcount-int(b/db)-2],me.verts[vcount-int(b/db)-1]])
		b = b + db
	
	me.faces.extend([me.verts[vcount],me.verts[vcount-1],me.verts[vcount-int((360-db)/db)-1]])
	eins = 1
	for face in me.faces:
		face.smooth=1
	return me
	


def ball(atom):
	ob = Object.New('Mesh', atom.name)
	ob.link(ball_mesh(atom.type))
	ob.loc = (atom.x,atom.y,atom.z)
	scene.link (ob)
	
def import_pdb(path):
	global structmode, scatom, sumatom, refineballs, refinesticks, scsticks, balls, sticks, hydros
	Blender.Window.WaitCursor(1)
	atoms = {}
	line_count = 0
	file = open(path, 'r')
	for line in file.readlines():
		line_count += 1
	file.close()
	file = open(path, 'r')
	Window.DrawProgressBar(0.0, 'Atoms')
	line_no = 0
	for line in file.readlines():
		line_no += 1
		if line_no % 100 == 0:
			Window.DrawProgressBar(float(line_no) / line_count, 'Atoms')
		parsed = parse_pdb_line(line)
		if parsed[0] == 'pass':
			pass
		elif parsed[0] == 'atom':
			atom = parsed[1]
			atoms[atom.name] = atom

			if balls and (atom.type != 'H' or hydros):
				ball(atom)

		elif parsed[0] == 'ter':
			pass
		elif parsed[0] == 'connect' and sticks:
			con0 = parsed[1]
			for i in range(0,4):
				con1 = parsed[2+i]
				if con1 > -1 and con1 > con0:
					a0 = atoms[con0]
					a1 = atoms[con1]
					if hydros or (a0.type!='H' and a1.type!='H'):
						stick3(a0, a1, scsticks.val)

	try:
		updater = Text.Get("pdb_updater")
		updater.clear()
	except:
		updater = Text.New("pdb_updater")
	updater.write("from proteindb import *\napply_pdb(r'" + path + "')\n")
	scene.addScriptLink("pdb_updater", "FrameChanged")
	scene.update()
	Blender.Redraw()		     
	Blender.Window.WaitCursor(0)

def gui():
	global structmode, scatom, sumatom, refineballs, refinesticks, balls, sticks, scsticks, hydros, bbut, sbbut, sbut, pbut
	bbut = Toggle('Balls',3, 40, 240, 80, 19, bbut.val)
	sbbut = Toggle('Sticks and Balls',4, 120, 240, 150, 19, sbbut.val)
	sbut = Toggle('Sticks',5, 270, 240, 80, 19, sbut.val)
	if hydros: Button('Hydrogens on',11, 40, 190, 310, 19)
	else: Button('Hydrogens off',11, 40, 190, 310, 19)
	if balls: scatom = Slider('Atom Scale :', 6, 40, 160, 310,19, scatom.val, 0.00, 4.00)
	if balls: sumatom = Slider('Atom Sum :', 7, 40, 140, 310,19, sumatom.val, 0.00, 2.00)
	if balls: refineballs = Slider('Atom Refinement :', 8, 40, 120, 310,19, refineballs.val, 4, 36)
	if sticks or pbut.val: scsticks = Slider('Stick Thickness :', 9, 40, 90, 310,19, scsticks.val, 0.00, 4.00)
	if sticks or pbut.val: refinesticks = Slider('Stick Refinement :', 10, 40, 70, 310,19, refinesticks.val, 4, 36)
	Button('Import',1, 40, 40, 155, 19)
	Button('Cancel',2, 195, 40, 155, 19)

def event(evt, val):
	if (evt == ESCKEY and not val): Exit()

def bevent(evt):
	global structmode, scatom, sumatom, refineballs, refinesticks, balls, sticks, scsticks, hydros, bbut, sbbut, sbut, pbut
	if evt == 2: Exit()
	elif evt == 1: 
		Blender.Window.FileSelector(import_pdb, 'Import')
	elif evt == 3:
		structmode = "balls"
		scatom.val = 1.0
		sumatom.val = 0.4
		refineballs.val = 24
		balls = 1
		sticks = 0
		bbut.val = 1
		sbbut.val = 0
		sbut.val = 0
		pbut.val = 0
		Redraw()
	elif evt == 4:
		structmode = "sticks and balls"
		scatom.val = 0.75
		sumatom.val = 0.0
		refineballs.val = 20
		refinesticks.val = 12
		balls = 1
		scsticks.val = 0.16
		sticks = 1
		bbut.val = 0
		sbbut.val = 1
		sbut.val = 0
		pbut.val = 0
		Redraw()
	elif evt == 5:
		structmode = "sticks"
		scsticks.val = 0.24
		refinesticks.val = 12
		balls = 0
		sticks = 1
		bbut.val = 0
		sbbut.val = 0
		sbut.val = 1
		pbut.val = 0
		Redraw()
	elif evt == 11: 
		if hydros: hydros = 0
		else: hydros = 1
		Redraw()
	elif evt == 8:
		while not ((int(360/refineballs.val) == float(360.00/refineballs.val)) and (int(refineballs.val)/2) == (float(refineballs.val)/2)):
			refineballs.val = refineballs.val + 1
		Redraw()
	elif evt == 10:
		while not ((int(360/refinesticks.val) == float(360.00/refinesticks.val)) and (int(refinesticks.val)/2) == (float(refinesticks.val)/2)):
			refinesticks.val = refinesticks.val + 1
		Redraw()

def initialize():
	global structmode, scatom, sumatom, refineballs, refinesticks, balls, sticks, scsticks, hydros, bbut, sbbut, sbut, pbut
	structmode = Create("balls")
	scatom = Create(1.0)
	sumatom = Create(0.4)
	scsticks = Create(0.24)
	refineballs = Create(24)
	refinesticks = Create(12)
	balls = Create(1)
	sticks = Create(0)
	hydros = Create(1)
	bbut = Create(1)
	sbbut = Create(0)
	sbut = Create(0)
	pbut = Create(0)
	Register(gui, event, bevent)

initialize()

Blender.Redraw()
