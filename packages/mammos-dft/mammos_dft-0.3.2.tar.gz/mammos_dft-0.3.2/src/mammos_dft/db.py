"""Functions for reading tables."""

import pathlib
import shutil
from textwrap import dedent

import mammos_entity as me
import mammos_units as u
import pandas as pd
from pydantic import ConfigDict
from pydantic.dataclasses import dataclass
from rich import print

DATA_DIR = pathlib.Path(__file__).parent / "data"


def _check_short_label(short_label: str) -> tuple[str, int]:
    """Check that short label follows the standards and returns material parameters.

    Args:
        short_label: Short label containing chemical formula and space group
            number separated by a hyphen.

    Returns:
        Chemical formula and space group number.

    Raises:
        ValueError: Wrong format.

    """
    short_label_list = short_label.split("-")
    if len(short_label_list) != 2:
        raise ValueError(
            dedent(
                """
                Wrong format for `short_label`.
                Please use the format <chemical_formula>-<space_group_number>.
                """
            )
        )
    chemical_formula = short_label_list[0]
    space_group_number = int(short_label_list[1])
    return chemical_formula, space_group_number


@dataclass(frozen=True, config=ConfigDict(arbitrary_types_allowed=True))
class MicromagneticProperties:
    """Result object containing micromagnetic properties."""

    Ms_0: me.Entity
    """Saturation magnetisation at T=0K."""
    Ku_0: me.Entity
    """Uniaxial anisotropy constant K1 at T=0K."""


def get_micromagnetic_properties(
    chemical_formula: str | None = None,
    space_group_name: str | None = None,
    space_group_number: int | None = None,
    cell_length_a: float | None = None,
    cell_length_b: float | None = None,
    cell_length_c: float | None = None,
    cell_angle_alpha: float | None = None,
    cell_angle_beta: float | None = None,
    cell_angle_gamma: float | None = None,
    cell_volume: float | None = None,
    ICSD_label: str | None = None,
    OQMD_label: str | None = None,
    print_info: bool = False,
) -> MicromagneticProperties:
    """Get micromagnetic intrinsic properties at 0K temperature from table.

    Given certain material information, this function searches
    and retrieves the following values from a local database:

    * `Ms_0`: spontaneous magnetisation at temperature 0K expressed in A/m.

    * `K_0`: magnetocrystalline anisotropy at temperature 0K expressed in J/m^3.

    Args:
        chemical_formula: Chemical formula.
        space_group_name: Space group name.
        space_group_number: Space group number.
        cell_length_a: Cell length a.
        cell_length_b: Cell length b.
        cell_length_c: Cell length c.
        cell_angle_alpha: Cell angle alpha.
        cell_angle_beta: Cell angle beta.
        cell_angle_gamma: Cell angle gamma.
        cell_volume: Cell volume.
        ICSD_label: Label in the NIST Inorganic Crystal Structure Database.
        OQMD_label: Label in the the Open Quantum Materials Database.
        print_info: Print info

    Returns:
        Saturation magnetisation and uniaxial anisotropy at T=0.

    Raises:
        ValueError: Wrong format for `short_label`.

    Examples:
        >>> import mammos_dft.db
        >>> mammos_dft.db.get_micromagnetic_properties("Nd2Fe14B")
        MicromagneticProperties(Ms_0=..., Ku_0=...)
    """
    # TODO: implement CIF parsing
    material = _find_unique_material(
        print_info=print_info,
        chemical_formula=chemical_formula,
        space_group_name=space_group_name,
        space_group_number=space_group_number,
        cell_length_a=cell_length_a,
        cell_length_b=cell_length_b,
        cell_length_c=cell_length_c,
        cell_angle_alpha=cell_angle_alpha,
        cell_angle_beta=cell_angle_beta,
        cell_angle_gamma=cell_angle_gamma,
        cell_volume=cell_volume,
        ICSD_label=ICSD_label,
        OQMD_label=OQMD_label,
    )
    return MicromagneticProperties(
        me.Ms(material.SpontaneousMagnetization),
        me.Ku(material.UniaxialAnisotropyConstant),
    )


