"""
This module contains functions for generating molcas input files
"""

import os
import warnings
import numpy as np
import numpy.linalg as la
import xyz_py as xyzp
from xyz_py import atomic
import scipy.special as sps
import copy

ANG2BOHR = 1.88973

class MolcasInput:

    def __init__(self, *sections, title=None):
        self.sections = sections
        self.title = title

    def write(self, f_name):

        with open(f_name, "w") as f:

            if self.title is not None:
                f.write(str(MolcasComm(self.title, num_char=3)))
                f.write('\n')

            f.write('\n\n'.join(str(sec) for sec in self.sections))


class MolcasComm:
    def __init__(self, text, num_char=1):
        self.num_char = num_char
        self.text = text

    def __str__(self):
        return "{} {}".format('*' * self.num_char, self.text)


class Emil:
    def __init__(self, cmd, *args, num_char=2):
        self.cmd = cmd.upper()
        self.args = args
        self.num_char = num_char

    def __str__(self):
        return '>' * self.num_char + " " + \
            "{} {}".format(self.cmd, " ".join(self.args))


class MolcasProg:
    def __init__(self, name, *args, num_indent=2, **kwargs):
        self.name = name.upper()
        self.args = args
        self.kwargs = kwargs
        self.num_indent = num_indent

    def __str__(self, *args, **kwargs):
        indent = self.num_indent * ' '
        keywords = self.args + args
        keywords_vals = dict(**self.kwargs, **kwargs)

        def str_indent(val):
            return indent + str(val)

        return '\n'.join(
            ["&{}".format(self.name)] +
            [str_indent(val) for val in keywords if val is not None] +
            ["\n".join(map(str_indent, [f"{key}= {val[0]}"] + val[1:]))
             if isinstance(val, list) else (
                 "\n".join(map(str_indent, (f"{key}",) + val))
                 if isinstance(val, tuple) else str_indent(f"{key}= {val}"))
             for key, val in keywords_vals.items() if val is not None])


class Gateway(MolcasProg):
    def __init__(self, *args, group="NoSym", kirkwood=None, **kwargs):

        if kirkwood is not None:  # make me pretty
            rf_params = f"{kirkwood[0]} {float(kirkwood[1]) * ANG2BOHR} {kirkwood[2]}"
            kwargs["rf-input"] = ("reaction field", rf_params, "end of rf-input")

        super().__init__('Gateway', *args, **kwargs, group="NoSym")


class Seward(MolcasProg):
    def __init__(self, *args, **kwargs):
        super().__init__('Seward', *args, **kwargs)


class Casscf(MolcasProg):
    def __init__(self, nactel, ras2, *args, **kwargs):
        kwargs["Nactel"] = f"{nactel} 0 0"
        kwargs["RAS2"] = None if ras2 is None else f"{ras2}"

        super().__init__('Rasscf', *args, **kwargs)


class Caspt2(MolcasProg):
    def __init__(self, roots, *args, **kwargs):
        self.roots = roots

        super().__init__('Caspt2', *args, **kwargs)

    def __str__(self):
        multistate = {"Multistate": "{} {}".format(
            len(self.roots), ' '.join(map(str, self.roots)))}
        return super().__str__(**multistate)


class Rassi(MolcasProg):
    def __init__(self, *args, jobiph=None, properties=None, **kwargs):
        self.jobiph = jobiph
        self.properties = properties
        super().__init__('Rassi', *args, **kwargs)

    def __str__(self):

        if self.jobiph is not None:
            jobiph_section = {
                "Nr of JobIph":
                    ["{} {}".format(
                        str(len(self.jobiph)),
                        " ".join([str(root) for root in self.jobiph]))] +
                    [" ".join([str(r) for r in range(1, root + 1)])
                     for root in self.jobiph],
                "IPHN":
                    tuple([f"{i}_IPH" for i in range(1, len(self.jobiph) + 1)])
            }
        else:
            jobiph_section = {}

        if self.properties is None or len(self.properties) == 0:
            prop_section = {}
        else:
            prop_section = {
                "PROP": tuple([len(self.properties)] + self.properties)}

        return super().__str__(**jobiph_section, **prop_section)


