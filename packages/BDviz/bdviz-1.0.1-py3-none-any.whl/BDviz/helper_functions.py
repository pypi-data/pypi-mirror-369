'''
This module defines some helper functions for ``BrownDwarf`` objects
'''

from astropy.coordinates import SkyCoord
import astropy.units as u


def get_angular_separation(object1, object2):
	'''Angular Separation 
	Calulates the angular separation between
	two objects in the scene

	Args:
	object1 (object): Brown Dwarf object
	object2 (object): Brown Dwarf object

	Returns:
		astropy.coordinates.Angle: separation of objects in degrees
	'''

	return object1.pos.separation(object2.pos).to(u.deg)


def get_physical_separation(object1, object2):
	'''Physical Separation
	Calulates the 3D distance between 
	two objects in the scene

	Args:
	object1 (object): Brown Dwarf object
	object2 (object): Brown Dwarf object

	Returns:
		astropy.coordinates.Distance: distance of objects in parsecs
	'''

	return object1.pos.separation_3d(object2.pos)