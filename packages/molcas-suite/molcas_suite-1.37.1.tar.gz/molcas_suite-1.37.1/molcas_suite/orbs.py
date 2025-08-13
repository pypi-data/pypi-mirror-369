"""
This module contains functions for working with molcas orbitals and orbital
files
"""

import numpy as np
import sys
from . import h5tools
import socket
from datetime import datetime


def parse_orbfile(orbname):
    """
    Reads ASCII orb file (e.g. RasOrb, ScfOrb) and returns MO vectors,
    energies, occupation numbers and type indices as numpy arrays.

    Parameters
    ----------
    orbname : str
        path to ASCII orb file

    Returns
    -------
        dict:
        Keys:
            'orbtype' (str),
            'nbas_orb' (int),
            'mo_vecs' (np.ndarray),
            'mo_types' (np.ndarray),
            'mo_energies' (np.ndarray),
            'mo_occupations' (np.ndarray)
    """
    data_dict = {}
    with open(orbname, 'r') as f:
        # Find INFO block and read orbital description and basis size
        line = f.readline()
        while '#INFO' not in line:
            line = f.readline()
        data_dict['orbtype'] = f.readline().lstrip('* ').rstrip()

        line = f.readline()
        nbas = int(f.readline().strip())
        # store to do consistency check with basis info from .h5 file
        data_dict['nbas_orb'] = nbas

        # Coefficients and occupation number are printed 5 on each line
        # determine number of lines
        if nbas % 5:
            nlines = nbas // 5 + 1
        else:
            nlines = nbas // 5

        # Find ORB block and read MO coefficients
        while '#ORB' not in line:
            line = f.readline()
        data_dict['mo_vecs'] = []
        for i in range(nbas):
            line = f.readline()  # MO header
            coeff_list = []
            for j in range(nlines):
                line = f.readline()
                coeff_list += [float(coeff) for coeff in line.strip().split()]
            data_dict['mo_vecs'].append(coeff_list)
        # Transpose to get MO column vectors
        data_dict['mo_vecs'] = np.array(data_dict['mo_vecs']).transpose(1, 0)

        # Occupations
        while '#OCC' not in line:
            line = f.readline()
        line = f.readline()
        data_dict['mo_occupations'] = []
        for i in range(nlines):
            line = f.readline()
            data_dict['mo_occupations'] += [
                float(occ) for occ in line.strip().split()
            ]
        data_dict['mo_occupations'] = np.array(data_dict['mo_occupations'])

        # Energies and indices are printed 10 on each line
        # determine number of lines
        if nbas % 10:
            nlines = nbas // 10 + 1
        else:
            nlines = nbas // 10

        # Energies
        while '#ONE' not in line:
            line = f.readline()
        line = f.readline()
        data_dict['mo_energies'] = []
        for i in range(nlines):
            line = f.readline()
            data_dict['mo_energies'] += [
                float(e) for e in line.strip().split()
            ]
        data_dict['mo_energies'] = np.array(data_dict['mo_energies'])

        # Indices / types
        while '#INDEX' not in line:
            line = f.readline()
        line = f.readline()
        data_dict['mo_types'] = []
        for i in range(nlines):
            line = f.readline()
            data_dict['mo_types'] += list(line[2:].strip())
        data_dict['mo_types'] = np.array(data_dict['mo_types'], dtype=str)

    return data_dict