class SingleAniso(MolcasProg):
    def __init__(self, *args, quax=None, **kwargs):
        self.quax = quax
        super().__init__('Single_Aniso', *args, **kwargs)

    def __str__(self):

        quax_section = {
            "QUAX": ([3] + [" ".join(map(str, row)) for row in self.quax])
            if self.quax is not None else 1}

        return super().__str__(**quax_section)


class Alaska(MolcasProg):
    def __init__(self, *args, **kwargs):
        super().__init__('Alaska', *args, **kwargs)


class Mclr(MolcasProg):
    def __init__(self, *args, **kwargs):
        super().__init__('Mclr', *args, **kwargs)


def resolve_labels(labels):

    # resolve atom labels
    atom_labels = [lab.split('.', 1)[0] for lab in labels]

    if not any(any(letter.isdigit() for letter in lab) for lab in atom_labels):
        atom_labels = xyzp.add_label_indices(atom_labels)

    # resolve predefined basis labels
    basis_labels = [lab.split('.', 1)[1] if lab.split('.', 1)[1:] else None
                    for lab in labels]

    return atom_labels, basis_labels


def resolve_coordination(coords, atom_labels, central, n_coord_atoms,
                         coord_hydrogens=False):

    # resolve center atom
    if not any(letter.isdigit() for letter in central):
        central += '1'

    ctr_idc = \
        [i for i, lab in enumerate(atom_labels) if lab == central.capitalize()]

    # If no match for central atom error out
    if len(ctr_idc) == 0:
        raise ValueError(f"No instances of central atom {central} found")

    # If more than one match for central atom error out
    if len(ctr_idc) > 1:
        raise ValueError(f"Multiple instances of central atom {central} found")

    ctr_idx = ctr_idc[0]
    ctr_coords = coords[ctr_idx]

    distances = [la.norm(atom_coords - ctr_coords) for atom_coords in coords]
    distance_order = np.argsort(distances).tolist()

    coord_idc = []
    counter = n_coord_atoms
    
    for idx, lab in enumerate([atom_labels[i] for i in distance_order]):
        if counter == 0:
            break
        elif (not coord_hydrogens and lab[0] == "H") or distance_order[idx] == ctr_idx:
            continue
        else:
            coord_idc.append(distance_order[idx])
            counter -= 1

    return ctr_idx, coord_idc


def save_xfield(f_name, xfield):

    if len(xfield[0]) == 4:
        n_ord = 0
        fmt = "{: 12.8f} " * 3 + "{:^12.8f} " + "\n"
    elif len(xfield[0]) == 7:
        n_ord = 1
        fmt = "{: 12.8f} " * 3 + "{:^12.8f} " + "{: 12.8f} " * 3 + "\n"
    else:
        raise ValueError("Wrong number of columns in xfield input!")

    with open(f_name, 'w') as f:
        f.write("{:d} ANGSTROM {:d}\n".format(len(xfield), n_ord))
        for line in xfield:
            # x, y, z, charge (, dipolex, dipoley, dipolez)
            f.write(fmt.format(*line))


