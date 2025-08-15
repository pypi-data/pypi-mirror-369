# %%
import re
from pathlib import Path
from typing import Optional

from numpy import ndarray

from .. import base
from .. import prop
from ..extra import ndarrayconvert


# %%
def bada3_aircraft(ac: str, bada_path: str):
    """Update aircraft with BADA3 data.

    Args:
        ac (str): Aircraft identifier (e.g. "A320")
        bada_path (str): Path to the BADA3 data folder.

    Returns:
        dict: Dictionary with aircraft performance data from aircraft yaml file
            as well as from BADA3.
    """

    def deep_update(target: dict, updates: dict):
        # recursively update values in target dictionary
        for key, value in updates.items():
            if (
                key in target
                and isinstance(target[key], dict)
                and isinstance(value, dict)
            ):
                deep_update(target[key], value)
            else:
                target[key] = value

    aircraft = prop.aircraft(ac)
    deep_update(aircraft, load_bada3(ac, bada_path))
    return aircraft


def load_bada3(ac: str, bada_path: str):
    """
    Load BADA3 aircraft performance data by first resolving the synonym
    and then parsing the associated .OPF file.

    Args:
        ac (str): Aircraft identifier (e.g. "A320").
        bada_path (str): Path to the BADA3 data folder.

    Raises:
        FileNotFoundError: If the OPF file corresponding to the synonym
            cannot be found.
        ValueError: If the aircraft code is not found in the SYNONYM file.

    Returns:
        dict: Dictionary with full aircraft performance data including
            aerodynamic coefficients, thrust/fuel parameters, and metadata.
    """
    synonym_data = read_synonym(ac, bada_path)
    synonym = synonym_data["synonym"]
    file = Path(bada_path) / f"{synonym}__.OPF"

    if not file.exists():
        raise FileNotFoundError(f"OPF file not found: {file}")

    with file.open("r", encoding="utf-8") as f:
        content = f.read()

    opf_data = parse_opf_content(content)
    return {
        "typecode": ac,
        **synonym_data,
        **opf_data,
    }


def read_synonym(ac: str, bada_path: str, synonym_file: str = "SYNONYM.NEW"):
    """
    Parse the BADA3 SYNONYM.NEW file to find manufacturer, model and synonym
    information for aircraft identifier "ac".

    Args:
        ac (str): Aircraft identifier (e.g. "A320")
        bada_path (str): Path to BADA3 folder.
        synonym_file (str, optional): Name of the SYNONYM file.
            Defaults to "SYNONYM.NEW".

    Raises:
        FileNotFoundError: If the SYNONYM file is not found.
        ValueError: If the aircraft code is not found in the file.

    Returns:
        dict: Dictionary with keys 'manufacturer', 'model', and 'synonym'.
    """

    file = Path(bada_path) / synonym_file

    if not file.exists():
        raise FileNotFoundError(f"SYNONYM file not found at: {file}")

    pattern = re.compile(
        r"^CD\s+[^\s]\s+(\S+)\s+"  # A/C code
        r"(\S(?:.*?\S)?)\s{2,}"  # Manufacturer
        r"(.+?)\s{2,}"  # Model
        r"(\S+)\s+.*?/$"  # Synonym
    )

    with open(file, "r", encoding="utf-8") as f:
        for line in f:
            match = pattern.match(line)
            if match:
                code, manufacturer, model, synonym = match.groups()
                if code.upper() == ac.upper():
                    return {
                        "aircraft": f"{manufacturer.strip()} {model.strip()}",
                        "manufacturer": manufacturer.strip(),
                        "model": model.strip(),
                        "synonym": synonym.strip()[:4],
                    }

    raise ValueError(f"Aircraft code '{ac}' not found in SYNONYM file.")


