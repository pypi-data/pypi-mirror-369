"""This module contains functions for extracting data from molcas output and
hdf5 files
"""
import re
from functools import reduce
from itertools import count
import mmap
import h5py
import numpy as np
from hpc_suite.store import RegexExtractor, H5AttrExtractor, H5Extractor, \
        Int, Cmplx, is_hdf5
# from scipy.optimize.optimize import _line_search_wolfe12

MOLCAS_PRGS = ['rasscf', 'caspt2', 'alaska', 'mclr']
MOLCAS_WF_PRGS = ['rasscf', 'caspt2', 'mclr']


def make_extractor(f_molcas, select):
    """Resolve selected extractor.

    Parameters
    ----------
    f_molcas : str
        Molcas text or HDF5 output
    select : tuple of str
        Pair of item and option string

    Returns
    -------
    hpc.Store object
        An extractor inheriting from the hpc.Store base class
    """

    # rasscf datasets
    hdf5_extractors = {
        ("rasscf", item): (ExtractRASSCFH5, {'item': item})
        for item in ["energies"]
    }

    # real valued rassi datasets
    hdf5_extractors.update({
        ("rassi", item): (ExtractRASSIH5, {'item': item})
        for item in ["SOS_energies", "SFS_energies", "SFS_AMFIint",
                     "center_coordinates", "SFS_edipmom"]
    })

    # complex valued rassi datasets
    hdf5_extractors.update({
        ("rassi", item): (ExtractRASSIH5c, {'item': item})
        for item in ["SOS_coefficients", "SOS_angmom",
                     "SFS_angmom", "HSO_matrix", "SOS_edipmom"]
    })

    # integer valued rassi attributes
    hdf5_extractors.update({
        ("rassi", item): (MolcasH5iAttrExtractor, {'item': item})
        for item in ["spin_mult"]
    })

    # plain text output extractors
    txt_extractors = {
        ("gradients", None): (ExtractAlaska, {'item': "gradients"}),
        ("rasscf", "energies"): (ExtractRASSCF, {'item': "energies"}),
        ("rasscf", "epot"): (ExtractRASSCFProperty, {'item': "epot"}),
        ("rasscf", "efld"): (ExtractRASSCFProperty, {'item': "efld"}),
        ("rasscf", "fldg"): (ExtractRASSCFProperty, {'item': "fldg"}),
        ("orbitals", "ener"): (ExtractRASSCFOrbitals, {'item': "orb_ener"}),
        ("orbitals", "occ"): (ExtractRASSCFOrbitals, {'item': "orb_occ"}),
        ("orbitals", "coef"): (ExtractRASSCFOrbitals, {'item': "orb_coef"})
    }

    # SINGLE_ANISO extractors
    txt_extractors.update({
        **{("quax", basis): (ExtractQUAX, {'basis': basis})
           for basis in ['l', 'j', 'zeeman']},
        **{("cfp", basis): (ExtractCFPs, {'basis': basis})
           for basis in ['l', 'j', 'zeeman']}
    })

    # NAC datasets
    txt_extractors.update({
        ("nacs", i): (ExtractAlaska, {'item': '_'.join(["NACs", i])})
        for i in ["CI", "CSF", "total"]
    })

    # wave function specification
    txt_extractors.update({
        ("wf_spec", prog): (ExtractWaveFunctionSpec, {'prog': prog})
        for prog in MOLCAS_WF_PRGS
    })

    # timing and timestamp extractors
    txt_extractors.update({
        ("timing", prog): (ExtractTiming, {'prog': prog})
        for prog in MOLCAS_PRGS
    })

    txt_extractors.update({
        ("timestamp", prog): (ExtractTimestamp, {'prog': prog})
        for prog in MOLCAS_PRGS
    })

    if is_hdf5(f_molcas):
        extractor, kwargs = hdf5_extractors[select]
    else:
        extractor, kwargs = txt_extractors[select]

    return extractor(f_molcas, **kwargs)


class MolcasH5iAttrExtractor(Int, H5AttrExtractor):
    """Extracts MOLCAS *.h5 attributes"""

    def __init__(self, h_file, item=None, label=(), units='dimensionless',
                 fmt='%d', **kwargs):
        """
        Parameters
        ----------
        h_file : str
            Name of Molcas *.h5 output
        item : {"spin_mult"}
            Attribute to read
        """
        args = {
            "spin_mult": ("spin_mult",
                          "spin multiplicities of rassi input states")
        }

        h_dset = {
            "spin_mult": "STATE_SPINMULT"
        }

        super().__init__(h_file, h_dset[item], ('/',), *args[item],
                         label=label, units=units, fmt=fmt, **kwargs)