def generate_input(labels, coords, central_atom, charge, n_active_elec,
                   n_active_orb, n_coord_atoms, f_name,
                   xfield=None, kirkwood=None, coord_hydrogens=False,
                   decomp="RICD_acCD", gateway_extra=((), {}),
                   basis_set_central="ANO-RCC-VTZP",
                   basis_set_coord="ANO-RCC-VDZP",
                   basis_set_remaining="ANO-RCC-VDZ",
                   rasscf_extra=((), {}), high_S_only=False, initial_orb=None,
                   max_orb=None, extract_orbs=True,
                   caspt2=False, caspt2_extra=((), {}),
                   rassi=True, rassi_extra=((), {}),
                   single_aniso=True, single_aniso_extra=((), {}),
                   quax=None, skip_magneto=False, optics=True,
                   x2c=False):
    """
    Generates OpenMolcas input file for a CASSCF-RASSI-SO calculation on a
        coordination complex

    Parameters
    ----------
    labels : list
        Atomic labels
    coords : list
        list of lists of xyz coordinates of each atom
    central_atom : str
        Atomic label of central atom
    charge : int
        Charge of entire system
    n_active_elec : int
        Number of active electrons
    n_active_orb : int
        Number of active orbitals
    n_coord_atoms : int
        Number of atoms coordinates to central atom
    f_name : str
        Filename of final input file including extension
    xfield : list, optional
        list of lists of x, y, z, charge, dipole
    kirkwood: tuple, optional
        Tuple of dielectric constant, cavitiy radius in Å, order of multipoles
    coord_hydrogens : bool, default False
        If True, hydrogens will be treated as coordinating atoms
    decomp : str, default "RICD_acCD"
        Keyword(s) to use for SEWARD 2 electron integral decompositon
    gateway_extra : list, optional
        Extra keywords/commands for GATEWAY section
    basis_set_central : str, default ANO-RCC-VTZP
        Basis set for central atom
    basis_set_coord : str, default ANO-RCC-VDZP
        Basis set for coordinated atoms
    basis_set_remaining : str, default ANO-RCC-VDZ
        Basis set for all other atoms
    rasscf_extra : list, optional
        Extra keywords/commands for CASSCF section(s)
    high_S_only : bool, default False
        If True, only consider the highest spin state
    initial_orb : str, optional
        Path to a custom input guess orbital file used in the initial
        RASSCF call
    max_orb : int, default None (all roots)
        Maximum number of RasOrb files to produce,
        one for each root up to the specified maximum. By default this is
        the number of roots per spin state
    extract_orbs : bool, default True
        If True, extract SA orbs with molcas_suite orbs to give human
        readable file for first spin
    caspt2 : bool, default False
        If True, include a CASPT2 section
    caspt2_extra : list, optional
        Extra keywords/commands for CASPT2 section
    rassi : bool, default True
        If True, include a RASSI section
    rassi_extra : list, optional
        Extra keywords/commands for RASSI section
    single_aniso : bool, default True
        If True, include a SINGLE_ANISO section
    single_aniso_extra : list, optional
        Extra keywords/commands for SINGLE_ANISO
    quax : np.ndarray, optional
        (3,3) array containing rotation matrix for CFP reference frame
    skip_magneto : bool, default False
        If True, skip calculation of magnetic data section
    optics : bool, default True
        If True, include extra keywords in SEWARD and RASSI sections to enable the evaluation of optical properties

    Returns
    -------
    None
    """

    atom_labels, predef_labels = resolve_labels(labels)

    # generate basis set labels
    ctr_idx, coord_idc = \
        resolve_coordination(coords, atom_labels, central_atom, n_coord_atoms,
                             coord_hydrogens=coord_hydrogens)

    ctr_lab = xyzp.remove_label_indices([central_atom])[0].capitalize()
    ctr_num = atomic.lab_num[ctr_lab]

    # return basis labels
    labels = \
        ['.'.join([lab, basis_set_central if i == ctr_idx else (
                            basis_set_coord if i in coord_idc else (
                                predef or basis_set_remaining))])
         for i, (lab, predef) in enumerate(zip(atom_labels, predef_labels))]

    # write external files
    abs_stem = os.path.splitext(f_name)[0]
    rel_stem = os.path.basename(abs_stem)

    # xyz coordinate file
    xyzp.save_xyz(f"{abs_stem}_basis.xyz", labels, coords, verbose=False)

    # write external xfield file
    if xfield is not None:
        save_xfield(f"{abs_stem}.xfield", xfield)

    sections = []
    sections.append(Gateway(
        "AMFI",
        *gateway_extra[0],
        "RICD" if decomp == 'RICD_acCD' else None,
        "acCD" if decomp == 'RICD_acCD' else None,
        "RX2C" if x2c else None,
        Coord=f"${{CurrDir}}/{rel_stem}_basis.xyz",
        XField=f"${{CurrDir}}/{rel_stem}.xfield" if xfield else None,
        kirkwood=kirkwood,
        Angmom=' '.join(map(str, coords[ctr_idx])) + " ANGSTROM",
        **gateway_extra[1]))

    sections.append(Seward(
        "Center= 2\n    1  " + ' '.join(map(str, coords[ctr_idx])) + " ANGSTROM\n    2  " + ' '.join(map(str, coords[ctr_idx])) + " ANGSTROM" if optics else None,
        decomp if decomp != 'RICD_acCD' else None))

    # Get information on electronic states
    spin_list, root_list, trunc_root_list = get_spin_and_roots(
        central_atom, n_active_elec, n_active_orb, high_S_only)

    if any([root > 500 for root in root_list]):
        warnings.warn("Encountered large number of roots.")

    if max_orb is None and any([root > 100 for root in root_list]):
        warnings.warn("Encountered large number of RasOrb files.")

    rasscf_sections = [[
        Casscf(n_active_elec, n_active_orb if i == 1 else None,
               None if i == 1 else "Typeindex",
               *rasscf_extra[0], Spin=spin, Charge=charge,
               FILEORB=initial_orb if i == 1 else f"{i-1:d}.RasOrb",
               CiRoot=f"{root} {root} 1", ORBA="FULL", MAXORB="1",
               **rasscf_extra[1]),
        Emil("Copy", "$Project.JobIph", f"{i:d}_IPH"),
        Emil("Copy", "$Project.RasOrb", f"{i:d}.RasOrb"),
        Emil("Copy", "$Project.rasscf.h5", f"{i:d}.rasscf.h5"),
        *([Caspt2(roots=range(1, root+1), *caspt2_extra[0], **caspt2_extra[1]),
           Emil("Copy", "$Project.JobIph", f"{i:d}_PT2_IPH")]
          if caspt2 else [])]
        for i, (spin, root) in enumerate(zip(spin_list, root_list), start=1)]

    sections.extend([row for sec in rasscf_sections for row in sec])

    sections.append(Rassi(
        "SPIN", "MEES", *rassi_extra[0], EPRG="7.0D-1",
        properties=[f"'ANGMOM' {i}" for i in range(1, 4)] if optics == False else [f"'ANGMOM' {i}" for i in range(1, 4)] + [f"'MltPl  1' {i}" for i in range(1, 4)] + [f"'MltPl  2' {i}" for i in range(1, 7)],
        jobiph=trunc_root_list,
        **rassi_extra[1]))

    # Request CFPs for TM, Ln, Ac
    if 21 <= ctr_num <= 30 and n_active_orb == 5:
        crys = True
    elif (57 <= ctr_num <= 71 or 89 <= ctr_num < 103) and n_active_orb == 7:
        crys = True
    else:
        warnings.warn("Manually assign multiplet dimension in MLTP!")
        crys = False

    sections.append(SingleAniso(
        *single_aniso_extra[0],
        CRYS=ctr_lab.lower() if crys else None, MLTP="1; 2",
        **{} if skip_magneto else {"TINT": "0.0  330.0  330  0.0001",
                                   "HINT": "0.0  10.0  201",
                                   "TMAG": "6 1.8 2 4 5 10 20"},
        quax=quax, **single_aniso_extra[1]))

    MolcasInput(*sections).write(f_name)


