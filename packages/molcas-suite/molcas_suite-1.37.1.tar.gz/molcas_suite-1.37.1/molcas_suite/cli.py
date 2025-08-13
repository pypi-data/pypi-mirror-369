"""
This module contains the command line interface to molcas_suite
"""

import os
import sys
import argparse
import xyz_py as xyzp
from textwrap import dedent
import h5py
import numpy as np

import hpc_suite as hpc
from hpc_suite.action import OrderedSelectionAction

from . import generate_input
from . import generate_job
from . import extractor
from . import orbs


class ParseExtra(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, [[], {}])
        for key, val in values:
            if val is None:
                getattr(namespace, self.dest)[0].append(key)
            else:
                getattr(namespace, self.dest)[1][key] = val


class QuaxActionMolcas(argparse.Action):
    def __init__(self, option_strings, dest, nargs=1, default=None, type=None,
                 choices=None, required=False, help=None, metavar=None):

        super().__init__(
            option_strings=option_strings, dest=dest, nargs=nargs,
            default=default, type=type, choices=choices, required=required,
            help=help, metavar=metavar
        )

    def __call__(self, parser, namespace, value, option_string=None):

        try:  # import from HDF5 database
            with h5py.File(value[0], 'r') as h:
                quax = h["quax"][...]

        except FileNotFoundError:  # choose coordinate system axis
            # cyclic permutation
            perm = {"x": [1, 2, 0], "y": [2, 0, 1], "z": [0, 1, 2]}[value[0]]
            quax = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])[perm]

        except OSError:
            if os.path.splitext(value[0])[1] in ['.out', '.log']:
                if namespace.basis is None:
                    raise ValueError("Specify --basis before --quax")
                quax = extractor.make_extractor(
                    value[0], ("quax", namespace.basis))[1]
            else:
                quax = np.loadtxt(value[0])

        except:
            raise ValueError("Invalid QUAX specification.")

        setattr(namespace, self.dest, quax)


def generate_input_func(args):
    """
    Wrapper function for command line interface call to generate_input

    Parameters
    ----------
    args : argparser object
        command line arguments

    Returns
    -------
    None

    """
    labels, coords = xyzp.load_xyz(args.xyz_input, capitalise=False, check=False)

    # set output to stem of xyz_input if not supplied
    path = args.xyz_input
    abs_stem = os.path.splitext(path)[0]

    name = args.output if args.output else abs_stem + '.input'

    if args.xfield_input:
        with open(args.xfield_input, 'r') as f:
            xfield = [[float(num) for num in line.split()]
                      for line in f if line.strip() != ""]
    else:
        xfield = None

    generate_input.generate_input(
        labels,
        coords,
        args.central_atom,
        args.charge,
        args.n_active_elec,
        args.n_active_orb,
        args.n_coord_atoms,
        name,
        xfield=xfield,
        kirkwood=args.kirkwood,
        decomp=args.decomp,
        gateway_extra=args.gateway_extra,
        basis_set_central=args.basis_set_central,
        basis_set_coord=args.basis_set_coord,
        basis_set_remaining=args.basis_set_remaining,
        rasscf_extra=args.rasscf_extra,
        high_S_only=args.high_S_only,
        initial_orb=args.initial_orb,
        max_orb=args.max_orb,
        caspt2=args.caspt2,
        caspt2_extra=args.caspt2_extra,
        rassi=args.rassi,
        rassi_extra=args.rassi_extra,
        single_aniso=args.single_aniso,
        single_aniso_extra=args.single_aniso_extra,
        quax=args.quax,
        skip_magneto=args.skip_magneto,
        optics=args.optics,
        x2c=args.x2c
    )


def generate_rasorb_func(args):
    """
    Wrapper function for command line interface call to generate_rasorb

    Parameters
    ----------
    args : argparser object
        command line arguments

    Returns
    -------
    None

    """
    orbs.generate_rasorb(
        infile=args.infile,
        outfile=args.outfile,
        alpha=args.alpha,
        beta=args.beta,
        root=args.root
    )

    return