def parse_opf_content(content: str):
    """
    Parse the contents of a BADA3 .OPF file and extract aircraft performance
    parameters.

    Args:
        content (str): Raw text content of the .OPF file.

    Returns:
        dict: Dictionary containing parsed aerodynamic and engine parameters,
            including CD0/CD2 by phase, thrust coefficients, fuel flow
            coefficients, wing area, engine type, and others.
    """

    def get_drag_coeff(phase):
        # get drag coefficients
        pattern = (
            rf"CD\s+\d+\s+{phase}\s+\S+\s+[\d.E+-]+\s+" r"([\d.E+-]+)\s+([\d.E+-]+)"
        )
        m = re.search(pattern, content)
        return (float(m.group(1)), float(m.group(2))) if m else (0.0, 0.0)

    def get_floats(pattern, count, default=0.0):
        # get a certain number of floats from a regex pattern
        m = re.search(pattern, content, re.DOTALL)
        return (
            [float(m.group(i)) for i in range(1, count + 1)] if m else [default] * count
        )

    # actype
    engine_type = "turbofan"
    num_engines = None  # or default like 0
    m_actype = re.search(r"Actype[\s\S]*?^CD\s+.*$", content, re.MULTILINE)
    if m_actype:
        cd_line = m_actype.group(0)

        # Engine type
        if re.search(r"Turboprop", cd_line, re.IGNORECASE):
            engine_type = "turboprop"
        elif re.search(r"Jet", cd_line, re.IGNORECASE):
            engine_type = "turbofan"
        elif re.search(r"Piston", cd_line, re.IGNORECASE):
            engine_type = "piston"
        elif re.search(r"Electric", cd_line, re.IGNORECASE):
            engine_type = "electric"

        # Number of engines
        m_engines = re.search(r"(\d+)\s+engines?", cd_line, re.IGNORECASE)
        if m_engines:
            num_engines = int(m_engines.group(1))

    # aircraft mass
    mass_vals = get_floats(
        r"Mass \(t\).*?CD\s+([\d.E+-]+)\s+([\d.E+-]+)\s+([\d.E+-]+)"
        r"\s+([\d.E+-]+)\s+[\d.E+-]+",
        4,
    )

    # flight envelope
    envelope_vals = get_floats(
        r"Flight envelope.*?CD\s+([\d.E+-]+)\s+([\d.E+-]+)\s+([\d.E+-]+)"
        r"\s+[\d.E+-]+\s+[\d.E+-]+",
        3,
    )

    # wing area
    wing_area = get_floats(r"Wing Area.*?CD \d+\s+([\d.E+-]+)", 1)[0]

    # Drag coefficients
    cd0_cr, cd2_cr = get_drag_coeff("CR")
    cd0_ic, cd2_ic = get_drag_coeff("IC")
    cd0_to, cd2_to = get_drag_coeff("TO")
    cd0_ap, cd2_ap = get_drag_coeff("AP")
    cd0_ld, cd2_ld = get_drag_coeff("LD")

    # Landing gear
    cd0_lgear = get_floats(r"CD \d+\s+DOWN\s+([\d.E+-]+)", 1)[0]

    # Thrust coefficients
    ct = get_floats(
        r"Max climb thrust coefficients.*?CD\s+([\d.E+-]+)\s+([\d.E+-]+)"
        r"\s+([\d.E+-]+)\s+([\d.E+-]+)\s+([\d.E+-]+)",
        5,
    )
    ctdes = get_floats(
        r"Desc\(low\).*?CD\s+([\d.E+-]+)\s+([\d.E+-]+)"
        r"\s+([\d.E+-]+)\s+([\d.E+-]+)\s+([\d.E+-]+)",
        5,
    )

    # Fuel coefficients
    cf = get_floats(
        r"Thrust Specific Fuel Consumption Coefficients.*?CD\s+([\d.E+-]+)"
        r"\s+([\d.E+-]+)",
        2,
    )
    cfdes = get_floats(
        r"Descent Fuel Flow Coefficients.*?CD\s+([\d.E+-]+)\s+([\d.E+-]+)", 2
    )
    cfcr = get_floats(r"Cruise Corr.*?CD\s+([\d.E+-]+)", 1, default=1.0)[0]

    # Altitude for hpdes (from Desc level)
    hpdes = get_floats(
        r"Desc level.*?CD\s+[\d.E+-]+\s+[\d.E+-]+\s+([\d.E+-]+)",
        1,
        default=8000.0,
    )[0]

    ground_vals = get_floats(
        r"Ground.*?CD\s+([\d.E+-]+)\s+([\d.E+-]+)\s+([\d.E+-]+)"
        r"\s+([\d.E+-]+)\s+[\d.E+-]+",
        4,
    )

    # return as openap aircraft style dictionary
    return {
        "mtow": mass_vals[2] * 1e3,  # convert to kg
        "mref": mass_vals[0] * 1e3,
        "oew": mass_vals[1] * 1e3,
        "mpl": mass_vals[3] * 1e3,
        "vmo": envelope_vals[0],  # kt
        "mmo": envelope_vals[1],
        "ceiling": envelope_vals[2] * 0.3048,  # convert to m
        "fuselage": {
            "length": ground_vals[3],
        },
        "wing": {
            "area": wing_area,
            "span": ground_vals[2],
        },
        "engine": {
            "type": engine_type,
            "number": num_engines,
        },
        "CD0": {"CR": cd0_cr, "IC": cd0_ic, "TO": cd0_to, "AP": cd0_ap, "LD": cd0_ld},
        "CD2": {"CR": cd2_cr, "IC": cd2_ic, "TO": cd2_to, "AP": cd2_ap, "LD": cd2_ld},
        "CD0_lgear": cd0_lgear,
        "Ct": ct,
        "CTdeshigh": ctdes[1],
        "CTdeslow": ctdes[0],
        "CTdesapp": ctdes[3],
        "CTdesld": ctdes[4],
        "HpDes": hpdes,
        "Cf": cf,
        "CfDes": cfdes,
        "CfCrz": cfcr,
    }