class MolcasH5Extractor(H5Extractor):
    """Extracts real Molcas *.h5 dataset."""

    def __init__(self, h_file, h_dset, h_grp, title, description,
                 units='au', fmt='% 20.14f', label=(), **kwargs):

        """
        Parameters
        ----------
        h_file : str
            Name of Molcas *.h5 output.
        """

        if description is None:
            with h5py.File(h_file, 'r') as h:
                try:
                    description = h[h_dset].attrs.get("DESCRIPTION").decode()
                except KeyError:
                    pass

        super().__init__(h_file, h_dset, h_grp, title, description,
                         units=units, fmt=fmt, label=label, **kwargs)

    def __iter__(self):

        with h5py.File(self.h_file, 'r') as h:

            try:
                data_real = h['_'.join([self.h_dset, "REAL"])][...]
                data_imag = h['_'.join([self.h_dset, "IMAG"])][...]
                data = self.format_data(data_real, data_imag)
                yield (self.format_label(), data)

            except KeyError:
                data = self.format_data(h[self.h_dset][...])
                yield (self.format_label(), data)


class ExtractRASSCFH5(MolcasH5Extractor):
    """Extracts Molcas *.rasscf.h5 dataset."""

    def __init__(self, h_file, item, label=("multiplicity",), units='au'):
        """
        Parameters
        ----------
        h_molcas : str
            Name of Molcas *.h5 output
        item : {'energies'}
            Item name
        """
        args = {
            "energies": ("ROOT_ENERGIES", ('/',), "SFS_energies", None)
        }

        super().__init__(h_file, *args[item], units=units, label=label)

    def format_label(self):
        with h5py.File(self.h_file, 'r') as h:
            label = h.attrs.get("SPINMULT")
            return (label,)


class ExtractRASSIH5(MolcasH5Extractor):
    """Extracts real Molcas *.rassi.h5 dataset."""
    def __init__(self, h_file, item, units='au'):
        """
        Parameters
            ----------
        h_file : str
            Name of Molcas *.h5 output
        item : {'SOS_energies', 'SFS_energies', 'SFS_angmom', 'SFS_AMFIint'}
            Item name
        """

        args = {
            "SOS_energies": ("SOS_ENERGIES", ('/',), "SOS_energies", None),
            "SFS_energies": ("SFS_ENERGIES", ('/',), "SFS_energies", None),
            "SFS_AMFIint": ("SFS_AMFIINT", ('/',), "SFS_AMFIint", None),
            "center_coordinates": ("CENTER_COORDINATES", ('/',),
                                   "center_coordinates", None),
            "SFS_edipmom": ("SFS_EDIPMOM", ('/',), "SFS_edipmom", None)
        }

        self.item = item

        super().__init__(h_file, *args[item], units=units)

    def format_data(self, data):

        func = {
            "SFS_AMFIint": lambda x: np.array([y.T for y in x])
        }

        return func.get(self.item, lambda x: x)(data)


class ExtractRASSIH5c(Cmplx, MolcasH5Extractor):
    """Extracts complex Molcas *.rassi.h5 dataset."""
    def __init__(self, h_file, item, units='au'):
        """
        Parameters
        ----------
        h_file : str
            Name of Molcas *.h5 output
        item : {'SOS_coefficients', 'SOS_angmom', 'SFS_angmom', 'HSO_matrix'}
            Item name
        """

        args = {
            "SOS_coefficients":
                ("SOS_COEFFICIENTS", ('/',), "SOS_coefficients",
                 "Eigenstates of the spin-orbit Hamiltonian, expressed as "
                 "linear combinations of the spin-free states"),
            "SOS_angmom":
                ("SOS_ANGMOM", ('/',), "SOS_angmom",
                 "Angular momentum components between the spin-orbit states"),
            "SFS_angmom":
                ("SFS_ANGMOM", ('/',), "SFS_angmom",
                 "Angular momentum components between the spin-orbit states"),
            "HSO_matrix":
                ("HSO_MATRIX", ('/',), "HSO_matrix",
                 "The spin-orbit Hamiltonian"),
            "SOS_edipmom":
                ("SOS_EDIPMOM", ('/',), "SOS_edipmom",
                 ("Electric dipole momentum components between the spin-orbit "
                  "states"))
        }

        self.item = item

        super().__init__(h_file, *args[item], units=units)

    def format_data(self, real, imag=0.0):

        func = {
            "SOS_coefficients": lambda x: x.T,
            "SOS_angmom": lambda x: 1.j * np.array([y.T for y in x]),
            "SFS_angmom": lambda x: 1.j * np.array([y.T for y in x]),
            "HSO_matrix": lambda x: x.T,
            "SOS_edipmom": lambda x: np.array([y.T for y in x])
        }

        return func[self.item](Cmplx.format_data(self, real, imag))


