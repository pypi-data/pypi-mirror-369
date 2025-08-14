"""
Functions for common MDAnalysis selections
"""

import numpy as np


def get_selection(system, selection_type: str, indices: list[int]):
    """
    For a list of indices, turn this list into a string and use it
    to select by a particular MDAnalysis selection type e.g. resid or index

    :param system: mdanalysis instance of atoms in a frame
    :param selection_type: string for what selection to make in mdanalysis, e.g
        index, resid
    :param indices: list of numbers corresponding to the atoms or resids to
        select
    """
    idx_str = " ".join(str(n) for n in indices)
    selection = system.select_atoms(f"""{selection_type} {idx_str}""")
    return selection


def find_molecule_UAs(molecule):
    """
    For a given molecule, return the heavy atoms it constitutes

    :param molecule: mdanalysis instance of atoms in a frame
    """
    UAs = molecule.select_atoms("mass 2 to 999")
    return UAs


def find_solute_molecules(system):
    """
    For a given system, find molecules containing more than one UA or is not
    a single UA molecule that contains an oxygen atom and return
    the resids for these molecules. Filter out MDAnalysis definition of water
    molecules by default.

    :param system: mdanalysis instance of atoms in a frame
    """
    atom = system.select_atoms("not water")
    # atom = system.select_atoms("all")
    molecules = atom.fragments
    solute_molecule_resid_list = []
    for molecule in molecules:
        for res in molecule.residues:
            UAs = atom.select_atoms(f"resid {res.resid} and mass 2 to 999")
            if len(UAs) > 1:
                solute_molecule_resid_list.append(res.resid)
            # if heavy atom is not oxygen, treat as solute
            if len(UAs) == 1 and np.floor(UAs[0].mass) != 16:
                solute_molecule_resid_list.append(res.resid)

    return solute_molecule_resid_list


def find_bonded_heavy_atom(atom_idx: int, system):
    """
    for a given atom, if it is a hydrogen, find what heavy atom it is bonded to

    :param atom_idx: atom index to find bonded heavy atom for
    :param system: mdanalysis instance of all atoms in current frame
    """
    atom = system.atoms[atom_idx]
    if atom.mass < 1.1:
        bonded_atoms = system.select_atoms(f"bonded index {atom_idx}")
        bonded_heavy_atoms = bonded_atoms.select_atoms("mass 2 to 999")
        bonded_heavy_atom = bonded_heavy_atoms[0]  # should be a list of one
    else:
        bonded_heavy_atom = atom
    return bonded_heavy_atom


def find_bonded_atoms(atom_idx: int, system):
    """
    for a given atom, find its bonded heavy and H atoms

    :param atom_idx: atom index to find bonded heavy atom for
    :param system: mdanalysis instance of all atoms in current frame
    """
    bonded_atoms = system.select_atoms(f"bonded index {atom_idx}")
    bonded_heavy_atoms = bonded_atoms.select_atoms("mass 2 to 999")
    bonded_H_atoms = bonded_atoms.select_atoms("mass 1 to 1.1")
    return bonded_heavy_atoms, bonded_H_atoms


def guess_length_scale(molecule):
    """Guess what the length scale of the molecule is

    :param molecule: MDAnalysis instance of molecule
    """
    molecule_scale = None
    UAs = find_molecule_UAs(molecule)
    if len(UAs) == 1:
        molecule_scale = "single_UA"
    elif len(UAs) > 1:
        if len(molecule.atoms.residues) > 1:
            molecule_scale = "polymer"
        else:
            molecule_scale = "multiple_UAs"
    else:
        molecule_scale = "no_UA"
    return molecule_scale