# %%
class Drag(base.DragBase):
    """
    Compute the drag of an aircraft using BADA3 models.

    Attributes:
        ac (str): aircraft ICAO identifer (e.g. A320)
        S (float): wing surface area [m^2]
        cd0_cr (float): parasitic drag coefficient (cruise)
        cd2_cr (float): induced drag coefficient (cruise)
        cd0_ap (float): parasitic drag coefficient (approach)
        cd2_ap (float): induced drag coefficient (approach)
        cd0_ld (float): parasitic drag coefficient (landing)
        cd2_ld (float): induced drag coefficient (landing)
        cd0_lgear (float): parasitic drag coefficient of extended landing gear

    Methods:
        _cd(cl, cd0, cd2, cd0_lg=0.0):
            Compute the drag coefficient for a given lift coefficient.

        _cl(mass, tas, alt):
            Compute the lift coefficient for a given aircraft mass, true
            airspeed (TAS), altitude and vertical speed.

        clean(mass, tas, alt, vs=None):
            Compute the total drag (N) for the aircraft in clean configuration.

        nonclean(self, mass, tas, alt, flap_angle=None, vs=None,
            landing_gear=False, phase=None):
            Compute the total drag (N) for the aircraft in non-clean
            configuration.
    """

    def __init__(self, ac: str, bada_path: str, model=None, **kwargs):
        super().__init__(ac, **kwargs)
        self.ac = ac.upper()
        if not model:
            model = load_bada3(ac, bada_path)
        self.S = model["wing"]["area"]
        self.cd0_cr = model["CD0"]["CR"]
        self.cd2_cr = model["CD2"]["CR"]
        self.cd0_ap = model["CD0"]["AP"]
        self.cd2_ap = model["CD2"]["AP"]
        self.cd0_ld = model["CD0"]["LD"]
        self.cd2_ld = model["CD2"]["LD"]
        self.cd0_lgear = model["CD0_lgear"]

    @ndarrayconvert(column=True)
    def _cd(self, cl, cd0, cd2, cd0_lg=0.0):
        """
        Compute drag coefficient.
        BADA3 eq. (3.6-2, 3.6-3, 3.6-4)

        Args:
            cl (float | ndarray): lift coefficient [-]
            cd0 (float | ndarray): parasitic drag coefficient
            cd2 (float | ndarray): induced drag coefficient
            cd0_lg (float | ndarray): parasitic drag coefficient of landing gear

        Returns:
            float | ndarray: drag coefficient [-]
        """
        cd = cd0 + cd0_lg + cd2 * cl**2
        return cd

    @ndarrayconvert(column=True)
    def _cl(self, mass, tas, alt):
        """
        Compute lift coefficient.
        BADA3 eq. (3.6-1)

        Args:
            mass (float | ndarray): mass of the aircraft [kg].
            tas (float | ndarray): true airspeed [kt].
            alt (float | ndarray): geopotential pressure altitude [ft].

        Returns:
            tuple of float | ndarray: (lift coefficient [-], q * S)
        """
        v = tas * self.aero.kts
        h = alt * self.aero.ft
        rho = self.aero.density(h)

        # calculate total lift
        qS = 0.5 * rho * v**2 * self.S
        L = mass * self.aero.g0
        cl = L / self.sci.maximum(qS, 1e-3)  # avoid zero division

        return cl, qS

    @ndarrayconvert(column=True)
    def clean(self, mass, tas, alt, vs=None) -> float | ndarray:
        """
        Compute drag in clean configuration.
        BADA3 eq. (3.6-5)

        Args:
            mass (float | ndarray): mass of the aircraft [kg].
            tas (float | ndarray): true airspeed [kt].
            alt (float | ndarray): geopotential pressure altitude [ft].
            vs: unused

        Returns:
            float | ndarray: Total drag in clean configuration (N).
        """
        cl, qS = self._cl(mass, tas, alt)
        cd = self._cd(cl, self.cd0_cr, self.cd2_cr)
        D = cd * qS
        return D

    @ndarrayconvert(column=True)
    def nonclean(self, mass, tas, alt, landing_gear=False, phase=None):
        """
        Compute drag in non-clean configuration (approach and landing phases).
        BADA3 eq. (3.6-3, 3-6-4, 3.6-5)

        Args:
            mass (float | ndarray): mass of the aircraft [kg].
            tas (float | ndarray): true airspeed [kt].
            alt (float | ndarray): geopotential pressure altitude [ft].
            flap_angle: unused
            vs: unused
            landing_gear (bool): boolean of whether landing gear extended
            phase (str): flight phase, one of AP or LD allowed

        Returns:
            float | ndarray: Total drag in non-clean configuration (N).
        """
        # ensure that the phase is one of AP or LD
        if phase not in ("AP", "LD"):
            raise ValueError(f"Phase {phase} unknown or not applicable.")
        cl, qS = self._cl(mass, tas, alt)
        if phase == "AP":
            # if both cd0 and cd2 of approach are zero, use clean config
            if self.cd0_ap == 0.0 and self.cd2_ap == 0.0:
                cd = self._cd(cl, self.cd0_cr, self.cd2_cr)
            else:
                cd = self._cd(cl, self.cd0_ap, self.cd2_ap)
        else:  # landing phase
            if self.cd0_ld == 0.0 and self.cd2_ld == 0.0:
                cd = self._cd(cl, self.cd0_cr, self.cd2_cr)
            else:
                cd = self._cd(
                    cl,
                    self.cd0_ld,
                    self.cd2_ld,
                    self.cd0_lgear if landing_gear else 0.0,
                )
        D = cd * qS
        return D


