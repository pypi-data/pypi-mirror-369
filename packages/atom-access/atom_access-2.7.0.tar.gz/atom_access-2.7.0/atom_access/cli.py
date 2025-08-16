'''
This module contains the command line interface to atom_access
'''

import argparse
from textwrap import dedent
import numpy as np
import xyz_py as xyzp
from . import utils as ut
from .core import trace_rays, cluster_rays, cluster_size, generate_output
import pickle
import sys
import os


def tracing_func(args):
    '''

    Wrapper function for ray tracing program

    Parameters
    ----------
    args : argparser object
        User arguments

    Returns
    -------
    None
    '''

    # Check requested density
    if args.density < 0:
        ut.cprint('ZCW Densities must be >=0', 'red')
        sys.exit()
    # elif args.density > 16:
    #     ut.cprint('ZCW Densities higher than 16 are not supported', 'red')
    #     sys.exit()

    # Load xyz file
    try:
        xyzp.check_xyz(args.xyz_f_name, allow_nonelements=True)
    except xyzp.XYZError as xe:
        ut.cprint(str(xe), 'red')
        sys.exit(1)
    labels, coords = xyzp.load_xyz(args.xyz_f_name, check=False)
    labels_nn = xyzp.remove_label_indices(labels)

    # Check atom number exists
    args.atom -= 1

    if args.atom < 0 or args.atom > len(labels):
        ut.cprint('Error: Atom index does not exist!', 'red')
        sys.exit(1)

    blocked, unblocked, n_cut = trace_rays(
        labels_nn,
        coords,
        args.atom,
        args.cutoff,
        args.density
    )

    total_rays = len(blocked) + len(unblocked)
    pc_unblocked = len(unblocked) / (total_rays) * 100.

    if not args.quiet:
        ut.cprint(f'\nUsing {total_rays:d} rays', 'blue')
        ut.cprint(
            f'\nCutoff of {args.cutoff:f} Angstroms has been enforced',
            'black_yellowbg'
        )
        ut.cprint(
            f'{n_cut:d} atoms are completely excluded',
            'black_yellowbg'
        )

        ut.cprint(
            f'\n{pc_unblocked:.2f} % of solid angle is visible',
            'green'
        )

    if not len(unblocked):
        if not args.quiet:
            ut.cprint('\nAll rays are blocked', 'red')
        sys.exit()

    # Cluster rays
    cluster_id = cluster_rays(unblocked, args.density)

    # Calculate size of clusters
    clust_percent, _ = cluster_size(cluster_id, total_rays)

    if not args.quiet:
        ut.cprint(
            f'\nThere are {clust_percent.size:d} clusters',
            'green'
        )

        for idx, x in enumerate(clust_percent):
            ut.cprint(
                'Cluster {:d} contains {:.2f} % solid angle'.format(
                    idx + 1, x
                ),
                'green'
            )

    # Get head of xyz file name (i.e. without extension)
    f_head = os.path.splitext(args.xyz_f_name)[0]

    # Print output file
    generate_output(
        f_head, args.density, pc_unblocked, clust_percent, args.cutoff,
        no_header=args.quiet
    )

    # Save rays, and xyz file shifted such that
    # atom of interest is at origin.
    if args.save_rays:
        print()
        _coords = coords - coords[args.atom]
        xyzp.save_xyz(
            f'{f_head}_shift.xyz',
            labels,
            _coords,
            comment=f'{args.xyz_f_name} coordinates shifted by atom_access'
        )
        with open('rays.pickle', 'wb') as f:
            pickle.dump(unblocked, f)
        ut.cprint('Rays pickled to rays.pickle', 'green')

    if args.plot:
        cart_vecs = np.array([ray.cart for ray in unblocked])
        ut.plot_rays(cart_vecs, cluster_id, clust_percent.size, show=True)

    return


def read_args(arg_list=None):
    '''

    Creates parser and subparsers for command line arguments

    Parameters
    ----------
    arg_list : list
        User arguments

    Returns
    -------
    None

    '''

    description = '''
    A program for assessing steric hinderance using ray tracing
    '''

    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.set_defaults(func=tracing_func) # noqa

    parser.add_argument(
        'xyz_f_name',
        help='Name of .xyz file containing atomic coordinates'
    )

    parser.add_argument(
        '-a',
        '--atom',
        help='Index of atom for which %% visible rays is calculated.',
        type=int,
        default=1
    )

    parser.add_argument(
        '-d',
        '--density',
        help=dedent(
            'ZCW integration density.Integer between 0 and 16,'
            ' note - number of points does not increase linearly.\n'
        ),
        type=int,
        default=10
    )

    parser.add_argument(
        '-c',
        '--cutoff',
        help=dedent(
            'Cutoff for intersection distance in Angstroms'
        ),
        default=5.,
        type=float,
    )

    parser.add_argument(
        '-p',
        '--plot',
        help=dedent(
            'Plot unblocked points in browser using Plotly'
        ),
        action='store_true'
    )

    parser.add_argument(
        '-sr',
        '--save_rays',
        help=dedent(
            'Pickle unblocked rays and save xyz file'
        ),
        action='store_true'
    )

    parser.add_argument(
        '-q',
        '--quiet',
        help=dedent(
            'Suppress print to terminal and output file header'
        ),
        action='store_true'
    )

    # If argument list is none, then call function func
    # which is assigned to help function
    args = parser.parse_args(arg_list)
    args.func(args)

    return


def main():
    read_args()