def generate_job_func(args, unknown_args):
    """
    Wrapper function for command line interface call to gen_submission

    Parameters
    ----------
    args : argparser object
        command line arguments
    unknown_args : list
        unknown command line flags to be passed on to a secondary parser

    Returns
    -------
    None

    """
    path = args.input_name
    base = os.path.basename(path)
    rel_stem = os.path.splitext(base)[0]
    abs_stem = os.path.splitext(path)[0]

    project_name = args.project_name if args.project_name else rel_stem
    output_name = args.output_name if args.output_name else abs_stem + '.out'
    err_name = args.err_name if args.err_name else abs_stem + '.err'

    if args.Help:
        unknown_args.append('--help')

    generate_job.gen_submission(
        project_name=project_name,
        input_name=args.input_name, output_name=output_name, err_name=err_name,
        molcas_module=args.molcas_module, molcas_path=args.molcas_path,
        memory=args.memory, disk=args.disk, scratch=args.scratch,
        in_scratch=args.in_scratch, omp=args.omp, mpi=args.mpi,
        hpc_args=unknown_args)


def extractor_func(args, unknown_args):
    """
    Wrapper function for command line interface call to extractor

    Parameters
    ----------
    args : argparser object
        command line arguments
    unknown_args : list
        unknown command line flags to be passed on to a secondary parser

    Returns
    -------
    None

    """

    selected = args._selection

    if not selected:
        sys.exit("No section selected for extraction!")

    # default filter selection {source: destination}
    default_filter = {
        "quax": {1: ()},  # by default select first occurrence
        "cfp": {1: ()},  # by default select first occurrence
        "timing": hpc.store.keep_all("occurrence")  # by default keep all
    }

    store_args = hpc.read_args(['store'] + unknown_args)

    # set up default filter
    store_args.filter = store_args.filter or \
        [default_filter.get(item, None) for item, _ in selected]

    hpc.store_func(store_args, extractor.make_extractor, selected)


def orbs_func(args):
    """
    Wrapper function for command line interface call to orbs

    Parameters
    ----------
    args : argparser object
        command line arguments

    Returns
    -------
    None

    """
    orbs.orbital_analysis(
        args.h5file,
        orbname=args.orbfile,
        pattern=args.sep,
        thr=args.thr,
        wfmode=args.wf,
        outfile=args.out,
        alpha=args.alpha,
        beta=args.beta,
        root=args.root,
        ener_range=args.ener_range,
        occ_range=args.occ_range,
        index=args.index,
        user_total_content_choice=args.total_content
    )

    return


def rotate_func(args):
    """
    Wrapper function for command line interface call to rotate

    Parameters
    ----------
    args : argparser object
        command line arguments

    Returns
    -------
    None

    """

    # Parse swap string
    swap_orb = []
    swap_space = []
    # Reparse if user has included quotation marks
    if len(args.swap_string) == 1 and args.swap_string[0].count(" ") > 0:
        args.swap_string = args.swap_string[0].split(" ")

    for pair in args.swap_string:
        [index, space] = pair.split("-")
        swap_orb.append(int(index))
        swap_space.append(space)

    orbs.rotate_spaces(
        orbname=args.orbfile,
        swap_orb=swap_orb,
        swap_space=swap_space,
        outfile=args.out
    )

    return


def reorder_func(args):
    """
    Wrapper function for command line interface call to reorder

    Parameters
    ----------
    args : argparser object
        command line arguments

    Returns
    -------
    None

    """

    # Parse swap string
    swap_list = []
    # Reparse if user has included quotation marks
    if len(args.swap_string) == 1 and args.swap_string[0].count(" ") > 0:
        args.swap_string = args.swap_string[0].split(" ")

    for pair in args.swap_string:
        sep = pair.split("-")
        initial = int(sep[0]) - 1
        final = int(sep[1]) - 1
        swap_list.append([initial, final])

    orbs.reorder_orbitals(
        orbname=args.orbfile,
        swap_list=swap_list,
        outfile=args.out
    )

    return