class Thrust(base.ThrustBase):
    """
    Thrust class for computing the thrust of an aircraft using BADA3 models.

    This class provides methods to compute thrust during the flight phases
    takeoff, climb and cruise.

    Attributes:
        ac (str): aircraft ICAO identifer (e.g. A320)
        engine_type (str): one of turbofan, turboprop, piston or electric
        ct (list): list of thrust-related coefficients from BADA3
        hpdes (float): design geopotential pressure altitude [ft]
        ctdes* (float): (high, low, app, ld) thrust-related coefficients for
            descent/idle conditions

    Methods:
        climb(tas, alt, dT=0):
            Compute the thrust force during the climb phase.

        cruise(tas, alt, roc=None, dT=0):
            Compute the thrust force during the cruise phase.

        takeoff(tas, alt, dT=0):
            Compute the thrust force during the takeoff phase.

        idle(tas, alt, roc=None, dT=0, config=None):
            Compute the thrust force during idle conditions.
    """

    def __init__(self, ac: str, bada_path: str, model=None, **kwargs):
        super().__init__(ac, **kwargs)
        self.ac = ac.upper()
        if not model:
            model = load_bada3(ac, bada_path)
        self.engine_type = model["engine"]["type"]
        self.ct = model["Ct"]
        self.ctdeshigh = model["CTdeshigh"]
        self.ctdeslow = model["CTdeslow"]
        self.ctdesapp = model["CTdesapp"]
        self.ctdesld = model["CTdesld"]

        nc_vals = [
            model["CD0"]["AP"],
            model["CD0"]["LD"],
            model["CD0_lgear"],
            model["CD2"]["AP"],
            model["CD2"]["LD"],
        ]
        nc_avail = all(val == 0 for val in nc_vals)
        if nc_avail:
            self.hpdes = self.sci.maximum(model["HpDes"], 8000.0)
        else:
            self.hpdes = model["HpDes"]

    @ndarrayconvert(column=True)
    def climb(self, tas, alt, dT=0) -> float | ndarray:
        """
        Compute the maximum climb thrust.
        BADA3 eq. (3.7-1 to 3.7-7)

        Args:
            tas (float | ndarray): true airspeed [kt]
            alt (float | ndarray): geopotential pressure altitude [ft]
            dT (float | ndarray, optional): ISA temperature deviation [K].
                Defaults to 0.0 K.

        Returns:
            float | ndarray: Thrust force (N) during the climb phase.
        """

        # calculate maximum climb thrust at ISA
        if self.engine_type == "turbofan":
            thr_isa = self.ct[0] * (1 - alt / self.ct[1] + self.ct[2] * alt**2)
        elif self.engine_type == "turboprop":
            thr_isa = self.ct[0] / tas * (1 - alt / self.ct[1]) + self.ct[2]
        elif self.engine_type in ("piston", "electric"):
            thr_isa = self.ct[0] * (1 - alt / self.ct[1]) + self.ct[2] / tas
        else:
            raise ValueError("Unknown engine type")

        # correct for temperature deviations from ISA whilst considering limits
        # eq. (3.7.4 - 3.7.7)
        dT_eff = dT - self.ct[3]
        c_tc5 = self.sci.maximum(self.ct[4], 0.0)
        dT_lim = self.sci.maximum(0.0, self.sci.minimum(c_tc5 * dT_eff, 0.4))
        thr_mcl = thr_isa * (1 - dT_lim)
        return thr_mcl

    @ndarrayconvert(column=True)
    def cruise(self, tas, alt, roc=None, dT=0) -> float | ndarray:
        """
        Compute the maximum cruise thrust.
        BADA3 eq. (3.7-8)

        Args:
            tas (float | ndarray): true airspeed [kt]
            alt (float | ndarray): geopotential pressure altitude [ft]
            roc: unused
            dT (float | ndarray, optional): ISA temperature deviation [K].
                Defaults to 0.0 K.

        Returns:
            float | ndarray: Thrust force (N) during the cruise phase.
        """
        ct_cr = 0.95  # constant in BADA3
        thr_cl_max = self.climb(tas, alt, dT)
        thr_cr_max = ct_cr * thr_cl_max
        return thr_cr_max

    @ndarrayconvert(column=True)
    def takeoff(self, tas, alt, dT=0) -> float | ndarray:
        """
        Compute takeoff thrust, which is assumed by BADA3 to be equal to
        maximum climb thrust.

        Args:
            tas (float | ndarray): true airspeed [kt]
            alt (float | ndarray): geopotential pressure altitude [ft]
            dT (float | ndarray, optional): ISA temperature deviation [K].
                Defaults to 0.0 K.

        Returns:
            float | ndarray: Thrust force (N) during the cruise phase.
        """
        return self.climb(tas, alt, dT)

    @ndarrayconvert(column=True)
    def idle(self, tas, alt, roc=None, dT=0, config=None) -> float | ndarray:
        """
        Compute idle (descent) thrust in various configurations.
        BADA3 eq. (3.7-9 to 3.7-12)

        Args:
            tas (float | ndarray): true airspeed [kt]
            alt (float | ndarray): geopotential pressure altitude [ft]
            roc: unused.
            dT (float | ndarray, optional): ISA temperature deviation [K].
                Defaults to 0.0 K.
            config (str): Aircraft configuration, choice of CR, AP or LD

        Returns:
            float | ndarray: Thrust force (N) during idle/descent.
        """
        thr_cl_max = self.climb(tas, alt, dT)
        if config not in ("CR", "AP", "LD"):
            raise ValueError("Config unknown.")
        if alt > self.hpdes:
            thr_des = self.ctdeshigh * thr_cl_max
        else:
            if config == "CR":
                ctdes = self.ctdeslow
            elif config == "AP":
                ctdes = self.ctdesapp
            else:
                ctdes = self.ctdesld
            thr_des = ctdes * thr_cl_max
        return thr_des


