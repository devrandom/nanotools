#
# LICENSE: GPLv3 ( http://www.gnu.org/licenses/gpl.html )
#

import os
import re
from Blender import *

sym_re = re.compile('[.0-9 \r]')

def parse_pdb_line(line):
	if len(line) == 0 or line == ('END'):
		return ['pass']
	elif line[:6] == 'HETATM' or line[:4] == 'ATOM':
		atom = Atom()
		atom.name = line[7:11].strip()
		if len(line) > 76: 
			atom.type = line[77:(len(line)-1)].strip()
		else:
			atom.type = line[13:16].strip()
			atom.type = sym_re.sub("", atom.type)
		atom.x = float(line[31:38].strip())
		atom.y = float(line[39:46].strip())
		atom.z = float(line[47:54].strip())
		return ['atom', atom]
	elif line[:3] == 'TER':
		return ['ter']
	elif line[:6] == 'CONECT':
		con0 = line[6:11].strip()
		res = ['connect', con0, -1, -1, -1, -1]
		for i in range(0,4):
			if len(line) > (15 + 5 * i):
				if not line[(11+5*i):(16+5*i)] == '     ':
					con1 = line[(11+5*i):(16+5*i)].strip()
					res[i+2] = con1
		return res
	else:
		return ['pass']

def apply_pdb(path):
	path = path.rsplit(".", 1)[0]
	frame = Get('curframe')

	traj_file_name = os.path.join(path, str(frame) + ".pdb")
	try:
		traj_file = open(traj_file_name, "r")
	except:
		print "could not open" + traj_file_name
		return
	print traj_file_name
	while True:
		line = traj_file.readline()
		if line == "":
			break
		parsed = parse_pdb_line(line)
		if parsed[0] != 'atom':
			continue
		atom = parsed[1]
		try:
			ob = Object.Get(atom.name)
		except:
			print "did not find atom '" + atom.name + "'"
			continue
		ob.LocX = atom.x
		ob.LocY = atom.y
		ob.LocZ = atom.z
	traj_file.close()


class Atom:
	pass

