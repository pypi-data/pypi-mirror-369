r"""
This module defines constants, mostly wrapped from scipy. Many constants are in
the top-level namespace. Many more are in the dictionary ``physical_constants``
that can be searched using :meth:`find` and accessed using :meth:`value`.

On top of the scipy constants, the following shorthands are defined:

``e2`` : :math:`e^2`

``pi2`` : :math:`\pi/2`

``pi4`` : :math:`\pi/4`

``two_pi`` : :math:`2\pi`

``four_pi`` : :math:`4\pi`

"""

from typing import Union
import numpy as np
from scipy.constants import (
    Avogadro,
    Boltzmann,
    Btu,
    Btu_IT,
    Btu_th,
    G,
    Julian_year,
    N_A,
    Planck,
    R,
    Rydberg,
    Stefan_Boltzmann,
    Wien,
    acre,
    alpha,
    angstrom,
    arcmin,
    arcminute,
    arcsec,
    arcsecond,
    astronomical_unit,
    atm,
    atmosphere,
    atomic_mass,
    atto,
    au,
    bar,
    barrel,
    bbl,
    blob,
    c,
    calorie,
    calorie_IT,
    calorie_th,
    carat,
    centi,
    convert_temperature,
    day,
    deci,
    degree,
    degree_Fahrenheit,
    deka,
    dyn,
    dyne,
    e,
    eV,
    electron_mass,
    electron_volt,
    elementary_charge,
    epsilon_0,
    erg,
    exa,
    exbi,
    femto,
    fermi,
    find,
    fine_structure,
    fluid_ounce,
    fluid_ounce_US,
    fluid_ounce_imp,
    foot,
    g,
    gallon,
    gallon_US,
    gallon_imp,
    gas_constant,
    gibi,
    giga,
    golden,
    golden_ratio,
    grain,
    gram,
    gravitational_constant,
    h,
    hbar,
    hectare,
    hecto,
    horsepower,
    hour,
    hp,
    inch,
    k,
    kgf,
    kibi,
    kilo,
    kilogram_force,
    kmh,
    knot,
    lambda2nu,
    lb,
    lbf,
    light_year,
    liter,
    litre,
    long_ton,
    m_e,
    m_n,
    m_p,
    m_u,
    mach,
    mebi,
    mega,
    metric_ton,
    micro,
    micron,
    mil,
    mile,
    milli,
    minute,
    mmHg,
    mph,
    mu_0,
    nano,
    nautical_mile,
    neutron_mass,
    nu2lambda,
    ounce,
    oz,
    parsec,
    pebi,
    peta,
    physical_constants,
    pi,
    pico,
    point,
    pound,
    pound_force,
    precision,
    proton_mass,
    psi,
    pt,
    short_ton,
    sigma,
    slinch,
    slug,
    speed_of_light,
    speed_of_sound,
    stone,
    survey_foot,
    survey_mile,
    tebi,
    tera,
    ton_TNT,
    torr,
    troy_ounce,
    troy_pound,
    u,
    unit,
    value,
    week,
    yard,
    year,
    yobi,
    yotta,
    zebi,
    zepto,
    zero_Celsius,
    zetta
)

e2 = e**2
pi2 = pi/2
pi4 = pi/4
two_pi = pi*2
four_pi = pi*4


def convert_attenuation(val: float, old_scale: str, new_scale: str) -> float:
    """Convert between different units of attenuation.

    Parameters
    ----------
    val: float
        Value to be converted.
    old_scale: str
        dB, field, or power.
    new_scale: str
        dB, field, or power.

    Returns
    -------
    The converted values.

    """

    if old_scale.lower() == 'db':
        atten = np.asanyarray(val)
    elif old_scale.lower() in ['field', 'f']:
        atten = 20*np.log10(np.asanyarray(val))
    elif old_scale.lower() in ['power', 'p']:
        atten = 10*np.log10(np.asanyarray(val))

    if new_scale.lower() == 'db':
        res = atten
    elif new_scale.lower() in ['field', 'f']:
        res = 10**(atten / 20)
    elif new_scale.lower() in ['power', 'p']:
        res = 10**(atten / 10)

    if res.ndim == 0:
        return float(res)

    return res


def convert_power(val: float, old_scale: str, new_scale: str) -> float:
    """Convert between different units of power.

    Parameters
    ----------
    val: float
        Value to be converted.
    old_scale: str
        dBm, watt, Vpp, or Vrms.
    new_scale: str
        dBm, watt, Vpp, or Vrms.

    Returns
    -------
    The converted values.

    """

    if old_scale.lower() == 'dbm':
        power = np.asanyarray(val)
    elif old_scale.lower() in ['watt', 'w']:
        power = 10 + 20*np.log10(np.sqrt(np.asanyarray(val)*100));
    elif old_scale.lower() == 'vpp':
        power = 10 + 20*np.log10(np.asanyarray(val)/2);
    elif old_scale.lower() == 'vrms':
        power = 10 + 20*np.log10(np.asanyarray(val)*np.sqrt(2))

    if new_scale.lower() == 'dbm':
        res = power
    elif new_scale.lower() in ['watt', 'w']:
        res = 10**((power - 10) / 20)**2 / 100;
    elif new_scale.lower() == 'vpp':
        res = 2 * 10**((power - 10) / 20)
    elif new_scale.lower() == 'vrms':
        res = 10**((power - 10) / 20) / np.sqrt(2);

    if res.ndim == 0:
        return float(res)

    return res


def lambda2eV(lambda_: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """Convert wavelength to eV.

    Parameters
    ----------
    lambda_: Union[float, np.ndarray]
        Wavelength in meters.

    Returns
    -------
    eV: Union[float, np.ndarray]
        Energy in eV.

    """
    return lambda2nu(lambda_)*h/e


def eV2lambda(eV: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """Convert eV to wavelength.

    Parameters
    ----------
    eV: Union[float, np.ndarray]
        Energy in eV.

    Returns
    -------
    lambda: Union[float, np.ndarray]
        Wavelength in meters.

    """
    return nu2lambda(e/h*eV)