def create_orbfile(data_dict, orbname="ModOrb"):
    """
    Creates ASCII orb file (e.g. RasOrb, ScfOrb) using provided MO vectors,
    energies, occupation numbers and type indices as numpy arrays.

    Parameters
    ----------
    orbname : str
        path to output ASCII orb file
    data_dict:
        Dictionary containing all information needed to reconstruct orbital
        file, see `parse_orbfile` for details
        Keys:
            'orbtype' (str),
            'nbas_orb' (int),
            'mo_vecs' (np.ndarray),
            'mo_types' (np.ndarray),
            'mo_energies' (np.ndarray),
            'mo_occupations' (np.ndarray)

    Returns
    -------
        None
    """

    nbas_orb = data_dict["nbas_orb"]

    index_table = data_dict["mo_types"]

    if nbas_orb % 10:
        n_to_add = 10 - (nbas_orb % 10)
        index_table = np.append(
            index_table, [""] * n_to_add
        )

    index_table = index_table.reshape([int(np.ceil(nbas_orb/10)), 10])

    host = socket.gethostname()

    with open(orbname, "w") as f:
        f.write("#INPORB 2.2\n")
        f.write("#INFO\n")
        f.write("*{}\n".format(data_dict["orbtype"]))
        # UHF, SYMMETRY, ORBTYPE
        f.write("       0       1       0\n")
        # Number of basis functions
        f.write("{:8d}\n".format(nbas_orb))
        # Number of orbitals
        f.write("{:8d}\n".format(nbas_orb))
        f.write(
            "*BC:HOST {} PID 12345 DATE {}\n".format(
                host,
                datetime.now().ctime()
            )
        )

        f.write("#ORB\n")
        for oit in range(nbas_orb):
            write_rasorb_section(
                f,
                "* ORBITAL    1{:5d}".format(oit+1),
                data_dict["mo_vecs"][:, oit],
                "{: 16.14E}",
                5,
                nbas_orb
            )

        write_rasorb_section(
            f,
            "#OCC\n* OCCUPATION NUMBERS",
            data_dict["mo_occupations"],
            "{: 16.14E}",
            5,
            nbas_orb
        )

        write_rasorb_section(
            f,
            "#OCHR\n* OCCUPATION NUMBERS (HUMAN-READABLE)",
            data_dict["mo_occupations"],
            "{: 6.4f}",
            10,
            nbas_orb
        )

        write_rasorb_section(
            f,
            "#ONE\n* ONE ELECTRON ENERGIES",
            data_dict["mo_energies"],
            "{: 6.4E}",
            10,
            nbas_orb
        )

        write_rasorb_index(f, index_table)
    return


def write_rasorb_section(file_obj, header, data, fmt, ncol, dat_size):
    """
    Writes a RasOrb file section to an already opened
    file object given a dataset and format string

    Parameters
    ----------
    file_obj : file object
        writable file object for output file
    header : str
        Header for section containing both the # and * lines with a newline
        character in between e.g "#ONE\\n* ONE ELECTRON ENERGIES"
    data : np.ndarray
        array (dat_size, dat_size) containing specified data
    fmt : str
        Formatting string for single entry e.g. "{: 16.14e}"
    ncol : int
        Number of columns of data per line
    dat_size : int
        Number of data entries in leading dimension of data

    Returns
    -------
        None
    """

    end = dat_size//ncol * ncol

    fmt = fmt.lstrip()
    fmt += " "

    file_obj.write("{}\n".format(header))
    for cit in range(0, end, ncol):
        frmt = " "+"".join(fmt * ncol)
        frmt = frmt.rstrip() + "\n"
        file_obj.write(frmt.format(*data[cit:cit+ncol]))
    if dat_size % ncol:
        frmt = " "+"".join(fmt * (dat_size % ncol))
        frmt = frmt.rstrip() + "\n"
        file_obj.write(frmt.format(*data[end:]))

    return


def write_rasorb_index(file_obj, index_table):
    """
    Writes a RasOrb file INDEX section

    Parameters
    ----------
    file_obj : file object
        writable file object for output file
    data : np.ndarray
        np.ndarray (ceil(n_orb/10), 10) containing index characters as strings

    Returns
    -------
        None
    """

    file_obj.write("#INDEX\n")
    file_obj.write("* 1234567890\n")

    # Write table to file
    for rit, row in enumerate(index_table):
        row_str = "".join(row)
        file_obj.write("{:d} {}\n".format(rit % 10, row_str.rstrip()))

    return


