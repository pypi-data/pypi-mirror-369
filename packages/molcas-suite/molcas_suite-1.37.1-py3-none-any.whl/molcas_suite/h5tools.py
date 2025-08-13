"""
This module contains functions for working with hdf5 files
"""

import numpy as np
import h5py


def get_orbtype(h5obj):
    """
    Reads Molcas module and orbital type from an h5py.File object

    Parameters
    ----------
        h5obj : h5py.File
            h5py.File object created for the Molcas .h5 file

    Returns
    -------
        dict
            Keys and (values) are
                'molcas_module' (str)
                'orbtype' (str)
    """
    # All strings from HDF5 files are binary, need to convert them to UTF-8
    data_dict = {
        'molcas_module': str(h5obj.attrs.get('MOLCAS_MODULE'), 'utf-8')
    }
    if data_dict['molcas_module'] in ['SCF', 'GUESSORB']:
        data_dict['orbtype'] = str(h5obj.attrs.get('ORBITAL_TYPE'), 'utf-8')
    else:
        data_dict['orbtype'] = 'RasOrb (average)'
    return data_dict


def get_basis(h5obj):
    """
    Reads information about CGTO basis set from an h5py.File object

    Parameters
    ----------
        h5obj : h5py.File
            h5py.File object created for the Molcas .h5 file

    Returns
    -------
        dict
            Keys and (values) are
                'atom_labels' (list)
                'natoms' (int),
                'bas_ids' (np.ndarray)
                'overlap' (np.ndarray)
                'nbas' (int)
    """
    data_dict = {
        'atom_labels': h5obj.get('CENTER_LABELS')[()],
        'natoms': h5obj.attrs.get('NATOMS_UNIQUE'),
        'bas_ids': h5obj.get('BASIS_FUNCTION_IDS')[()],
        'overlap': h5obj.get('AO_OVERLAP_MATRIX')[()],
        'nbas': (h5obj.attrs.get('NBAS'))[0]
    }

    # Clean atom labels - strip whitespace, capitalise and convert to ndarray
    labels_clean = []
    for lbl in data_dict['atom_labels']:
        labels_clean.append(str(lbl.strip(), 'utf-8').capitalize())
    data_dict['atom_labels'] = np.array(labels_clean, dtype=str)

    # Clean basis id
    data_dict['bas_ids'][:, 0] -= 1  # make atom index start at 0
    # the shell number n starts from 1 regardless of angmom
    # correct this by adding l
    data_dict['bas_ids'][:, 1] += data_dict['bas_ids'][:, 2]

    # Reshape AO overlap matrix
    data_dict['overlap'] = data_dict['overlap'].reshape(
        (data_dict['nbas'], data_dict['nbas'])
    )
    return data_dict


def get_orbitals(h5obj, nbas, alpha=False, beta=False):
    """
    Reads information about molecular orbitals (MOs) from an h5py.File object

    Parameters
    ----------
        h5obj : h5py.File
            h5py.File object created for the Molcas .h5 file
        nbas : int
            basis size
        alpha : bool, default False
            read alpha MOs instead of natural MOs (UHF data only)
        beta : bool, default False
            read beta MOs instead of natural MOs (UHF data only)

    Returns
    -------
        dict
            Keys and (values) are
                'mo_vecs' (np.ndarray),
                'mo_types' (np.ndarray),
                'mo_energies' (np.ndarray),
                'mo_occupations' (np.ndarray)
    """
    if alpha:
        data_dict = {
            'mo_vecs': h5obj.get('MO_ALPHA_VECTORS')[()],
            'mo_types': h5obj.get('MO_ALPHA_TYPEINDICES')[()],
            'mo_energies': h5obj.get('MO_ALPHA_ENERGIES')[()],
            'mo_occupations': h5obj.get('MO_ALPHA_OCCUPATIONS')[()]
        }
    elif beta:
        data_dict = {
            'mo_vecs': h5obj.get('MO_BETA_VECTORS')[()],
            'mo_types': h5obj.get('MO_BETA_TYPEINDICES')[()],
            'mo_energies': h5obj.get('MO_BETA_ENERGIES')[()],
            'mo_occupations': h5obj.get('MO_BETA_OCCUPATIONS')[()]
        }
    else:
        data_dict = {
            'mo_vecs': h5obj.get('MO_VECTORS')[()],
            'mo_types': h5obj.get('MO_TYPEINDICES')[()],
            'mo_energies': h5obj.get('MO_ENERGIES')[()],
            'mo_occupations': h5obj.get('MO_OCCUPATIONS')[()],
            'den_mat': h5obj.get('DENSITY_MATRIX')[()]
        }

    # mo_vecs is 1D, need to reshape it into a square matrix and transpose it
    data_dict['mo_vecs'] = data_dict['mo_vecs'].reshape(nbas, nbas).transpose(1, 0) # noqa
    # Each column in data_dict['mo_vecs'] is now one MO

    # Read type indices and convert to UTF-8
    types_clean = []
    for i in range(nbas):
        types_clean.append(str(data_dict['mo_types'][i], 'utf-8').lower())
    data_dict['mo_types'] = types_clean
    return data_dict


def read_h5(h5name, basis_only=False, alpha=False, beta=False):
    """
    Opens .h5 file from Molcas and reads basis and MO information

    Parameters
    ----------
        h5obj : h5py.File
            h5py.File object created for the Molcas .h5 file
        basis_only : bool, default False
            if True, only read basis information
        alpha : bool, default False
            read alpha MOs instead of natural MOs (UHF data only)
        beta : bool, default False
            read beta MOs instead of natural MOs (UHF data only)

    Returns
    -------
        dict
            Keys and (values) are
                'atom_labels' (list)
                'natoms' (int)
                'bas_ids' (np.ndarray)
                'overlap' (np.ndarray)
                'nbas' (int); if basis_only is False
                additional elements:
                'molcas_module' (str)
                'orbtype' (str)
                'mo_vecs' (np.ndarray)
                'mo_types' (np.ndarray)
                'mo_energies' (np.ndarray)
                'mo_occupations' (np.ndarray)
    """
    data = {}
    with h5py.File(str(h5name), 'r') as f:
        # Read basis info
        data.update(get_basis(f))

        # Read everything else, if required
        if not basis_only:
            data.update(get_orbtype(f))
            if data['orbtype'] != 'SCF-UHF':
                alpha, beta = False, False  # reset alpha and beta if not UHF

            if data['molcas_module'] in ['RASSCF', 'GUESSORB', 'SCF']:
                data.update(
                    get_orbitals(f, data['nbas'], alpha=alpha, beta=beta)
                )
                # for UHF, alpha=False and beta=False reads the
                # unrestricted natural orbitals (UnaOrb)
            else:
                raise ValueError(
                    'The {} module is not supported.'.format(
                        data['molcas_module']
                    )
                )
    return data