class MolcasExtractor(RegexExtractor):
    """Extracts Molcas datasets from plain text output."""
    def __init__(self, prog, *args, **kwargs):
        """
        Parameters
        ----------
        prog : str
            Name of Molcas program in lower case
        """

        super().__init__(*args, **kwargs)

        sep_line = r"(?m:^(?:\(\)){50})\s+"
        self.skip = r"(?m:^(?!(?:\(\)){50}).*$\n)*?"

        self.timestamp = (
            r"\-\-\- Start Module: {} at (?P<dow>\w+) (?P<mon>\w+) "
            r"(?P<dom>\d+) (?P<time>\d+\:\d+\:\d+) (?P<year>\d+) \-\-\-\s+"
        ).format(prog.lower())

        if prog == "single_aniso":  # exception in header naming convention
            self.header = \
                sep_line + r"\&SINGLE_ANISO(_OPEN)?\s+" + self.skip + sep_line
        else:
            self.header = \
                sep_line + r"\&{}\s+".format(prog.upper()) + self.skip + \
                sep_line

        self.wf_spec = (
            r"\+\+\s+Wave function specifications:\s+" +
            re.escape("-----------------------------") + r"\s+" # noqa
            r"Number of closed shell electrons\s+(?P<n_elec_closed>\d+)\s+"
            r"Number of electrons in active shells\s+(?P<n_elec_active>\d+)\s+"
            r"Max number of holes in RAS1 space\s+(?P<n_holes>\d+)\s+"
            r"Max (?:nr|number) of electrons in RAS3 space\s+(?P<n_exc>\d+)\s+"
            r"Number of inactive orbitals\s+(?P<n_inact>\d+)\s+"
            r"Number of active orbitals\s+(?P<n_act>\d+)\s+"
            r"Number of secondary orbitals\s+(?P<n_sec>\d+)\s+"
            r"Spin quantum number\s+(?P<spin_qn>\d+\.\d+)\s+"
            r"State symmetry\s+(?P<symm>\d+)\s+"
        )

        footer = (r"\-\-\- Module {} spent "
                  r"(?:(?{}\d+) days? )?"
                  r"(?:(?{}\d+) hours? )?"
                  r"(?:(?{}\d+) minutes? )?"
                  r"(?{}\d+) seconds? \-\-\-\s+")

        self.footer = footer.format(prog, ":", ":", ":", ":")
        self.timing = footer.format(
            prog, "P<days>", "P<hrs>", "P<mins>", "P<secs>")

        self.sec_pattern = self.skip.join([
            self.header, self.wf_spec, self.footer])


class ExtractWaveFunctionSpec(MolcasExtractor):
    """
    Extracts wave function specification from RASSCF, CASPT2 & MCLR module.
    """
    def __init__(self, txt_file, prog, description=None,
                 label=("multiplicity",), units="dimensionless", fmt='%d'):
        """
        Parameters
        ----------
        txt_file : str
            Molcas text output file
        prog : str
            Molcas program name
        """
        description = description or ', '.join([
            "closed shell elec",
            "active shell elec",
            "holes in RAS1",
            "exc in RAS3",
            "inactive orbs",
            "active orbs",
            "secondary orbs",
            "mulitplicity",
            "symmetry"
        ])

        super().__init__(prog, txt_file, "{}_wf_specification".format(prog),
                         description, label=label, units=units, fmt=fmt)

        self.row_pattern = self.wf_spec

    def format_label(self, spin_qn=None, **kwargs):
        return (int(2 * float(spin_qn)) + 1,)

    def format_data(self, data, n_elec_closed=None, n_elec_active=None,
                    n_holes=None, n_exc=None, n_inact=None, n_act=None,
                    n_sec=None, spin_qn=None, symm=None, **kwargs):
        return np.array([
            int(n_elec_closed),
            int(n_elec_active),
            int(n_holes),
            int(n_exc),
            int(n_inact),
            int(n_act),
            int(n_sec),
            int(2 * float(spin_qn)) + 1,
            int(symm)
        ])