def compute_mo_contributions(mo_vecs, ao_overlap, nbas):
    """
    Computes AO percentage contributions to each MO. Orthogonalizes MO
    coefficient vectors using ao_overlap.

    Parameters
    ----------
    mo_vecs : np.ndarray
        2D array of MO coefficients as column vectors
    ao_overlap : np.ndarray
        2D overlap matrix of AO basis functions
    nbas : int
        basis size

    Returns
    -------
    list
        orthogonalised MO coefficient percentages and MO vectors
        np.ndarray
            2D ndarray of AO percentage contributions
        np.ndarray
            2D ndarray of AO coefficients
    """
    # Diagonalise overlap matrix S and compute S^1/2
    ovlp_evals, ovlp_evecs = np.linalg.eigh(ao_overlap)
    ovlp_sqrt = np.zeros((nbas, nbas), dtype=np.float64)
    np.fill_diagonal(ovlp_sqrt, np.sqrt(ovlp_evals))
    # Convert ovlp_sqrt from its eigenbasis to AO basis
    ovlp_sqrt = ovlp_evecs @ ovlp_sqrt @ ovlp_evecs.T

    # Orthogonalise MO coefficients as S^1/2 C
    _mo_vecs = ovlp_sqrt @ mo_vecs
    # resulting matrix is orthonormal (coeffs were already normalised)
    # Create array of percentage contributions
    mo_percentages = 100 * _mo_vecs ** 2
    return mo_percentages, _mo_vecs


def create_basis_labels(bas_id_groups, ngroups, atom_labels, pattern='cnlm'):
    """
    Creates string labels for each AO contribution obeying the given pattern.
    Called from group_and_sort.

    Parameters
    ----------
    bas_id_groups : np.ndarray
        array of unique basis identifiers;
        columns correspond to a subset of
        atom index (c), shell (n),
        angular momentum (l) and angular momentum
        projection (m); max 4 columns
    ngroups : int
        number of AO groups, as determined by the pattern
    atom_labels : np.ndarray
        array of atom labels (strings)
    pattern : str, {'cnlm', 'c', 'cn', 'cl', 'cnl', 'clm'}
        pattern of basis identifiers

    Returns
    -------
    list
        string labels for the AO groups defined according to pattern
    """
    shells_by_angmom = ['s', 'p', 'd', 'f', 'g', 'h', 'i', 'k', 'l']
    # Molcas order for p shell components
    cartcomps = {1: 'x', -1: 'y', 0: 'z'}
    group_labels = []
    for i in range(ngroups):
        lbl = ''
        for j in range(len(pattern)):
            idx = bas_id_groups[i, j]
            if pattern[j] == 'c':
                lbl += '{:5}'.format(atom_labels[idx])
            elif pattern[j] == 'n':
                lbl += '{:3d}'.format(idx)
            elif pattern[j] == 'l':
                lbl += '{:1}'.format(shells_by_angmom[idx])
            elif pattern[j] == 'm' and bas_id_groups[i, j - 1] == 1:
                # p sub-shells, print Cartesian label if m is in the pattern
                lbl += '{:1}'.format(cartcomps[idx])
            elif pattern[j] == 'm' and bas_id_groups[i, j - 1]:
                # all sub-shells except s and p, print m_l quantum number
                lbl += '{:+1d}'.format(idx)
        group_labels.append(lbl)
    return group_labels


