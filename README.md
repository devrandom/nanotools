Instructions:
=============

* Copy proteindb.py to ~/.blender/scripts
* Create a directory for per-frame pdb files and name it the same as the structure (e.g. "c60")
* Each per-frame pdb file should be named with the frame number and ".pdb" extension. e.g. "1.pdb" through "999.pdb" and placed in the "c60" directory
* Run the script, choose your structure file (e.g. "c60.pdb")
* Advancing the frames will animate the structure
* To create the pdb frames from GROMACS, use the trjconv program:

         trjconv -s <structure> -f traj.trr -o .pdb -sep