class ExtractTiming(MolcasExtractor):
    """Extracts timing from program footer."""
    def __init__(self, txt_file, prog, description="runtime of module",
                 label="occurrence", units="s", fmt='%d'):
        """
        Parameters
        ----------
        txt_file : str
            Molcas text output file
        prog : str
            Molcas program name
        """

        super().__init__(prog, txt_file, "{}_timing".format(prog), description,
                         label=label, units=units, fmt=fmt)

        self.row_pattern = self.timing

        self.sec_pattern = self.skip.join([self.header, self.timing])

    def format_data(self, data, days=None, hrs=None, mins=None, secs=None,
                    **kwargs):

        time = reduce(lambda x, y: (x + int(y[0] or 0)) * y[1],
                      zip((days, hrs, mins, secs), (24, 60, 60, 1)), 0)

        return np.array([time])


class ExtractTimestamp(MolcasExtractor):
    """Extracts timestamp from module footer."""
    def __init__(self, txt_file, prog, description="timestamp of module",
                 label="occurrence", units="date", fmt='%s'):

        """
        Parameters
        ----------
        txt_file : str
            Molcas text output file
        prog : str
            Molcas program name
        """

        super().__init__(prog, txt_file, "{}_timestamp".format(prog),
                         description, label=label, units=units, fmt=fmt)

        self.row_pattern = self.timestamp

        self.sec_pattern = self.skip.join([
            self.timestamp, self.header, self.footer])

    def format_data(self, data, **kwargs):
        return np.array(["{dow} {mon} {dom} {time} {year}".format(
            **{key: val.decode() for key, val in kwargs.items()})], dtype='S')


class ExtractSingleAniso(MolcasExtractor):
    """Extracts data from the Single Aniso section."""
    def __init__(self, basis, *args, label="occurrence", **kwargs):
        """
        Parameters
        ----------
        basis : {'l', 'j', 'zeeman'}
            Angular momentum basis. 'j' and 'zeeman' are synonymous
        """
        self.basis_line = {
            "j": r"\s+CALCULATION OF CRYSTAL-FIELD PARAMETERS OF THE GROUND ATOMIC MULTIPLET.*\n",  # noqa
            "zeeman": r"\s+CALCULATION OF CRYSTAL-FIELD PARAMETERS OF THE GROUND ATOMIC MULTIPLET.*\n",  # noqa
            "l": r"\s+CALCULATION OF CRYSTAL-FIELD PARAMETERS OF THE GROUND ATOMIC TERM.*\n"  # noqa
        }[basis.lower()]

        super().__init__("single_aniso", *args, label=label, **kwargs)


class ExtractQUAX(ExtractSingleAniso):
    """Extracts QUAX from the Single Aniso section."""
    def __init__(self, txt_file, basis="j", title="quax",
                 description="Quantisation axis", units="dimensionless",
                 fmt=['% 20.14f', '% 20.14f', '% 20.14f']):

        """
        Parameters
        ----------
        txt_file : str
            Molcas text output file
        basis : {'j', 'l'}
            Angular momentum basis
        """

        super().__init__(basis, txt_file, title, description,
                         units=units, fmt=fmt)

        # floating point number starting with - or " "
        self.row_pattern = ' '.join([r"([- ]\d*\.\d+)"] * 3)
        data_pattern = (
            r"(?P<array>"
            r"\-{67}\|\s+"
            r"x , y , z  -- initial Cartesian axes\s+\|\s+"
            r"Xm, Ym, Zm --\s*(?:\w+\s)+\s+\|\s+"
            r"\s+x\s+y\s+z\s+\|\s+"
            r"      \| Xm \| " + self.row_pattern + r" \|\s+"
            r" R =  \| Ym \| " + self.row_pattern + r" \|\s+"
            r"      \| Zm \| " + self.row_pattern + r" \|\s+"
            r"\-{67}\|\s+)"
        )

        self.sec_pattern = self.skip.join([
            self.header, self.basis_line, data_pattern])