def group_and_sort(mo_percentages, bas_id, nbas, atom_labels, pattern='cnlm'):
    """
    Group AO percentage contributions based on the pattern given.

    Parameters
    ----------
    mo_percentages : np.ndarray
        2D array of AO percentage contributions
    bas_id : np.ndarray
        array of unique basis identifiers c, n, l, m for each basis
        function
    nbas  : int
        basis size
    atom_labels : np.ndarray
        array of unique atom labels stored as strings (e.g. 'Dy1')
    pattern : str, {'cnlm', 'c', 'cn', 'cl', 'cnl', 'clm'}
        pattern of basis identifiers used to group AO contributions

    Returns
    -------
    np.ndarray
        (ngroups, nbas) array of sorted AO percentage contributions
    np.ndarray
        (ngroups, nbas) array mapping indices of sorted contributions
        to the indices of group_labels
    list
        AO / AO group labels in normal order
    """

    if pattern == 'cnlm':
        bas_groups, ngroups, grouped_percentages = bas_id, nbas, mo_percentages
    else:
        # Determine what columns from bas_id to consider
        bas_id_toc = {'c': 0, 'n': 1, 'l': 2, 'm': 3}
        bas_id_cols = []
        for c in list(pattern):
            bas_id_cols.append(bas_id_toc[c])

        # Group basis functions according to pattern
        bas_groups, bas_inv = np.unique(
            bas_id[:, bas_id_cols], return_inverse=True, axis=0
        )
        ngroups = bas_groups.shape[0]

        # Convert bas_inv to dictionary mapping bas_groups rows to bas_id rows
        bas_ptr = {}
        for i in range(nbas):
            if bas_inv[i] in bas_ptr.keys():
                bas_ptr[bas_inv[i]].append(i)
            else:
                bas_ptr[bas_inv[i]] = [i]

        grouped_percentages = np.zeros((ngroups, nbas))
        for i in range(ngroups):
            grouped_percentages[i, :] = np.sum(
                mo_percentages[bas_ptr[i], :], axis=0
            )

    group_labels = create_basis_labels(
        bas_groups,
        ngroups,
        atom_labels,
        pattern=pattern
    )

    # Sort contributions
    sorted_idx = np.argsort(grouped_percentages, axis=0)
    # Reverse the order of sorted contributions
    sorted_idx = sorted_idx[::-1, :]
    sorted_percentages = np.take_along_axis(
        grouped_percentages, sorted_idx, axis=0
    )

    return sorted_percentages, sorted_idx, group_labels


def write_report(sorted_percentages, sorted_idx, group_labels, mo_energies,
                 mo_occ, mo_type, wfmode=False,
                 mo_coeff=None, fileobj=None, thr=1., signed_occ=False,
                 mo_filter=None, total_content_choice=None):
    """
    Writes MO data to orbs code output file.

    Parameters
    ----------
    sorted_percentages : np.ndarray
        (ngroups, nbas) array of sorted AO percentage contributions
    sorted_idx : np.ndarray
        (ngroups, nbas) array mapping indices of sorted contributions to
        the indices of group_labels
    group_labels : list
        AO / AO group labels in normal order
    mo_energies : np.ndarray
        MO energies
    mo_occ : np.ndarray
        MO occupation numbers
    mo_type : np.ndarray
        MO type indices
    wfmode : bool, default False
        if True, requests printing MO coefficients alongside percentages
    mo_coeff : np.ndarray, optional
        orthogonalised MO coefficient column vectors, required for `wfmode`
    fileobj : file object, optional
        file object to write orbital analysis output to.
        Default prints to screen
    thr : float, default 1.
        threshold for printing percentage contributions
    signed_occ : bool, default False
        if True, print singed occupation numbers
    mo_filter : np.ndarray, default None
        (bool) boolean array of MOs to be included in report. If None, all 
        orbitals printed.
   total_content_choice : char array, default None
        Position [0] gives atom or atom type, e.g. C or C21
        Position [1] gives AO type, e.g. 2p
        If None, default behaviour is maintained.

    Returns
    -------
    None
    """
    if fileobj is None:
        fileobj = sys.stdout

    (ngroups, nbas) = sorted_percentages.shape

    if signed_occ:
        mo_fmt = '---- MO {:4d}, occ = {:+4.2f}, energy = {:+12.4E}, index = {:1} ----\n'  # noqa
    else:
        mo_fmt = '---- MO {:4d}, occ = {:4.2f}, energy = {:+12.4E}, index = {:1} ----\n'  # noqa

    if wfmode:
        ao_fmt = '  {:11}  {:7.3f}    {:+13.7E}\n'
    else:
        ao_fmt = '  {:11}  {:7.3f}\n'

    if total_content_choice is not None:
        total_fmt = '  {:5}{:5}  {:11.7f}\n'

    for i in range(nbas):
        if mo_filter is None or mo_filter[i]:
            fileobj.write(
                    mo_fmt.format(i + 1, mo_occ[i], mo_energies[i], mo_type[i])
            )
            component_sum = 0.0
            for j in range(ngroups):
                ao_lbl = group_labels[sorted_idx[j, i]]
                if total_content_choice is not None:
                    if total_content_choice[0] in ao_lbl and total_content_choice[1] in ao_lbl:
                        component_sum += sorted_percentages[j, i]
                elif sorted_percentages[j, i] >= thr:
                    if wfmode:
                        fileobj.write(
                            ao_fmt.format(
                                ao_lbl,
                                sorted_percentages[j, i],
                                mo_coeff[sorted_idx[j, i], i]
                            )
                        )
                    else:
                        fileobj.write(
                            ao_fmt.format(ao_lbl, sorted_percentages[j, i])
                        )
                else:
                    break
            if total_content_choice is not None:
                fileobj.write(
                    total_fmt.format(total_content_choice[0], total_content_choice[1], component_sum)
                )


