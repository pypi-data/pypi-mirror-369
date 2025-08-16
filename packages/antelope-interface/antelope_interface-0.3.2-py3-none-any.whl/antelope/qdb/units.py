"""
this belongs in the implementation, not the interface
"""

from pint import UnitRegistry


U = UnitRegistry()


comp_units = {
    'm3': U.meter ** 3,
    'm2a': U.meter ** 2 * U.year,
    'tkm': U.tonne * U.kilometer,
}
