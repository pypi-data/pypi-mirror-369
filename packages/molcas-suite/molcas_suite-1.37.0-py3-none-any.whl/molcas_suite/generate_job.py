"""
This module contains functions for generating molcas job scripts
"""

import os
import stat
import sys
import inspect
from .extractor import read_elec_orb, read_rasscf_orb, read_completion,\
                       check_single_aniso
import hpc_suite as hpc
from hpc_suite.generate_job import parse_hostname


def gen_submission(project_name,
                   input_name=None, output_name=None, err_name=None,
                   molcas_module=None, molcas_path=None,
                   memory=None, disk=None, scratch=None, in_scratch=None,
                   omp=1, mpi=1, hpc_args=[]):
    """
    Create submission script for a single molcas calculation.

    Parameters
    ----------
        project_name : str
            Molcas project name
        input_name : str, optional
            Name of molcas input file, default is project_name + .input
        output_name : str, optional
            Name of molcas output file, default is project_name + .out
        err_name : str, optional
            Name of molcas error file, default is project_name + .err
        molcas_module : str, default "apps/gcc/openmolcas/latest" (CSF)
            Path to molcas module for module load command
        molcas_path : str, default "/opt/OpenMolcas-21.06-hyperion" (Cerberus)
            Path to molcas executables
        memory : int, optional
            Amount of memory given to molcas in MB
        disk : int, optional
            Amount of disk given to molcas in MB
        scratch : str, optional
            Path to the scratch directory
        in_scratch : bool, optional
            Flag to indicate if Molcas is run entirely in scratch
        hpc_args : list
            List of unparsed extra arguments known to the parser of hpc_suite's
            generate_job programme

    Returns
    -------
        None
    """

    args = hpc.read_args(['generate_job'] + hpc_args)

    if args.profile == 'read_hostname':
        machine = parse_hostname()
    else:
        machine = args.profile

    supported_machines = [
        "cerberus",
        "medusa",
        "csf3",
        "csf4",
        "gadi"
    ]

    if machine not in supported_machines:
        sys.exit("Error: Unsupported machine")
    
    default_mod = {
        "cerberus": None,
        "medusa": None,
        "csf3": "chiltongroup/openmolcas/24.06",
        "csf4": "chiltongroup/openmolcas/23.02",
        "gadi": "chiltongroup/openmolcas/24.06_mpi"
    }

    default_path = {
        "cerberus": "/opt/OpenMolcas-21.06-hyperion",
        "medusa": "/opt/OpenMolcas-30jun21",
        "csf3": None,
        "csf4": None,
        "gadi": None
    }
    default_mem = {
        "cerberus": {
            None: 30000
        },
        "medusa": {
            None: 30000
        },
        "csf3": {
            None: 4000,
            "high_mem": 16000
        },
        "csf4": {
            None: 4000
        },
        "gadi": {
            None: 3500,
            "normal":3500,
            "normalbw":7500,
            "hugemem":30000,
            "hugemembw":36000,
        },
    }

    default_disk = {
        "cerberus": 20000,
        "medusa": 20000,
        "csf3": 200000,
        "csf4": 200000,
        "gadi": 200000,
    }

    default_scratch = {
        "cerberus": r"$CurrDir/scratch",
        "medusa": r"$CurrDir/scratch",
        "csf3": r"/scratch/$USER/$MOLCAS_PROJECT.$SLURM_JOB_ID",
        "csf4": r"/scratch/$USER/$MOLCAS_PROJECT.$SLURM_JOB_ID",
        "gadi": r"/scratch/ls80/$USER/$MOLCAS_PROJECT.$PBS_JOBID"
    }

    default_in_scratch = {
        "cerberus": True,
        "medusa": True,
        "csf3": False,
        "csf4": False,
        "gadi": False,
    }

    default_node_type = {
        "cerberus": None,
        "medusa": None,
        "csf3": None,
        "csf4": None,
        "gadi": "normalbw",
    
    }

    # Fetch defaults if not set explicitly
    if molcas_module is None and molcas_path is None:
        molcas_module = default_mod[machine]
        molcas_path = default_path[machine]

    # check if requested molcas version is valid
    if molcas_module is None and molcas_path is None:
        sys.exit("Error: No Molcas version specified!")
    elif molcas_module and molcas_path:
        sys.exit("Error: Ambiguous Molcas version specified!")
    
    # set default node type
    args.node_type = default_node_type[machine] \
        if args.node_type is None else args.node_type 

    if not omp:
        if machine == "gadi":
            omp = 2
        else:
            omp = 1
    
    if not mpi:
        mpi = 1
        
    # if mpi threads is greater than one, set args.omp (total number of CPUs, for 
    # hpc_suite).
    args.omp = omp * mpi

    memory_per_core = default_mem[machine][args.node_type] 
    memory = memory_per_core * omp * mpi
    # if memory is set, check enough CPUs are requested            
    
    disk = default_disk[machine] if disk is None else disk
    scratch = default_scratch[machine] if scratch is None else scratch
    in_scratch = default_in_scratch[machine] \
        if in_scratch is None else in_scratch

    # Set environmental variables

    if molcas_path:  # add MOLCAS variable to env
        args.env_vars['MOLCAS'] = molcas_path

    args.env_vars["MOLCAS_PROJECT"] = project_name
    args.env_vars["MOLCAS_MEM"] = str(int(memory_per_core * omp))
    args.env_vars["MOLCAS_THREADS"] = str(omp)
    args.env_vars["MOLCAS_NPROCS"] = str(mpi)
    args.env_vars["MOLCAS_DISK"] = str(disk)
    args.env_vars["MOLCAS_PRINT"] = str(2)
    args.env_vars["MOLCAS_MOLDEN"] = "ON"
    args.env_vars["CurrDir"] = r"$(pwd -P)"
    args.env_vars["WorkDir"] = scratch

    # Set molcas module
    if molcas_module:
        args.modules.append(molcas_module)

    # Set job, input, output and error names
    args.job_name = project_name if args.job_name is None else args.job_name
    input_name = '$MOLCAS_PROJECT.input' if input_name is None else input_name
    output_name = '$MOLCAS_PROJECT.out' if output_name is None else output_name
    err_name = '$MOLCAS_PROJECT.err' if err_name is None else err_name

    if in_scratch:
        input_name = '/'.join(["$CurrDir", input_name])
        output_name = '/'.join(["$CurrDir", output_name])
        err_name = '/'.join(["$CurrDir", err_name])

    # Define call to pymolcas
    pymolcas_args = "{} 2>> {} 1>> {}".format(
        input_name, err_name, output_name
    )

    body_mkdir = "mkdir -p $WorkDir"
    body_cd = "cd $WorkDir" if in_scratch else ""

    # Define Body
    if molcas_module: 
        body = f"pymolcas {pymolcas_args}\n"
    else:
        body = f"$MOLCAS/pymolcas {pymolcas_args}\n"

    args.body = '\n'.join([body_mkdir, body_cd, body])
    # Generate job submission script
    hpc.generate_job_func(args)