def average_to_root(orb_data,root):
    """
    Replaces average MO vectors and occupations with those for a specific
    root

    Parameters
    ----------
    orb_data : dict
        Dictionary containing MO vectors, types and occupations, and the
        single electron density matrices for each root
        Keys:
            'mo_vecs' (np.ndarray),
            'mo_occupations' (np.ndarray),
            'mo_types' (np.ndarray),
            'den_mat' (np.ndarray),
            'orbtype' (str)
    root : int, default 0
        index for outputting root MOs
        if 0, output average MOs

    Returns
    -------
    dict
        Keys:
            'mo_vecs' (np.ndarray),
            'mo_occupations' (np.ndarray)
            'mo_types' (np.ndarray),
            'den_mat' (np.ndarray),
            'orbtype' (str)
            plus any other keys in orb_data

    """

    active_indices = np.where(np.array(orb_data['mo_types']) == '2')[0]
    active_orbitals = orb_data['mo_vecs'][:,active_indices]
    occ,root_vecs = np.linalg.eigh(orb_data['den_mat'][root - 1])
    active_orbitals = active_orbitals @ root_vecs
    orb_data['mo_vecs'][:,active_indices] = active_orbitals
    orb_data['mo_occupations'][active_indices] = occ
    orb_data['orbtype'] = 'RasOrb (root ' + str(root) + ')'

    return orb_data