def find_materials(**kwargs) -> pd.DataFrame:
    """Find materials in database.

    This function retrieves one or known materials from the database
    `db.csv` by filtering for any requirements given in `kwargs`.

    Args:
        kwargs: Selection criteria.

    Returns:
        Dataframe containing materials with requested qualities. Possibly empty.

    """
    df = pd.read_csv(
        DATA_DIR / "db.csv",
        converters={
            "chemical_formula": str,
            "space_group_name": str,
            "space_group_number": int,
            "cell_length_a": u.Quantity,
            "cell_length_b": u.Quantity,
            "cell_length_c": u.Quantity,
            "cell_angle_alpha": u.Quantity,
            "cell_angle_beta": u.Quantity,
            "cell_angle_gamma": u.Quantity,
            "cell_volume": u.Quantity,
            "ICSD_label": str,
            "OQMD_label": str,
            "label": str,
            "SpontaneousMagnetization": u.Quantity,
            "UniaxialAnisotropyConstant": u.Quantity,
        },
    )
    for key, value in kwargs.items():
        if value is not None:
            if isinstance(value, u.Quantity):
                df = df[df[key] == value.to(df[key].unit)]
            else:
                df = df[df[key] == value]
    return df


def _find_unique_material(print_info: bool = False, **kwargs) -> pd.DataFrame:
    """Find unique material in database.

    This function retrieves one material from the database
    `db.csv` by filtering for any requirements given in **kwargs.
    If no or more than one materials are found, an error is raised.

    Args:
        print_info: Show detailed info.
        **kwargs: Filter criteria.

    Returns:
        Dataframe containing materials with requested qualities. Possibly empty.

    Raises:
        LookupError: Requested material not found in database.
        LookupError: Too many results.

    """
    df = find_materials(**kwargs)
    num_results = len(df)
    if num_results == 0:
        raise LookupError("Requested material not found in database.")
    elif num_results > 1:  # list all possible choice
        error_string = (
            "Too many results. Please refine your search.\n"
            + "Avilable materials based on request:\n"
        )
        for _row, material in df.iterrows():
            error_string += _describe_material(material)
        raise LookupError(error_string)
    else:
        material = df.iloc[0]
        if print_info:
            print("Found material in database.")
            print(_describe_material(material))
        return material


def _get_cif(
    short_label: str | None = None,
    chemical_formula: str | None = None,
    space_group_name: str | None = None,
    space_group_number: int | None = None,
    cell_length_a: float | None = None,
    cell_length_b: float | None = None,
    cell_length_c: float | None = None,
    cell_angle_alpha: float | None = None,
    cell_angle_beta: float | None = None,
    cell_angle_gamma: float | None = None,
    cell_volume: float | None = None,
    ICSD_label: str | None = None,
    OQMD_label: str | None = None,
    print_info: bool = False,
    outdir: str | pathlib.Path = "out",
) -> None:
    """Load cif and move it to the directory `outdir`.

    Args:
        short_label: Chemical formula and space group number separated by a hyphen "-".
        chemical_formula: Chemical formula.
        space_group_name: Space group name.
        space_group_number: Space group number.
        cell_length_a: Cell length a.
        cell_length_b: Cell length b.
        cell_length_c: Cell length c.
        cell_angle_alpha: Cell angle alpha.
        cell_angle_beta: Cell angle beta.
        cell_angle_gamma: Cell angle gamma.
        cell_volume: Cell volume.
        ICSD_label: Label in the NIST Inorganic Crystal Structure Database.
        OQMD_label: Label in the the Open Quantum Materials Database.
        print_info: Print info
        outdir: Output directory

    """
    pathlib.Path(outdir).mkdir(exist_ok=True, parents=True)
    if short_label is not None:
        chemical_formula, space_group_number = _check_short_label(short_label)
    material = _find_unique_material(
        print_info=print_info,
        chemical_formula=chemical_formula,
        space_group_name=space_group_name,
        space_group_number=space_group_number,
        cell_length_a=cell_length_a,
        cell_length_b=cell_length_b,
        cell_length_c=cell_length_c,
        cell_angle_alpha=cell_angle_alpha,
        cell_angle_beta=cell_angle_beta,
        cell_angle_gamma=cell_angle_gamma,
        cell_volume=cell_volume,
        ICSD_label=ICSD_label,
        OQMD_label=OQMD_label,
    )
    shutil.copy(
        DATA_DIR / material.label / "structure.cif",
        outdir,
    )