class ExtractCFPs(ExtractSingleAniso):
    """Extracts CFPs from the Single Aniso section."""
    def __init__(self, txt_file, basis="j", title="CFPs",
                 description="Crystal field parameters", units="cm^-1",
                 fmt=['% 20.13e']):
        """
        Parameters
        ----------
        txt_file : str
            Molcas text output file
        basis : {'j', 'l'}
            Angular momentum basis
        """
        super().__init__(basis, txt_file, title, description,
                         units=units, fmt=fmt)

        # floating point number in scientific notation starting with - or " "
        self.row_pattern = r"([- ]\d\.\d+E[-+]\d+)"

        pre_lines_1 = [
            r"The Crystal-Field Hamiltonian:",
            r"   Hcf = SUM_{k,q} * [ B(k,q) * O(k,q) ];",
            r"where:",
            r"   O(k,q) =  Extended Stevens Operators (ESO)as defined in:",
            r"          1. Rudowicz, C.; J.Phys.C: Solid State Phys.,18(1985) 1415-1430.",  # noqa
            r'          2. Implemented in the "EasySpin" function in MATLAB, www.easyspin.org.',  # noqa
            r"   k - the rank of the ITO, = 2, 4, 6, 8, 10, 12.",
            r"   q - the component of the ITO, = -k, -k+1, ... 0, 1, ... k;"
        ]

        pre_lines_2 = [
            r"k = 12 may not be the highest rank of the ITO for this case, but it",  # noqa
            r'is the maximal k implemented in the "EasySpin" function in MATLAB.'  # noqa
        ]

        pre_lines_3 = [
            r"Knm are proportionality coefficients between the ESO and operators defined in",  # noqa
            r"J. Chem. Phys., 137, 064112 (2012)."
        ]

        pre_pattern = (
            r"\s+".join([re.escape(line) for line in pre_lines_1]) + r"\s+(" +
            r"\s+".join([re.escape(line) for line in pre_lines_2]) + r"\s+)?" +
            r"\s+".join([re.escape(line) for line in pre_lines_3]) + r"\s+"
        )

        data_pattern = (
            r"(?P<array>"
            r"------------------------------------------------\|\s+"
            r"  k \|  q  \|    \(K\)\^2    \|         B\(k,q\)        \|\s+"
            r"(?:"
            r"----\|-----\|-------------\|-----------------------\|\s+"
            r"(?:\s*\d+ \|\s*-?\d+ \|\s*\d+\.\d+  \| " + self.row_pattern +
            r" \|\s+)+"
            r")+)"
        )

        self.sec_pattern = self.skip.join([
            self.header,
            self.basis_line,
            pre_pattern,
            data_pattern
        ])


def read_completion(f_molcas):
    """
    Checks for completion of molcas calculation

    Parameters
    ----------
        f_molcas : str
            Molcas file name

    Returns
    -------
        bool
            True if calculation finished successfully else False
    """

    happy_landing = False

    for line in reversed(list(open(f_molcas))):
        if "Happy landing!" in line:
            happy_landing = True
            break

    return happy_landing


def check_single_aniso(f_molcas):
    """
    Checks that a single_aniso section is present in the output file

    Parameters
    ----------
        f_molcas : str
            Molcas file name

    Returns
    -------
        bool
            True if section exists, else False

    """
    sa_exists = False

    for line in reversed(list(open(f_molcas))):
        if "CALCULATION OF CRYSTAL-FIELD PARAMETERS OF THE GROUND ATOMIC MULTIPLET" in line: # noqa
            sa_exists = True
            break

    return sa_exists


