#!/usr/bin/env python

"""
"""

import argparse
from datetime import datetime
import logging
import sys

from MDAnalysis import Universe

import waterEntropy.recipes.interfacial_solvent as GetSolvent


def run_waterEntropy(
    file_topology="file_topology",
    file_coords="file_coords",
    file_forces="file_forces",
    file_energies="file_energies",
    list_files="list_files",
    start="start",
    end="end",
    step="step",
):
    # pylint: disable=all
    """ """

    startTime = datetime.now()
    print(startTime)

    # load topology and coordinates
    u = Universe(file_topology, file_coords)
    # set the frames to be analysed
    # start, end, step = 0, 4, 2
    print(u.trajectory)
    # u.trajectory[frame] # move to a particular frame using this

    # get the coordination shells of water molecules at interfaces
    frame_solvent_shells = GetSolvent.get_interfacial_shells(u, start, end, step)
    # print out the UA indices in the shells of each interfacial water index
    GetSolvent.print_frame_solvent_shells(frame_solvent_shells)

    sys.stdout.flush()
    print(datetime.now() - startTime)


def main():
    """ """
    try:
        usage = "runWaterEntropy.py [-h]"
        parser = argparse.ArgumentParser(
            description="Program for reading "
            "in molecule forces, coordinates and energies for "
            "entropy calculations.",
            usage=usage,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
        parser.add_argument_group("Options")
        parser.add_argument(
            "-top",
            "--file_topology",
            metavar="file",
            default=None,
            help="name of file containing system topology.",
        )
        parser.add_argument(
            "-crd",
            "--file_coords",
            metavar="file",
            default=None,
            help="name of file containing coordinates.",
        )
        parser.add_argument(
            "-frc",
            "--file_forces",
            metavar="file",
            default=None,
            help="name of file containing forces.",
        )
        parser.add_argument(
            "-ener",
            "--file_energies",
            metavar="file",
            default=None,
            help="name of file containing energies.",
        )
        parser.add_argument(
            "-l",
            "--list_files",
            action="store",
            metavar="file",
            default=False,
            help="file containing list of file paths.",
        )
        parser.add_argument(
            "-s",
            "--start",
            action="store",
            metavar="int",
            default=0,
            help="frame number to start analysis from.",
        )
        parser.add_argument(
            "-e",
            "--end",
            action="store",
            metavar="int",
            default=1,
            help="frame number to end analysis at.",
        )
        parser.add_argument(
            "-dt",
            "--step",
            action="store",
            metavar="int",
            default=1,
            help="steps to take between start and end frame selections.",
        )
        op = parser.parse_args()
    except argparse.ArgumentError:
        logging.error(
            "Command line arguments are ill-defined, please check the arguments."
        )
        raise
        sys.exit(1)

    run_waterEntropy(
        file_topology=op.file_topology,
        file_coords=op.file_coords,
        file_forces=op.file_forces,
        file_energies=op.file_energies,
        list_files=op.list_files,
        start=op.start,
        end=op.end,
        step=op.step,
    )


if __name__ == "__main__":
    main()