def _get_dft_output(
    short_label: str | None = None,
    chemical_formula: str | None = None,
    space_group_name: str | None = None,
    space_group_number: int | None = None,
    cell_length_a: float | None = None,
    cell_length_b: float | None = None,
    cell_length_c: float | None = None,
    cell_angle_alpha: float | None = None,
    cell_angle_beta: float | None = None,
    cell_angle_gamma: float | None = None,
    cell_volume: float | None = None,
    ICSD_label: str | None = None,
    OQMD_label: str | None = None,
    print_info: bool = False,
    outdir: str | pathlib.Path = "out",
) -> None:
    """Load dft output files and move them to directory `outdir`.

    Args:
        short_label: Chemical formula and space group number separated by a hyphen "-".
        chemical_formula: Chemical formula.
        space_group_name: Space group name.
        space_group_number: Space group number.
        cell_length_a: Cell length a.
        cell_length_b: Cell length b.
        cell_length_c: Cell length c.
        cell_angle_alpha: Cell angle alpha.
        cell_angle_beta: Cell angle beta.
        cell_angle_gamma: Cell angle gamma.
        cell_volume: Cell volume.
        ICSD_label: Label in the NIST Inorganic Crystal Structure Database.
        OQMD_label: Label in the the Open Quantum Materials Database.
        print_info: Print info
        outdir: Output directory

    """
    pathlib.Path(outdir).mkdir(exist_ok=True, parents=True)
    if short_label is not None:
        chemical_formula, space_group_number = _check_short_label(short_label)
    material = _find_unique_material(
        print_info=print_info,
        chemical_formula=chemical_formula,
        space_group_name=space_group_name,
        space_group_number=space_group_number,
        cell_length_a=cell_length_a,
        cell_length_b=cell_length_b,
        cell_length_c=cell_length_c,
        cell_angle_alpha=cell_angle_alpha,
        cell_angle_beta=cell_angle_beta,
        cell_angle_gamma=cell_angle_gamma,
        cell_volume=cell_volume,
        ICSD_label=ICSD_label,
        OQMD_label=OQMD_label,
    )
    for file in "jfile", "momfile", "posfile":
        shutil.copy(
            DATA_DIR / material.label / file,
            outdir,
        )


def _describe_material(
    material: pd.DataFrame | None = None, material_label: str | None = None
) -> str:
    """Describe material in a complete way.

    This function returns a string listing the properties of the given material
    or the given material label.

    Args:
        material: Material dataframe containing structure information.
        material_label: Label of material in local database.

    Returns:
        Description of the material

    Raises:
        ValueError: If `material` and `material_label` are both ``None``.

    """
    if material is None and material_label is None:
        raise ValueError("Material and material label cannot be both empty.")
    elif material_label is not None:
        df = find_materials()
        material = df[df["label"] == material_label].iloc[0]
    return dedent(
        f"""
            Chemical Formula: {material.chemical_formula}
            Space group name: {material.space_group_name}
            Space group number: {material.space_group_number}
            Cell length a: {material.cell_length_a}
            Cell length b: {material.cell_length_b}
            Cell length c: {material.cell_length_c}
            Cell angle alpha: {material.cell_angle_alpha}
            Cell angle beta: {material.cell_angle_beta}
            Cell angle gamma: {material.cell_angle_gamma}
            Cell volume: {material.cell_volume}
            ICSD_label: {material.ICSD_label}
            OQMD_label: {material.OQMD_label}
            """
    )