def get_spin_and_roots(central_atom, n_active_elec, n_active_orb,
                       high_S_only=False):

    """
    Generates list of spin states and roots given a number of orbitals and
    electrons

    Parameters
    ----------
    central_atom : str
        Atomic label of central atom
    n_active_elec : int
        Number of active electrons
    n_active_orb : int
        Number of active orbitals
    high_S_only : bool, default False
        If True, only consider the highest spin state

    Returns
    -------
    list
        2S values for each spin state
    list
        Number of roots for each spin state
    list
        Reduced number of roots for each spin state
    """

    # Calculate high and low spin states
    if (n_active_elec <= n_active_orb):
        high_spin = n_active_elec + 1
    else:
        high_spin = 2 * n_active_orb - n_active_elec + 1

    low_spin = n_active_elec % 2 + 1

    # Calculate total number of spin states
    if (high_S_only):
        lim = copy.copy(high_spin)
    else:
        lim = copy.copy(low_spin)

    n_spin_states = len(range(high_spin, lim-2, -2))

    # Array of spin values for each spin states
    spin_states = [int(high_spin - 2*i) for i in range(0, n_spin_states)]

    # Calculate the roots of each spin

    # Calculate number of roots in each spin state, and
    # truncated number of roots used in RASSI

    # Dictionary of roots and truncated roots for Lanthanide ions
    # Key is number of active electrons
    # Value is [roots, trunc_roots]
    # Where roots and trunc_roots are lists
    ln_roots_dict = {
        1: [[7], [7]],
        2: [[21, 28], [21, 28]],
        3: [[35, 112], [35, 112]],
        4: [[35, 210, 196], [35, 159, 156]],
        5: [[21, 224, 490], [21, 128, 130]],
        6: [[7, 140, 588, 490], [7, 140, 195, 197]],
        7: [[1, 48, 392, 784], [1, 48, 119, 113]],
        8: [[7, 140, 588, 490], [7, 140, 195, 197]],
        9: [[21, 224, 490], [21, 128, 130]],
        10: [[35, 210, 196], [35, 159, 156]],
        11: [[35, 112], [35, 112]],
        12: [[21, 28], [21, 28]],
        13: [[7], [7]]
    }
    # Defining small list of roots for spin-phonon calculations on Ln3+ ions
    # Ce = 2F
    # Pr = 3H + 3F
    # Nd = 4I
    # Pm = 5I
    # Sm = 6H + 6F
    # Eu = 7F
    # Gd = 8S
    # Tb = 7F
    # Dy = 6H + 6F
    # Ho = 5I
    # Er = 4I
    # Tm = 3H
    # Yb = 2F
    small_ln_roots_dict = {
        1: [[7], [7]],
        2: [[18], [18]],
        3: [[13], [13]],
        4: [[13], [13]],
        5: [[18], [18]],
        6: [[7], [7]],
        7: [[1], [1]],
        8: [[7], [7]],
        9: [[18], [18]],
        10: [[13], [13]],
        11: [[13], [13]],
        12: [[11], [11]],
        13: [[7], [7]]
    }

    _central_atom = xyzp.remove_label_indices([central_atom])[0].capitalize()

    # Check if Lanthanide n in 7 calculation
    if 57 <= atomic.lab_num[_central_atom] <= 71 and n_active_orb == 7:
        ln_calc = True
    else:
        ln_calc = False

    # If n in 7 for Ln: use above dictionary
    if ln_calc:
        roots, trunc_roots = ln_roots_dict[n_active_elec]
    # All other elements calculate the number of roots with Weyl's formula
    else:
        roots = []
        for spin in spin_states:
            k = spin/float(n_active_orb+1)
            k *= sps.binom(
                n_active_orb + 1,
                0.5*n_active_elec - (spin - 1.) * 0.5
                )
            k *= sps.binom(
                n_active_orb + 1,
                0.5*n_active_elec + (spin - 1.) * 0.5+1.
                )
            if (k <= 500):
                roots.append(int(k))
            else:
                roots.append(-1)
            # In this case trunc_roots is equal to roots
        trunc_roots = copy.copy(roots)

    if high_S_only:
        if ln_calc:
            roots, trunc_roots = small_ln_roots_dict[n_active_elec]
        else:
            roots = [roots[0]]
            trunc_roots = [trunc_roots[0]]

    return spin_states, roots, trunc_roots