class FuelFlow(base.FuelFlowBase):
    """
    FuelFlow class to compute the fuel flow [kg/s] of an aircraft using BADA3
    models.

    Attributes:
        ac (str): aircraft ICAO identifier (e.g. A320)
        engine_type (str): one of turbofan, turboprop, piston or electric
        cf1 (float): 1st thrust specific fuel consumption coefficient
        cf2 (float): 2nd thrust specific fuel consumption coefficient
        cf3 (float): 1st descent fuel flow coefficient
        cf4 (float): 2nd descent fuel flow coefficient
        cfcr (float): cruise fuel flow correction coefficient

    Methods:
        nominal(mass, tas, alt, vs=0):
            Compute the fuel flow [kg/s] in all conditions except idle descent
            and cruise.

        enroute(mass, tas, alt, vs=0, acc=None):
            Compute the fuel flow [kg/s] in cruise.

        idle(mass, tas, alt, vs=None):
            Compute the fuel flow [kg/s] in idle conditions.

        approach(mass, tas, alt, vs=0):
            Compute the fuel flow [kg/s] in approach.
    """

    def __init__(self, ac: str, bada_path: Optional[str] = None, model=None, **kwargs):
        super().__init__(ac, **kwargs)
        self.ac = ac.upper()
        if not model:
            model = load_bada3(ac, bada_path)
        self.thrust = Thrust(ac, bada_path, model=model)
        self.drag = Drag(ac, bada_path, model=model)
        # load parameters from BADA3
        self.engine_type = model["engine"]["type"]
        self.cf1 = model["Cf"][0]
        self.cf2 = model["Cf"][1]
        self.cf3 = model["CfDes"][0]
        self.cf4 = model["CfDes"][1]
        self.cfcr = model["CfCrz"]

    @ndarrayconvert(column=True)
    def nominal(self, mass, tas, alt, vs=0) -> float | ndarray:
        """Calculate the nominal fuel flow.
        BADA3 eq. (3.9-1, 3.9-2, 3.9-3)

        Args:
            mass (float | ndarray): mass of the aircraft [kg].
            tas (float | ndarray): true airspeed [kt].
            alt (float | ndarray): geopotential pressure altitude [ft].
            vs (float): vertical rate [ft/min]. Default: 0.

        Returns:
            float | ndarray: Nominal fuel flow [kg/s]
        """
        # calculate gamma angle and drag
        v = tas * self.aero.kts
        gamma = self.sci.arctan2(vs * self.aero.fpm, v)
        D = self.drag.clean(mass, tas, alt, vs)

        # thrust is equal to drag, but not larger than climb thrust
        T = self.sci.minimum(
            D + mass * self.aero.g0 * self.sci.sin(gamma), self.thrust.climb(tas, alt)
        )

        # calculate nominal fuel flow depending on engine_type
        if self.engine_type == "turbofan":
            eta = self.cf1 * (1 + tas / self.cf2) * 1e-3
            f_nom = eta * T
        elif self.engine_type == "turboprop":
            eta = self.cf1 * (1 - tas / self.cf2) * (tas / 1e3) * 1e-3
            f_nom = eta * T
        elif self.engine_type in ("piston", "electric"):
            f_nom = self.cf1
        else:
            raise ValueError("Unknown engine type.")

        # nominal must be at least idle
        f_nom = self.sci.maximum(f_nom, self.idle(mass, tas, alt, vs))
        return f_nom / 60.0  # conversion [kg/min] -> [kg/s]

    @ndarrayconvert(column=True)
    def enroute(self, mass, tas, alt, vs=0, acc=None):
        """Calculate the cruise (clean) fuel flow.
        BADA3 eq. (3.9-6)

        Args:
            mass (float | ndarray): mass of the aircraft [kg].
            tas (float | ndarray): true airspeed [kt].
            alt (float | ndarray): geopotential pressure altitude [ft].
            vs (float): vertical rate [ft/min]. Default: 0.
            acc: unused.

        Returns:
            float | ndarray: Cruise fuel flow [kg/s]
        """
        f_nom = self.nominal(mass, tas, alt, vs)  # [kg/s]
        return self.cfcr * f_nom

    @ndarrayconvert(column=True)
    def idle(self, mass, tas, alt, vs=None):
        """Calculate idle fuel flow.
        BADA3 eq. (3.9-4)

        Args:
            mass: unused
            tas: unused
            alt (float | ndarray): geopotential pressure altitude [ft].
            vs: unused

        Returns:
            float | ndarray: Idle fuel flow [kg/s]
        """
        if self.engine_type in ("turbofan", "turboprop"):
            f_min = self.cf3 * (1 - alt / self.cf4)
        elif self.engine_type in ("piston", "electric"):
            f_min = self.cf3
        else:
            raise ValueError("Unknown engine type.")
        return f_min / 60.0  # conversion [kg/min] -> [kg/s]

    @ndarrayconvert(column=True)
    def approach(self, mass, tas, alt, vs=0):
        """Calculate approach and landing fuel flow. Only applicable to
        jet and turboprop aircraft.
        BADA3  eq. (3.9-5)

        Args:
            mass (float | ndarray): mass of the aircraft [kg].
            tas (float | ndarray): true airspeed [kt].
            alt (float | ndarray): geopotential pressure altitude [ft].
            vs (float): vertical rate [ft/min]. Default: 0.

        Returns:
            float | ndarray: Approach/landing fuel flow [kg/s]
        """
        if self.engine_type not in ("turbofan", "turboprop"):
            raise ValueError(
                f"Engine type {self.engine_type} unknown or not applicable."
            )
        f_nom = self.nominal(mass, tas, alt, vs)  # [kg/s]
        f_min = self.idle(mass, tas, alt, vs)  # [kg/s]
        f_ap = self.sci.maximum(f_nom, f_min)
        return f_ap