def read_rasscf_orb(f_molcas, orb_type, threshold=0.01):
    """
    Reads truncated orbital information written in RASSCF section of output
    file. Checks that convergence has been reached, that active space
    orbitals are pure (3d or 4f) functions.

    For more accurate results use the functionality provided in orbs.py

    Parameters
    ----------
        f_molcas : str
            Molcas file name
        orb_type : str {"3d", "4f"}
            Type of orbital expected in active space
        threshold : float, default 0.01
            MOs with % contributions larger than this value from non
            `orb_type` orbitals result in impure active space
    Returns
    -------
        int
            Successful calculation =  0
            No convergence         = -1
            Impure active space    = -2
    """

    if "4f" in orb_type:
        threshold = 0.01
    elif "4f" in orb_type:
        threshold = 0.025

    converged = False
    pure = True

    _, _, n_inact_orb, n_act_orb, n_sec_orb = read_elec_orb(f_molcas)

    n_basis = n_inact_orb + n_act_orb + n_sec_orb

    wavefunc = np.zeros([n_basis, 50])
    atoms = np.zeros(n_basis, dtype='U25')

    with open(f_molcas, 'r') as f:
        for line in f:
            if "Convergence after" in line:
                converged = True

            if "Molecular orbitals for symmetry species 1: a" in line:
                stored = []
                reading_orbs = True
                n_stored = 0
                for _ in range(3):
                    line = next(f)
                while reading_orbs:
                    orb_nums = line.split()[1:]
                    if any([n_inact_orb < int(num) <= n_inact_orb + n_act_orb
                            for num in orb_nums]):
                        for _ in range(3):
                            line = next(f)
                        # Store index of orbitals that have been read in
                        # some of these will not be active and so will
                        # be removed later
                        [stored.append(int(orb)) for orb in orb_nums]

                        # Read in MO coefficients
                        for bit in range(n_basis):
                            line = next(f)
                            # Atom and orbital identities
                            atoms[bit] = line[7:16]
                            # Coefficients
                            _coeffs = [float(val) for val in line.split()[3:]]
                            _n_orbs = len(orb_nums)
                            wavefunc[bit, n_stored:n_stored+_n_orbs] = _coeffs
                        n_stored += _n_orbs
                        if any([int(num) >= n_inact_orb + n_act_orb
                                for num in orb_nums]):
                            reading_orbs = False
                    else:
                        for _ in range(n_basis+3):
                            line = next(f)
                    for _ in range(3):
                        line = next(f)
    # Find index of first active orbital in stored array
    for it, st in enumerate(stored):
        if st == n_inact_orb + 1:
            active_ind = it

    # Calculate % composition of each active orbital
    composition = np.zeros([n_basis, n_act_orb])
    for ait, oit in enumerate(range(active_ind, active_ind + n_act_orb)):
        composition[:, ait] = wavefunc[:, oit]**2.
        sum_of = np.sum(composition[:, ait])
        # Normalise by sum
        composition[:, ait] /= sum_of
        for bit in range(10):
            if composition[bit, ait] >= threshold \
             and atoms[bit][8:] != orb_type:
                pure = False

    if converged and pure:
        return_code = 0
    elif not converged:
        return_code = -1
    elif not pure:
        return_code = -2

    return return_code


def read_elec_orb(f_molcas):
    """
    Reads molcas output and retrieves electron and orbital numbers for
    different RAS spaces

    Parameters
    ----------
        f_molcas : str
            Molcas file name

    Returns
    -------
        list :
            Number of closed shell electrons
            Number of active electrons
            Number of inactive orbitals
            Number of active orbitals
            Number of secondary orbitals

    """
    with open(f_molcas) as f:
        for line in f:
            if "Wave function specifications" in line:
                for _ in range(3):
                    line = next(f)
                n_closed_elec = int(line.split()[5])
                line = next(f)
                n_act_elec = int(line.split()[6])
                for _ in range(3):
                    line = next(f)
                n_inact_orb = int(line.split()[4])
                line = next(f)
                n_act_orb = int(line.split()[4])
                line = next(f)
                n_sec_orb = int(line.split()[4])

                break

    data = [n_closed_elec, n_act_elec, n_inact_orb, n_act_orb, n_sec_orb]

    return data