def orbital_analysis(h5name, orbname=None, pattern='cnlm', thr=1.,
                     wfmode=False, outfile=None, alpha=False, beta=False,
                     root=0, ener_range=None, occ_range=None, index='i123s',
                     user_total_content_choice=None):
    """
    Main method for the orbs program for orbital analysis.

    Parameters
    ----------
    h5name : str
        name of HDF5 file
    orbname : str, optional
        name of plain text orb file; overrides MO data from h5name
        default prints to screen
    pattern : str, {'cnlm', 'c', 'cn', 'cl', 'cnl', 'clm'}
        basis identifier pattern to split AO contributions
    thr : float, default 1.
        threshold for printing percentage contributions
    wfmode : bool, default True
        equivalent to pattern='cnlm' if True
    outfile : str, optional
        name of file to write output to
    alpha : bool, default False
        if True and h5name is from a UHF calculation, analyse alpha MOs
        instead of the natural MOs
    beta : bool, default False
        if True and h5name is from a UHF calculation, analyse beta MOs
        instead of the natural MOs
    root : int, default 0
        index for outputting root MOs
        if 0, output average MOs
    ener_range : list, [e_min, e_max], default None
        range of MO energies to be analysed. If None, no threshold 
        applied.
    occ_range : list, [occ_min, occ_max], default None
        range of orbital occupation numbers to be analysed. If None, no  
        threshold applied
    index : string, default 'i123s'
        string of orbital index types (i123s) to be included.
    user_total_content_choice : char array, default=None
        Position [0] gives atom or atom type, e.g. C or C21
        Position [1] gives AO type, e.g. 2p
        If None, default behaviour is maintained.

    Returns
    -------
    None
    """
    if wfmode:
        pattern = 'cnlm'
    elif pattern == 'cnlm':
        wfmode = True

    if orbname is None:
        orb_data = h5tools.read_h5(h5name, alpha=alpha, beta=beta)
    else:
        orb_data = h5tools.read_h5(h5name, basis_only=True)
        orb_data.update(parse_orbfile(orbname))
        # Double check basis sizes match
        if orb_data['nbas'] != orb_data['nbas_orb']:
            raise ValueError('The basis sizes do not match!')

    if 'spin density' in orb_data['orbtype']:
        signed_occ = True  # print signed occupations for spin density orbitals
    else:
        signed_occ = False

    #replace average MO vectors with those for the chosen root, using the single
    #electron density matrix
    #(single electron density matrix is only for the active space)
    if root > 0:
        orb_data = average_to_root(orb_data,root)

    mo_percentages, _mo_vecs = compute_mo_contributions(
        orb_data['mo_vecs'],
        orb_data['overlap'],
        orb_data['nbas']
    )
    sorted_percentages, sorted_idx, group_labels = group_and_sort(
        mo_percentages,
        orb_data['bas_ids'],
        orb_data['nbas'],
        orb_data['atom_labels'],
        pattern=pattern
    )
    if outfile is None:
        fout = sys.stdout
    else:
        fout = open(outfile, 'w+')

    # Print general info to output
    fout.write('Input HDF5 file: {}\n'.format(h5name))
    if orbname is not None:
        fout.write('Input ASCII file: {}\n'.format(orbname))

    if 'UHF' not in orb_data['orbtype']:
        fout.write('Orbital type: {}\n'.format(orb_data['orbtype']))
    elif alpha:
        fout.write('Orbital type: {} (alpha orbitals)\n'.format(
            orb_data['orbtype'])
        )
    elif beta:
        fout.write('Orbital type: {} (beta orbitals)\n'.format(
            orb_data['orbtype'])
        )
    else:
        fout.write('Orbital type: {} (unrestricted natural orbitals)\n'.format(
            orb_data['orbtype'])
        )

    fout.write('Separate AO contributions by: {}\n'.format(pattern))
    fout.write('Contribution threshold: {:5.1f} %\n'.format(thr))
    fout.write('Basis size: {}\n'.format(orb_data['nbas']))

    # energy range
    if ener_range:
        mo_energies_filter = \
            [ener_range[0] <= orb_data['mo_energies'][i] <= ener_range[1]
             for i in range(orb_data['nbas'])]
    else:
        mo_energies_filter = [True] * orb_data['nbas']

    # occupation number range
    if occ_range:
        mo_occ_filter = \
            [occ_range[0] <= orb_data['mo_occupations'][i] <= occ_range[1]
             for i in range(orb_data['nbas'])]
    else:
        mo_occ_filter = [True] * orb_data['nbas']

    # orbital type (index)
    index_filter = [i in set(index) for i in orb_data['mo_types']]

    # all filters must be true for MO to be included in report
    mo_filter = \
        [all(criteria)
         for criteria in zip(mo_energies_filter, mo_occ_filter, index_filter)]

    # Write MO data
    if wfmode:
        write_report(
            sorted_percentages,
            sorted_idx,
            group_labels,
            orb_data['mo_energies'],
            orb_data['mo_occupations'],
            orb_data['mo_types'],
            wfmode=True,
            mo_coeff=_mo_vecs,
            fileobj=fout,
            thr=thr,
            signed_occ=signed_occ,
            mo_filter=mo_filter
        )
    else:
        write_report(
            sorted_percentages,
            sorted_idx,
            group_labels,
            orb_data['mo_energies'],
            orb_data['mo_occupations'],
            orb_data['mo_types'],
            fileobj=fout,
            thr=thr,
            signed_occ=signed_occ,
            mo_filter=mo_filter,
            total_content_choice=user_total_content_choice
        )

    if outfile is None:
        fout.close()


