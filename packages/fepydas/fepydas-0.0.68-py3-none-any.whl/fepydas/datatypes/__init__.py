from fepydas.datatypes.Data import DataType, Unit
import sympy.physics.units as u

class RamanUnit(Unit):
    def __init__(self):
        super().__init__(u.planck * u.c / u.cm)
        
    def __str__(self):
        return("cm^-1")

WL_nm = DataType("Wavelength",Unit(u.nm))
RS_cm = DataType("Raman Shift",RamanUnit())
COUNTS = DataType("Counts","#")
TIME_s = DataType("Time",Unit(u.s))
TIME_ns = DataType("Time",Unit(u.ns))
TIME_ps = DataType("Time",Unit(u.ps))
E_eV = DataType("Energy",Unit(u.eV))
ANGLE_au = DataType("Angle",Unit(u.degree))
NUMBER = DataType("Number","#")
I_mA = DataType("Current",Unit(u.milli*u.A))
P_mW = DataType("Power",Unit(u.milli*u.W))
POS_um = DataType("Position",Unit(u.micrometer))
POS_mm = DataType("Position",Unit(u.milli*u.m))
TEMP_K = DataType("Temperature",Unit(u.K))

prefix_map = {
    'Y': u.yotta, 'Z': u.zetta, 'E': u.exa, 'P': u.peta, 'T': u.tera,
    'G': u.giga, 'M': u.mega, 'k': u.kilo, 'h': u.hecto, 
    'd': u.deci, 'c': u.centi, 'm': u.milli, 'μ': u.micro, 'n': u.nano,
    'p': u.pico, 'f': u.femto, 'a': u.atto, 'z': u.zepto, 'y': u.yocto
}

def unitFromAbbrev(abbrev):
    """
    Attempts to find the sympy unit for the given string, i.e. "mA" => u.milli*u.ampere

    Args
        abbrev: the text to parse
    Returns
        a sympy expression or (if it failed) the argument as string
    """
    # If it's empty, return "#"
    if len(abbrev) == 0:
        return "#"
    # Find longest matching prefix (up to 2 characters for 'da', 'μ' etc.)
    for prefix_len in [2, 1]:
        if len(abbrev) >= prefix_len:
            prefix_str = abbrev[:prefix_len]
            if prefix_str in prefix_map:
                prefix = prefix_map[prefix_str]
                base_str = abbrev[prefix_len:]
                break
    else:
        prefix = 1  # No prefix
        base_str = abbrev

    # Get base unit from SymPy's predefined units
    base_unit = getattr(u, base_str, None)
    if not isinstance(base_unit, u.Quantity):
        print (f"Unknown base unit: {base_str} ({abbrev})")
        return abbrev

    return Unit(prefix * base_unit)   

def generateDataType(name,unit):
    """
    Constructs a DataType
    """
    return DataType(name,unitFromAbbrev(unit))