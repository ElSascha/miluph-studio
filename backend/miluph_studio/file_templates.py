from __future__ import annotations

from pathlib import Path
from typing import Any

DEFAULT_PARAMETER_H = """#ifndef _PARAMETER_H
#define _PARAMETER_H

// Dimension of the problem
#define DIM 3

// Physical model flags
#define SOLID 1
#define HYDRO 0
#define REAL_HYDRO 0
#define GRAVITATING_POINT_MASSES 0
#define PARTICLE_ACCRETION 0
#define UPDATE_SINK_VALUES 0
#define INTEGRATE_ENERGY 1
#define INTEGRATE_DENSITY 1
#define NAVIER_STOKES 0
#define SHAKURA_SUNYAEV_ALPHA 0
#define CONSTANT_KINEMATIC_VISCOSITY 0
#define KLEY_VISCOSITY 0
#define FRAGMENTATION 0
#define DAMAGE_ACTS_ON_S 0
#define ANEOS_VAPOR_NO_STRENGTH 0
#define SPH_EQU_VERSION 1
#define ARTIFICIAL_STRESS 0
#define ARTIFICIAL_VISCOSITY 1
#define BALSARA_SWITCH 0
#define INVISCID_SPH 0
#define SHEPARD_CORRECTION 0
#define TENSORIAL_CORRECTION 1
#define VON_MISES_PLASTICITY 0
#define DRUCKER_PRAGER_PLASTICITY 0
#define MOHR_COULOMB_PLASTICITY 0
#define COLLINS_PLASTICITY 0
#define COLLINS_PLASTICITY_INCLUDE_MELT_ENERGY 0
#define COLLINS_PLASTICITY_SIMPLE 1
#define LOW_DENSITY_WEAKENING 0
#define VISCOUS_REGOLITH 0
#define PURE_REGOLITH 0
#define JC_PLASTICITY 0
#define PALPHA_POROSITY 0
#define STRESS_PALPHA_POROSITY 0
#define SIRONO_POROSITY 0
#define EPSALPHA_POROSITY 0
#define MAX_NUM_FLAWS 1
#define MAX_NUM_INTERACTIONS 512
#define VARIABLE_SML 1
#define FIXED_NOI 0
#define INTEGRATE_SML 1
#define READ_INITIAL_SML_FROM_PARTICLE_FILE 0
#define SML_CORRECTION 0
#define AVERAGE_KERNELS 0
#define TOO_MANY_INTERACTIONS_KILL_PARTICLE 0
#define DEAL_WITH_TOO_MANY_INTERACTIONS 0
#define XSPH 0
#define BOUNDARY_PARTICLE_ID -1
#define GHOST_BOUNDARIES 0
#define HDF5IO 1
#define MORE_OUTPUT 1
#define MORE_ANEOS_OUTPUT 1
#define OUTPUT_GRAV_ENERGY 0
#define BINARY_INFO 0

#endif
"""

DEFAULT_MILUPHCUDA_CONFIG = {
    "simulation_name": "demo",
    "rho_0": 3000.0,
    "bulk_modulus": 1.0e10,
    "n": 1.0,
    "alpha": 1.0,
    "beta": 2.0,
    "c_gravity": 6.67408e-11,
}


def read_text_file(path: Path, default_content: str) -> str:
    if not path.exists():
        return default_content
    return path.read_text(encoding="utf-8")


def write_text_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _coerce_values(values: dict[str, Any]) -> dict[str, Any]:
    merged = dict(DEFAULT_MILUPHCUDA_CONFIG)
    merged.update(values)
    return merged