class ExtractAlaska(MolcasExtractor):
    """Extracts derivative data from Alaska section."""
    def __init__(self, txt_file, item, units="au", fmt=['% 20.14e'] * 3):
        """
        Parameters
        ----------
        txt_file : str
            Molcas text output file
        item : {'gradients', 'NACs_CI', 'NACs_CSF', 'NACs_total'}
            Type of derivative
        """
        # TODO: this has to be checked!
        # inconstency in the molcas output:
        # (either h^ij / scal
        #  or f_CSF^ij * scal)
        # and f_total^ij * scal
        # Also only works with nosymm

        args = {
            "gradients": ("gradients", "Atomic gradients"),
            "NACs_CI": ("NACs_CI",
                        "CI contribution to the derivative coupling"),
            "NACs_CSF": ("NACs_CSF",
                         "CSF contribution to the derivative coupling"),
            "NACs_total": ("NACs_total", "CI/dE + CSF")
        }

        label = ("multiplicity", "root") if item == "gradients" else \
                ("multiplicity", "root_i", "root_j")

        super().__init__("alaska", txt_file, *args[item], label=label,
                         units=units, fmt=fmt)

        mclr = MolcasExtractor("mclr", txt_file, "", "")

        header_line = {
            "gradients": "Molecular gradients",
            "NACs_CI": "CI derivative coupling",
            "NACs_CSF": "CSF derivative coupling",
            "NACs_total": "Total derivative coupling"
        }[item]

        roots_pattern = (
            r"\s+Lagrangian multipliers are calculated for states? "
            r"no.\s+(?P<roots>\d+(\/\s+\d+)?)\s+"
        )

        # floating point number starting with - or " " separated by 3 spaces
        self.row_pattern = r'   '.join([r"([- ]\d\.\d+E[-+]\d+)"] * 3)

        data_pattern = (
            r"(?P<array>"
            r"\s*(\*+\s+\*\s+\*\s+\*\s+" +
            header_line + r"(?: \(divided by (?P<div_by>\d\.\d+E[-+]\d+)\))?"
            r"\s+\*\s+\*\s+\*\s+\*+)(?s:.*?)"
            r"Irreducible representation: a\s+"
            r"\-{90}\s+"
            r"X\s+Y\s+Z\s+"
            r"\-{90}"
            r"(?:\s*\w+\s*" + self.row_pattern + r")+"
            r")\s+"
        )

        # match basis line and data separated by as few lines as possible (.*?)

        self.sec_pattern = self.skip.join([
            mclr.header,
            mclr.wf_spec,
            roots_pattern,
            mclr.footer,
            self.header,
            data_pattern,
            self.footer
        ])

    def format_data(self, data, div_by=None, **kwargs):
        if div_by is None:
            return np.array(data, dtype=float)
        else:
            return np.array(data, dtype=float) * float(div_by)

    def format_label(self, spin_qn=None, roots=None, **kwargs):
        return (int(2 * float(spin_qn)) + 1,
                *[int(root) for root in roots.split(b'/')])


class ExtractRASSCF(MolcasExtractor):
    """Extracts data from the RASSCF section."""
    def __init__(self, txt_file, item, label=("multiplicity",), units='au'):

        """
        Parameters
        ----------
        txt_file : str
            Molcas text output file
        item : {'energies'}
            Item name
        """

        args = {
            "energies": ("energies", "RASSCF root energies"),
            "orbital_coefficients": ("orbital_coefficients", "Orbital coefficient matrix")
        }

        fmt = {
            "energies": '% .8f'
        }

        super().__init__("rasscf", txt_file, *args[item], label=label,
                         units=units, fmt=fmt[item])

        if item == "energies":
            self.row_pattern = r"([- ]\d+\.\d+)"
            data_pattern = (
                r"(?P<array>"
                r"\s+Final state energy\(ies\)\:\s+" +
                r"\s+\-{24}\s+" +
                r"(?:\:\:\s+RASSCF root number\s+\d+ Total energy\:\s+" +
                self.row_pattern + r"\s+)+)"
            )

        self.sec_pattern = self.skip.join([
            self.header,
            self.wf_spec,
            data_pattern,
            self.footer
        ])

        print(self.sec_pattern)

    def format_label(self, spin_qn=None, **kwargs):
        return (int(2 * float(spin_qn)) + 1,)