def read_args(arg_list=None):
    """
    Parser for command line arguments. Uses subparsers for individual programs

    Parameters
    ----------
    args : argparser object
        command line arguments

    Returns
    -------
    None

    """

    description = dedent(
        '''
        A package for dealing with OpenMOLCAS input and output files.

        Available programs:
            molcas_suite generate_input ...
            molcas_suite generate_rasorb ...
            molcas_suite generate_job ...
            molcas_suite extractor ...
            molcas_suite orbs ...
            molcas_suite rotate ...
        '''
    )

    epilog = dedent(
        """To display options for a specific program, use molcas_suite PROGRAMNAME -h""" # noqa
    )

    parser = argparse.ArgumentParser(
        description=description,
        epilog=epilog,
        formatter_class=argparse.RawTextHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='prog')

    # Generate Input files

    gen_inp = subparsers.add_parser(
        'generate_input',
        formatter_class=argparse.RawTextHelpFormatter
    )
    gen_inp.set_defaults(func=generate_input_func)

    gen_inp.add_argument(
        'xyz_input',
        type=str,
        help='Input file containing the xyz-coordinates.'
    )

    gen_inp.add_argument(
        'central_atom',
        type=str,
        help='Indexed atomic label of central ion of complex, e.g. "Dy1".'
    )

    gen_inp.add_argument(
        'n_active_elec',
        type=int,
        help='Number of electrons in active space.'
    )

    gen_inp.add_argument(
        'n_active_orb',
        type=int,
        help='Number of orbitals in active space.'
    )

    gen_inp.add_argument(
        'n_coord_atoms',
        type=int,
        help='Number of atoms coordinated to central atom.'
    )

    gen_inp.add_argument(
        'charge',
        type=int,
        default=0,
        help='Molecular charge.'
    )

    gen_inp.add_argument(
        '--output',
        type=str,
        default=None,
        help='Name of resulting OpenMolcas input file.'
    )

    gen_inp.add_argument(
        '--xfield_input',
        type=str,
        default=[],
        help=dedent(
            """\
            Name of the file containing input charges and dipoles in raw format
            Each line contains < x y z q dipx dipy dipz >.
            """
        )
    )

    gen_inp.add_argument(
        '--decomp',
        type=str,
        default="RICD_acCD",
        choices=["High Cholesky", "RICD_acCD"],
        help='Option for two-electron integral decomposition in MOLCAS. (default: RICD_acCD)'
    )

    gen_inp.add_argument(
        '--x2c',
        default=True,
        action=argparse.BooleanOptionalAction,
        help='Use X2C Hamiltonian.'
    )

    gen_inp.add_argument(
        '--gateway_extra',
        type=hpc.cli.make_parse_dict(str, str, key_only=True),
        nargs='+',
        action=ParseExtra,
        default=((), {}),
        help='Additional options for gateway section.'
    )

    gen_inp.add_argument(
        '--basis_set_central',
        type=str,
        default="ANO-RCC-VTZP",
        help='Basis set of the central ion metal ion.'
    )

    gen_inp.add_argument(
        '--basis_set_coord',
        type=str,
        default="ANO-RCC-VDZP",
        help='Basis set of the coordinating atoms.'
    )

    gen_inp.add_argument(
        '--basis_set_remaining',
        type=str,
        default="ANO-RCC-VDZ",
        help='Basis set of the remaining atoms.'
    )

    gen_inp.add_argument(
        '--rasscf_extra',
        type=hpc.cli.make_parse_dict(str, str, key_only=True),
        nargs='+',
        action=ParseExtra,
        default=((), {}),
        help='Additional options for RASSCF section.'
    )

    gen_inp.add_argument(
        '--high_S_only',
        action=argparse.BooleanOptionalAction,
        default=False,
        help='Only consider the highest spin state.'
    )

    gen_inp.add_argument(
        '--initial_orb',
        type=str,
        default=None,
        help='Path to a guess orbital file used in the initial RASSCF call.'
    )

    gen_inp.add_argument(
        '--max_orb',
        type=int,
        default=None,
        help=dedent(
            """\
            Maximum number of RasOrb files to produce one for each root up to
            the specified maximum. Default = number of roots per spin state.
            """
        )
    )

    gen_inp.add_argument(
        '--caspt2',
        action=argparse.BooleanOptionalAction,
        help='Include a CASPT2 section.'
    )

    gen_inp.add_argument(
        '--caspt2_extra',
        type=hpc.cli.make_parse_dict(str, str, key_only=True),
        nargs='+',
        action=ParseExtra,
        default=((), {}),
        help='Additional options for gateway section.'
    )

    gen_inp.add_argument(
        '--rassi',
        default=True,
        action=argparse.BooleanOptionalAction,
        help='Include a RASSI section.'
    )

    gen_inp.add_argument(
        '--rassi_extra',
        type=hpc.cli.make_parse_dict(str, str, key_only=True),
        nargs='+',
        action=ParseExtra,
        default=((), {}),
        help='Additional options for RASSI section.'
    )

    gen_inp.add_argument(
        '--single_aniso',
        action=argparse.BooleanOptionalAction,
        default=True,
        help='Include SINGLE_ANISO section.'
    )

    gen_inp.add_argument(
        '--single_aniso_extra',
        type=hpc.cli.make_parse_dict(str, str, key_only=True),
        nargs='+',
        action=ParseExtra,
        default=((), {}),
        help='Additional options for SINGLE_ANISO section.'
    )

    gen_inp.add_argument(
        '--basis',
        default='j',
        help='Basis of the quax info read from Molcas output.'
    )

    gen_inp.add_argument(
        '--quax',
        action=QuaxActionMolcas,
        help=('Molcas output or HDF5 database containing the rotation matrix '
              'for the CFP reference frame. Use together with --basis. '
              'Alternatively, supply txt file containing the rotation matrix '
              'or x, y, z to pick the cyclically permuted quantisation axis.')
    )

    gen_inp.add_argument(
        '--skip_magneto',
        action=argparse.BooleanOptionalAction,
        default=False,
        help='Skip calculation of magnetic data.'
    )

    gen_inp.add_argument(
        '--kirkwood',
        nargs=3,
        metavar=("eps", "radius", "order"),
        help=('Request Kirkwood reaction field with parameters: dielectric '
              'constant, cavitiy radius in Å, order of multipole expansion.')
        )
    
    gen_inp.add_argument(
        '--optics',
        default=False,
        action=argparse.BooleanOptionalAction,
        help='Include extra keywords in SEWARD and RASSI sections to enable electric dipole and electric quadrupole evaluation.'
    )

    # Generate Jobscript

    job = subparsers.add_parser(
        'generate_job',
        description="""
        Creates shell script for running molcas calculation
        """,
    )

    job.set_defaults(func=generate_job_func)

    job.add_argument(
        '-H', '--Help', const='generate_job',
        action=hpc.SecondaryHelp,
        help='show help message for additional arguments and exit'
    )

    molcas_job = job.add_argument_group('molcas specific arguments')

    molcas_job.add_argument(
        'input_name',
        type=str,
        help='Name of molcas input file.'
    )

    molcas_job.add_argument(
        '--output_name',
        type=str,
        help='Name of molcas output file, default = stem of input + .out'
    )

    molcas_job.add_argument(
        '--err_name',
        type=str,
        help='Name of molcas error file, default = stem of input + .err'
    )

    molcas_job.add_argument(
        '--project_name',
        type=str,
        help='Job name, default = stem of input file name'
    )

    molcas_job.add_argument(
        '--molcas_module',
        type=str,
        help='Path to molcas module.'
    )

    molcas_job.add_argument(
        '--molcas_path',
        type=str,
        help='Path to the molcas executables, e.g. the $MOLCAS env variable'
    )

    molcas_job.add_argument(
        '--scratch',
        type=str,
        help='Path to the molcas scratch directory'
    )

    molcas_job.add_argument(
        '--in_scratch',
        default=None,
        action='store_true',  # todo: change to BooleanOptionalAction
        help='Run Molcas job entirely in scratch'
    )

    molcas_job.add_argument(
        '--memory',
        type=int,
        help='Amount of memory given to molcas in megabytes'
    )

    molcas_job.add_argument(
        '--disk',
        type=int,
        help='Amount of disk given to molcas in megabytes'
    )

    molcas_job.add_argument(
        '--omp',
        type=int,
        default=None,
        help='Number of openMP threads per MPI process. (default: 2 on Gadi, 1 elsewhere)'
    )

    molcas_job.add_argument(
        '--mpi',
        type=int,
        default=None,
        help='Number of MPI processes. Number of CPUs requested is set to n threads * n procs. (default: 1)'
    )


    # Extractor

    extract = subparsers.add_parser(
        'extractor',
        description="""Program which facilitates extraction of data from the
        human-readable text output and *.hdf5 output files from an (Open)Molcas
        calculation.""",
        epilog="""Example: molcas_suite extractor -i dy.out -o CFPs_dy.hdf5
        --cfp j""")

    extract.set_defaults(func=extractor_func)

    extract.add_argument(
        '-H', '--Help', const='store',
        action=hpc.SecondaryHelp,
        help='show help message for additional arguments and exit'
    )

    extract.add_argument(
        '--cfp',
        nargs=1,
        action=OrderedSelectionAction,
        choices=["l", "j", "zeeman"],
        help='extract CFPs (by order)'
    )

    extract.add_argument(
        '--quax',
        nargs=1,
        action=OrderedSelectionAction,
        choices=["l", "j", "zeeman"],
        help='extract quax (by order)'
    )

    extract.add_argument(
        '--rassi',
        nargs='+',
        action=OrderedSelectionAction,
        choices=["SOS_energies", "SOS_coefficients", "SOS_angmom",
                 "HSO_matrix", "SFS_energies", "SFS_angmom", "SFS_AMFIint",
                 "spin_mult", "center_coordinates", "SFS_edipmom",
                 "SOS_edipmom"],
        help='followed by list of items to read from the rassi.h5 file'
    )

    extract.add_argument(
        '--rasscf',
        nargs='+',
        action=OrderedSelectionAction,
        choices=['energies', 'epot', 'efld', 'fldg'],
        help=('followed by list of items to read from the rasscf.h5 file or '
              'molcas output file (by multiplicity)')
    )

    extract.add_argument(
        '--gradients',
        action=OrderedSelectionAction,
        help='extract gradients (by multiplicity/root)'
    )

    extract.add_argument(
        '--nacs',
        nargs='+',
        action=OrderedSelectionAction,
        choices=["total", "CSF", "CI"],
        help=('extract non-adiabatic/derivative coupling vectors '
              '(by multiplicity/root_i/root_j)')
    )

    extract.add_argument(
        '--wf_spec',
        nargs='+',
        action=OrderedSelectionAction,
        choices=extractor.MOLCAS_WF_PRGS,
        help=('extract wave function specification (by multiplicity)')
    )

    extract.add_argument(
        '--timing',
        nargs='+',
        action=OrderedSelectionAction,
        choices=extractor.MOLCAS_PRGS,
        help=('extract timings of specified modules (by order)')
    )

    extract.add_argument(
        '--timestamp',
        nargs='+',
        action=OrderedSelectionAction,
        choices=extractor.MOLCAS_PRGS,
        help=('extract timestamp of specified modules (by order)')
    )

    extract.add_argument(
        '--orbitals',
        nargs='+',
        action=OrderedSelectionAction,
        choices=["ener", "occ", "coef"],
        help='Extract orbital information from the RASSCF section.',
    )

    # Orbital analysis
    orbitals = subparsers.add_parser('orbs')
    orbitals.set_defaults(func=orbs_func)

    orbitals.add_argument(
        'h5file',
        type=str,
        help='OpenMolcas HDF5 file name'
    )

    orbitals.add_argument(
        'orbfile',
        type=str,
        nargs='?',
        default=None,
        help='OpenMolcas ASCII file name (optional)'
             + '- overrides MO information from HDF5 file'
    )

    orbitals.add_argument(
        '--sep',
        type=str,
        default='cnl',
        choices=['c', 'cn', 'cl', 'cnl', 'clm', 'cnlm'],
        help=('Pattern used to separate AO contributions; '
              'string is a subset of c (atom index), '
              'n (shell number), l (angular momentum) '
              'and m (angular momentum projection). Default: cnl')
    )

    orbitals.add_argument(
        '--thr',
        type=float,
        default=1.0,
        help='Percentage threshold for printing contributions'
    )
    orbitals.add_argument(
        '--wf',
        action='store_true',
        default=False,
        help='Enables wf mode. Equivalent to --sep cnlm'
    )
    orbitals.add_argument(
        '--out',
        type=str,
        default=None,
        help='Path to output file for the orbital analysis'
    )

    orbitals.add_argument(
        '--alpha',
        action='store_true',
        default=False,
        help='Print alpha orbitals instead of default'
             + 'natural orbitals (UHF only)'
    )

    orbitals.add_argument(
        '--beta',
        action='store_true',
        default=False,
        help='Print beta orbitals instead of default'
             + 'natural orbitals (UHF only)'
    )

    orbitals.add_argument(
        '--root',
        type=int,
        default=0,
        help='Print root n orbitals instead of average'
    )

    orbitals.add_argument(
        '--ener_range',
        type=float,
        nargs=2,
        default=None,
        help='Energy range of orbitals to print contributions'
    )

    orbitals.add_argument(
        '--occ_range',
        type=float,
        default=None,
        nargs=2,
        help='Occupation range of orbitals to print contributions'
    )

    orbitals.add_argument(
        '--index',
        type=str,
        default='i123s',
        help=('Orbital indices to include, default i123s. i: inactive, '
              '1: RAS1, 2: RAS2, 3: RAS3, s: secondary.')
    )

    orbitals.add_argument(
        '--total_content',
        type=str,
        default=None,
        nargs=2,
        help=('Print total content in each MO of given type, '
              'e.g. C 2p would print the total C 2p %% in each MO, '
              'or C21 2s would print the total C21 2s %% in each MO.')
    )

    # Rotation of spaces
    rotate = subparsers.add_parser('rotate')
    rotate.set_defaults(func=rotate_func)

    rotate.add_argument(
        'orbfile',
        type=str,
        help='OpenMolcas ASCII orbital file name'
    )

    # Green start and end ascii
    sc = '\033[0;32m'
    ec = '\033[0m'

    rotate.add_argument(
        'swap_string',
        type=str,
        nargs='+',
        help='String specifying rotations to perform \
              format is "' + sc + 'x-c y-c z-c ...' + ec +
             '" where orbital space is c = f,i,1,2,3,s,d \
              and orbital number(s) are x, y, z.\
              N.B. quotations should not be included'
    )

    rotate.add_argument(
        '--out',
        type=str,
        default='ModOrb',
        help='Path to output file for rotated orbital file. \
              Default is ModOrb'
    )

    # Rotation of spaces
    reorder = subparsers.add_parser('reorder')
    reorder.set_defaults(func=reorder_func)

    reorder.add_argument(
        'orbfile',
        type=str,
        help='OpenMolcas ASCII orbital file name'
    )

    reorder.add_argument(
        'swap_string',
        type=str,
        nargs='+',
        help='String specifying which orbitals to swap \
              format is "' + sc + 'i-f i-f i-f ...' + ec +
             '" where i is initial and f is final orbital number \
              N.B. quotations should not be included'
    )

    reorder.add_argument(
        '--out',
        type=str,
        default='ModOrb',
        help='Path to output file for reordered orbital file. \
              Default is ModOrb'
    )

    # Write RasOrb from h5

    rasorb = subparsers.add_parser('generate_rasorb')
    rasorb.set_defaults(func=generate_rasorb_func)

    rasorb.add_argument(
        'infile',
        type=str,
        help='Name of input file'
    )

    rasorb.add_argument(
        'outfile',
        type=str,
        help='Name of output file'
    )

    rasorb.add_argument(
        '--alpha',
        action='store_true',
        default=False,
        help='Output alpha orbitals instead of default'
             + 'natural orbitals (UHF only)'
    )

    rasorb.add_argument(
        '--beta',
        action='store_true',
        default=False,
        help='Output beta orbitals instead of default'
             + 'natural orbitals (UHF only)'
    )

    rasorb.add_argument(
        '--root',
        type=int,
        default=0,
        help='Output root n orbitals instead of average'
    )

    # read sub-parser
    parser.set_defaults(func=lambda args: parser.print_help())
    args, unknown_args = parser.parse_known_args(arg_list)

    # select parsing option based on sub-parser
    if args.prog in ['generate_job', 'extractor', 'cfp']:
        args.func(args, unknown_args)
    else:
        args = parser.parse_args(arg_list)
        args.func(args)


def main():
    read_args()