def write_parameter_header(path: Path, values: dict[str, Any]) -> str:
    resolved = _coerce_values(values)
    existing = path.read_text(encoding="utf-8") if path.exists() else DEFAULT_PARAMETER_H

    replacements = {
        "DIM": str(resolved.get("DIM", resolved.get("dim", 3))),
        "SOLID": str(resolved.get("SOLID", resolved.get("solid", 1))),
        "HYDRO": str(resolved.get("HYDRO", resolved.get("hydro", 0))),
        "REAL_HYDRO": str(resolved.get("REAL_HYDRO", resolved.get("real_hydro", 0))),
        "GRAVITATING_POINT_MASSES": str(resolved.get("GRAVITATING_POINT_MASSES", 0)),
        "PARTICLE_ACCRETION": str(resolved.get("PARTICLE_ACCRETION", 0)),
        "UPDATE_SINK_VALUES": str(resolved.get("UPDATE_SINK_VALUES", 0)),
        "INTEGRATE_ENERGY": str(resolved.get("INTEGRATE_ENERGY", resolved.get("integrate_energy", 1))),
        "INTEGRATE_DENSITY": str(resolved.get("INTEGRATE_DENSITY", resolved.get("integrate_density", 1))),
        "ARTIFICIAL_VISCOSITY": str(resolved.get("ARTIFICIAL_VISCOSITY", resolved.get("artificial_viscosity", 1))),
        "COLLINS_PLASTICITY_SIMPLE": str(resolved.get("COLLINS_PLASTICITY_SIMPLE", resolved.get("collins_plasticity_simple", 1))),
        "VARIABLE_SML": str(resolved.get("VARIABLE_SML", resolved.get("variable_sml", 1))),
        "FIXED_NOI": str(resolved.get("FIXED_NOI", resolved.get("fixed_noi", 0))),
        "INTEGRATE_SML": str(resolved.get("INTEGRATE_SML", resolved.get("integrate_sml", 1))),
        "HDF5IO": str(resolved.get("HDF5IO", resolved.get("hdf5io", 1))),
    }

    content = existing
    for name, replacement in replacements.items():
        content = __import__("re").sub(rf"^#define\s+{name}\s+.+$", f"#define {name} {replacement}", content, flags=__import__("re").MULTILINE)

    write_text_file(path, content)
    return content


def write_miluphcuda_config(path: Path, values: dict[str, Any]) -> str:
    resolved = _coerce_values(values)
    # Build a material.cfg-style config block. Keep formatting compatible with
    # existing fixtures (materials = ( { ... }, ... ); ). Produce one material
    # entry filled from resolved values and close the materials list properly.
    # Build extra EoS lines from any resolved keys not represented explicitly
    def _format_value(v: Any) -> str:
        if isinstance(v, bool):
            return '1' if v else '0'
        if isinstance(v, (int, float)):
            # preserve large floats in scientific notation when appropriate
            return f"{v:.6g}"
        # attempt numeric conversion for strings
        try:
            fv = float(str(v))
            return f"{fv:.6g}"
        except Exception:
            return f'"{str(v)}"'

    # keys already rendered at top-level or structural
    top_level_keys = {
        'simulation_name', 'rho_0', 'bulk_modulus', 'n', 'alpha', 'beta', 'c_gravity',
        'include', 'eos_type', 'shear_modulus', 'sml',
    }

    # whitelist of allowed EOS/porosity/plasticity parameter names we will write
    allowed_eos_keys = {
        'porjutzi_p_elastic', 'porjutzi_p_transition', 'porjutzi_p_compacted',
        'porjutzi_alpha_0', 'porjutzi_alpha_e', 'porjutzi_alpha_t',
        'porjutzi_n1', 'porjutzi_n2', 'cs_porous', 'crushcurve_style',
        'yield_stress', 'cohesion', 'friction_angle', 'friction_angle_damaged',
        'till_rho_0', 'till_A', 'till_B', 'till_E_0', 'till_a', 'till_b',
        'till_alpha', 'till_beta', 'till_E_iv', 'till_E_cv', 'rho_limit', 'cs_limit',
        'aneos_param',
    }

    eos_extra_lines = []
    for k, v in resolved.items():
        # skip top-level and internal keys
        if k in top_level_keys or k in ('instance_name',):
            continue
        if not isinstance(k, str):
            continue
        if k not in allowed_eos_keys:
            continue
        # skip structural-looking values
        if isinstance(v, str) and any(ch in v for ch in '{}()'):
            continue
        eos_extra_lines.append(f"        {k} = {_format_value(v)}")

    eos_extra = "\n".join(eos_extra_lines)

    content = """
global = {{
    c_gravity = {c_gravity}
}}

materials = (
{{
    ID = {id}
    name = "{simulation_name}"
    sml = {sml}
    interactions = {int}
    artificial_viscosity = {artificial_viscosity}
            eos = {{
        type = {eos_type}
        shear_modulus = {shear_modulus}
        bulk_modulus = {bulk_modulus}
        # include EoS params
        @include "{include_path}"
        rho_0 = {rho_0}
        # EoS / porosity / plasticity parameters (populated from payload)
    {eos_extra}
    }}

}}
);

""".format(
        id = resolved.get("ID", 0), # second value is default ID if not provided
        simulation_name=resolved.get("simulation_name", "none"),
        rho_0=resolved.get("rho_0", 0),
        bulk_modulus=resolved.get("bulk_modulus", 0),
        n=resolved.get("n", 1.0),
        alpha=resolved.get("alpha", 1.0),
        beta=resolved.get("beta", 2.0),
        c_gravity=resolved.get("c_gravity", 6.67408e-11),
        include_path=resolved.get("include", "material_data/basalt.till.cfg"),
        eos_type=resolved.get("eos_type", 1),
        shear_modulus=resolved.get("shear_modulus", 0),
        eos_extra=eos_extra,
        sml=resolved.get("sml", 1.0),
        int=resolved.get("interactions", 0),
        artificial_viscosity=resolved.get("artificial_viscosity", 1),
        porjutzi_p_elastic=resolved.get("porjutzi_p_elastic", 0),
        porjutzi_p_transition=resolved.get("porjutzi_p_transition", 0),
        porjutzi_p_compacted=resolved.get("porjutzi_p_compacted", 0),
        porjutzi_alpha_0=resolved.get("porjutzi_alpha_0", 0),
        porjutzi_alpha_e=resolved.get("porjutzi_alpha_e", 0),
        porjutzi_alpha_t=resolved.get("porjutzi_alpha_t", 0),
        porjutzi_n1=resolved.get("porjutzi_n1", 0),
        porjutzi_n2=resolved.get("porjutzi_n2", 0),
        cs_porous=resolved.get("cs_porous", 0),
        crushcurve_style=resolved.get("crushcurve_style", 0),
        yield_stress=resolved.get("yield_stress", 0),
        cohesion=resolved.get("cohesion", 0),
        friction_angle=resolved.get("friction_angle", 0),
        friction_angle_damaged=resolved.get("friction_angle_damaged", 0),
    )
    write_text_file(path, content)
    return content