class ExtractRASSCFProperty(MolcasExtractor):
    """Extracts data from the RASSCF section."""
    def __init__(self, txt_file, item, label=("multiplicity", "root"),
                 units='au'):

        """
        Parameters
        ----------
        txt_file : str
            Molcas text output file
        item : {'energies'}
            Item name
        """

        columns = {
            "epot": [],
            "efld": ["X", "Y", "Z"],
            "fldg": ["(2*XX-YY-ZZ)/2", "1.5*XY", "1.5*XZ", "(2*YY-ZZ-XX)/2",
                     "1.5*YZ", "(2*ZZ-XX-YY)/2", "RR=XX+YY+ZZ"]
        }[item]

        components = ', '.join(columns)

        title = {
            "epot": "electric_potential",
            "efld": "electric_field",
            "fldg": "electric_field_gradient"
        }[item]

        description = {
            "epot": "RASSCF electrostatic potential",
            "efld": f"RASSCF electric field; components: {components}",
            "fldg": f"RASSCF electric field gradient; components: {components}"
        }[item]

        fmt = {
            "epot": '% .8f',
            "efld": '% .8f',
            "fldg": '% .8f'
        }

        super().__init__("rasscf", txt_file, title, description, label=label,
                         units=units, fmt=fmt[item])

        self.row_pattern = {
            "epot": r"([- ]\d+\.\d+)",
            "efld": r'\s+'.join([r"([- ]\d+\.\d+)"] * 3),
            "fldg": r'\s+'.join([r"([- ]\d+\.\d+)"] * 7),
        }[item]

        self.data_pattern = r"(?P<array>\s+" + r'\s+'.join(map(re.escape, {
            "epot": ["Electric potential:"],
            "efld": ["Electric field:"],
            "fldg": ["Electric field gradient:"]
        }[item] + columns)) + r"\s+(?:\d+\s+" + self.row_pattern + r"\s+)+)"

    def format_label(self, spin_qn=None, root=None, **kwargs):
        return (int(2 * float(spin_qn)) + 1, int(root))

    def __iter__(self):

        header = \
            r"\s+Expectation values of various properties for root number\:\s+"

        skip = r"(?m:^(?!{:}).*$\n)*?".format(header)

        root_pattern = skip.join([
            header + r"(?P<root>\d+)\s+\-{59}\s+", self.data_pattern])

        with open(self.txt_file, 'r+b') as f:
            # use mmap to buffer file contents
            # as a result, search pattern has to be encoded to byte string
            content = mmap.mmap(f.fileno(), 0)
            it = re.finditer(self.sec_pattern.encode(), content)

        for m in it:
            # get dictionary of matches
            named = m.groupdict()
            for root in re.finditer(root_pattern.encode(), m.group()):
                # format data
                named_root = root.groupdict()
                data = self.format_data(
                    re.findall(self.row_pattern.encode(), named_root["array"]))

                # generate label
                label = self.format_label(**named, **named_root)

                yield (label, data)


class ExtractRASSCFOrbitals(MolcasExtractor):

    def __init__(self, txt_file, item, label="occurrence", units='au', fmt='% .4f'):

        """
        Parameters
        ----------
        txt_file : str
            Molcas text output file
        item : {'energies'}
            Item name
        """

        title, description = {
            "orb_ener": ("orbital_energies", "Orbital energies"),
            "orb_occ": ("orbital_occupations", "Orbital occupations"),
            "orb_coef": ("orbital_coefficients", "Orbital coefficients")
        }[item]

        super().__init__("rasscf", txt_file, title, description, label=label,
                         units=units, fmt=fmt)

        # \s*- to deal with concatentated negative 4 digit energies
        row_patterns = {
            "orb_ener": r"(?:Energy((?:\s*-?\d+\.\d+)+))",
            "orb_occ": r"(?:Occ\. No\.((?:\s+\d\.\d+)+))",
            "orb_coef": r"(?:\d+ \w+\s+[A-Za-z0-9+-]+((?:\s+\-?\d\.\d+)+))"
        }

        self.item = item
        self.row_pattern = row_patterns[item]

        self.array_pattern = r"\s+".join([
            r"Orbital(?:\s+\d+\s+)+",
            rf"{row_patterns['orb_ener']}",
            rf"{row_patterns['orb_occ']}",
            rf"(?:{row_patterns['orb_coef']}\s+)+"])

    def __iter__(self):

        counter = count(1)

        header = "Molecular orbitals for symmetry species 1: a"
        block_pattern = header + rf"\s+(?:{self.array_pattern})+"

        with open(self.txt_file, 'rb') as f:
            # use mmap to buffer file contents
            # as a result, search pattern has to be encoded to byte string
            content = mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)
            it = re.finditer(self.sec_pattern.encode(), content)

        def array_iter(block):
            for array in re.finditer(self.array_pattern.encode(), block):
                lines = re.findall(self.row_pattern.encode(), array.group(0))
                yield list(map(lambda x: re.findall(r"(-?\d+\.\d+)".encode(), x), lines))

        def block_iter(m):
            for block in re.finditer(block_pattern.encode(), m.group()):
                data = [[elem for line in lines for elem in line]
                        for lines in zip(*array_iter(block.group()))]
                return data

        for m in it:
            yield self.format_label(counter=counter), self.format_data(block_iter(m))

    def format_data(self, data):
        if self.item in ["orb_occ", "orb_ener"]:
            return np.array(data, dtype=float)[0, :]

        return np.array(data, dtype=float)