def rotate_spaces(orbname, swap_orb, swap_space, outfile="ModOrb"):
    """
    Rotate orbitals between different active spaces in molcas orbital
    text file and print new orbital file

    Parameters
    ----------
    orbname : str
        name of plain text orb file
    swap_orb : list
        List of orbital indices (1 indexed) which will be moved, commensurate
        with swap_space
    swap_space : list
        List of orbital spaces (f,i,1,2,3,s,d) which orbitals will be moved
        into, commensurate with swap_orb
    outfile : str, default "ModOrb"
        Name of output file containing rotated orbital spaces

    Returns
    -------
    None
    """

    data_dict = parse_orbfile(orbname)

    # Change elements of table
    for orb, space in zip(swap_orb, swap_space):
        data_dict["mo_types"][orb-1] = space

    # Write new file
    create_orbfile(data_dict, outfile)

    return


def reorder_orbitals(orbname, swap_list, outfile="ModOrb"):
    """
    Reorder orbitals in RasOrb file while keeping their space index the same
    and print new orbital file

    Parameters
    ----------
    orbname : str
        name of plain text orb file
    swap_list : list of lists
        List of [initial, final] pairs for swaps, zero indexed
    outfile : str, default "ModOrb"
        Name of output file containing rotated orbital spaces

    Returns
    -------
    None
    """

    # Extract MO data from file
    data_dict = parse_orbfile(orbname)

    # MO Vectors
    for (ini, fin) in swap_list:
        data_dict["mo_vecs"][:, [ini, fin]] = data_dict[
            "mo_vecs"
            ][:, [fin, ini]]

    # MO Energies
    for (ini, fin) in swap_list:
        data_dict["mo_energies"][[ini, fin]] = data_dict[
            "mo_energies"
            ][[fin, ini]]

    # Occupation Numbers
    for (ini, fin) in swap_list:
        data_dict["mo_occupations"][[ini, fin]] = data_dict[
            "mo_occupations"
            ][[fin, ini]]

    # INDEX
    for (ini, fin) in swap_list:
        data_dict["mo_types"][[ini, fin]] = data_dict[
            "mo_types"
            ][[fin, ini]]

    # Write new file
    create_orbfile(data_dict, outfile)

    return


def generate_rasorb(infile,outfile,alpha=False,beta=False,root=0):
    """
    Read in h5 file and write out RasOrb file for average orbitals, or
    orbitals for a specific root

    Parameters
    ----------
    infile : str
        name of input file
    outfile : str
        name of output file
    alpha : bool, default False
        read alpha MOs instead of natural MOs (UHF data only)
    beta : bool, default False
        read beta MOs instead of natural MOs (UHF data only)
    root : int, default 0
        index for outputting root MOs
        if 0, output average MOs

    Returns
    -------
    None
    """

    #Read in h5 file
    basis_only = False
    data = h5tools.read_h5(infile,basis_only,alpha,beta)
    data['nbas_orb'] = data.pop('nbas')

    #Replace average MO vectors and occupancies with those for a
    #specific root
    if root > 0:
        data = average_to_root(data,root)

    #Write new RasOrb file
    create_orbfile(data,outfile)

    return