def load_miluphcuda_config(path: Path, default_values: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists():
        return dict(default_values or DEFAULT_MILUPHCUDA_CONFIG)

    parsed: dict[str, Any] = {}
    defaults = dict(default_values or DEFAULT_MILUPHCUDA_CONFIG)
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("//", 1)[0].strip()
        if not line or line.startswith("#"):
            continue

        if ":" in line and "=" not in line:
            key, _, value = line.partition(":")
            raw = value.strip()
            if not key or not value:
                continue
            # ignore structural tokens
            if raw in ('{', '}', '(', ')'):
                continue
            if raw.replace('.', '', 1).isdigit():
                parsed[key.strip()] = float(raw) if '.' in raw else int(raw)
            else:
                parsed[key.strip()] = raw.strip('"')
            continue

        if "=" in line:
            key, _, value = line.partition("=")
            key = key.strip()
            raw = value.strip().rstrip(";")
            if not key or not raw:
                continue
            # ignore structural tokens like braces or parentheses
            if raw in ('{', '}', '(', ')'):
                continue
            if raw.startswith('"') and raw.endswith('"'):
                parsed[key] = raw[1:-1]
            elif raw.replace('.', '', 1).isdigit():
                parsed[key] = float(raw) if '.' in raw else int(raw)
            else:
                parsed[key] = raw

        if line.startswith("name") and "simulation_name" not in parsed:
            parsed["simulation_name"] = parsed.get("name", "")

    if "dt" in parsed:
        defaults["dt"] = parsed["dt"]
    if "t_end" in parsed:
        defaults["t_end"] = parsed["t_end"]
    if "nx" in parsed:
        defaults["nx"] = parsed["nx"]
    if "ny" in parsed:
        defaults["ny"] = parsed["ny"]
    if "nz" in parsed:
        defaults["nz"] = parsed["nz"]

    defaults.update(parsed)
    return defaults
