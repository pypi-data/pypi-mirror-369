import os.path as osp
from glob import glob
from typing import Iterable
from operator import attrgetter

from tqdm import tqdm
import numpy as np
import torch

from hotpot.cheminfo.core import Molecule, Atom, AtomPair
from .consts import *

__all__ = [
    "direct_edge_to_indirect",
    "extract_atom_attrs",
    "extract_bond_attrs",
    "extract_atom_pairs",
    "extract_ring_attrs",
    "merge_individual_data_to_block",
    "make_empty_graph",
    "graph_extraction"
]

def make_empty_graph(prefix: str = ''):
    return {
        f'{prefix}x': torch.empty((0, 16), dtype=torch.float),
        f'{prefix}x_names': [],
        f'{prefix}edge_index': torch.empty((2, 0), dtype=torch.long),
        f'{prefix}edge_attr': torch.empty((0, len(edge_attr_names)), dtype=torch.float),
        f'{prefix}edge_attr_names': [],
        f'{prefix}pair_index': torch.empty((2, 0), dtype=torch.long),
        f'{prefix}pair_attr': torch.empty((0, num_atom_pair_attr), dtype=torch.float),
        f'{prefix}pair_attr_names': [],
        f'{prefix}mol_rings_nums': torch.zeros(1, dtype=torch.int),
        f'{prefix}rings_node_index': torch.empty(0, dtype=torch.long),
        f'{prefix}rings_node_nums': torch.empty(0, dtype=torch.int),
        f'{prefix}mol_rings_node_nums': torch.zeros(1, dtype=torch.int),
        f'{prefix}rings_attr': torch.empty((0, len(rings_attr_names)), dtype=torch.float),
        f'{prefix}rings_attr_names': [],
    }


def graph_extraction(mol: Molecule = None, prefix: str = '', with_batch: bool = False) -> dict:
    if prefix and not prefix.endswith('_'):
        prefix += '_'

    if mol is None:
        graph_data = make_empty_graph(prefix)

    else:
        x, x_names = extract_atom_attrs(mol)

        edge_index, edge_attr = extract_bond_attrs(mol, edge_attr_names)
        pair_index, pair_attr, pair_attr_names = extract_atom_pairs(mol)

        mol_rings_nums, rings_node_index, rings_node_nums, mol_rings_node_nums, rings_attr = (
            extract_ring_attrs(mol, rings_attr_names))

        graph_data = {
            f'{prefix}x': x,
            f'{prefix}x_names': x_names,
            f'{prefix}edge_index': edge_index,
            f'{prefix}edge_attr': edge_attr,
            f'{prefix}edge_attr_names': edge_attr_names,
            f'{prefix}pair_index': pair_index,
            f'{prefix}pair_attr': pair_attr,
            f'{prefix}pair_attr_names': pair_attr_names,
            f'{prefix}mol_rings_nums': mol_rings_nums,
            f'{prefix}rings_node_index': rings_node_index,
            f'{prefix}rings_node_nums': rings_node_nums,
            f'{prefix}mol_rings_node_nums': mol_rings_node_nums,
            f'{prefix}rings_attr': rings_attr,
            f'{prefix}rings_attr_names': rings_attr_names,
        }

    if with_batch:
        graph_data.update({f'{prefix}batch': torch.zeros(len(graph_data[f'{prefix}x']), dtype=torch.long)})

    return graph_data


def direct_edge_to_indirect(attr_or_index: torch.Tensor, is_index=True) -> torch.Tensor:
    """"""
    if is_index:
        return torch.cat([attr_or_index, attr_or_index.flip(0)], dim=1)
    else:
        return torch.cat([attr_or_index, attr_or_index.flip(0)], dim=0)


def extract_atom_attrs(mol: Molecule) -> (torch.Tensor, list):
    x_names = Atom._attrs_enumerator[:15]
    additional_attr_names = ('is_metal',)
    x_names = x_names + additional_attr_names
    additional_attr_getter = attrgetter(*additional_attr_names)
    x = torch.from_numpy(
        np.array([a.attrs[:15].tolist() + [additional_attr_getter(a)] for a in mol.atoms])
    ).float().reshape(-1, 16)

    return x, x_names

def extract_bond_attrs(mol: Molecule, edge_attr_names: Iterable[str]) -> (torch.Tensor, torch.Tensor):
    bond_attr_getter = attrgetter(*edge_attr_names)
    if (link_matrix := mol.link_matrix).ndim == 2:
        edge_index = direct_edge_to_indirect(torch.tensor(link_matrix).T).long()
    else:
        edge_index = torch.empty((2, 0), dtype=torch.long)

    edge_attr = direct_edge_to_indirect(
        torch.from_numpy(np.array([(bond_attr_getter(b)) for b in mol.bonds])), is_index=False
    ).float().reshape(-1, len(edge_attr_names))

    return edge_index, edge_attr

def extract_atom_pairs(mol: Molecule) -> (torch.Tensor, torch.Tensor, list):
    atom_pairs = mol.atom_pairs
    atom_pairs.update_pairs()
    if (idx_matrix := atom_pairs.idx_matrix).ndim == 2:
        pair_index = torch.tensor(idx_matrix).T.long()
    else:
        pair_index = torch.empty((2, 0), dtype=torch.long)

    pair_attr_names = AtomPair.attr_names
    pair_attr = torch.tensor([p.attrs for k, p in atom_pairs.items()]).float().reshape(-1, len(pair_attr_names))

    return pair_index, pair_attr, pair_attr_names

def extract_ring_attrs(mol: Molecule, ring_attr_names: Iterable[str]) -> (torch.Tensor, torch.Tensor):
    rings = mol.ligand_rings

    if rings:
        rings_node_index = [r.atoms_indices for r in rings]
        rings_node_nums = [len(rni) for rni in rings_node_index]

        mol_rings_nums = torch.tensor([len(rings_node_nums)], dtype=torch.long)
        rings_node_index = torch.tensor(sum(rings_node_index, start=[]), dtype=torch.long)
        rings_node_nums = torch.tensor(rings_node_nums, dtype=torch.int)
        mol_rings_node_nums = torch.tensor([rings_node_nums.sum()], dtype=torch.int)

        ring_attr_getter = attrgetter(*ring_attr_names)
        rings_attr = torch.from_numpy(
            np.array([ring_attr_getter(r) for r in rings])
        ).float().reshape(len(rings), len(ring_attr_names))

    else:
        mol_rings_nums = torch.tensor([0], dtype=torch.long)
        rings_node_index = torch.tensor([], dtype=torch.long)
        rings_node_nums = torch.tensor([], dtype=torch.int)
        mol_rings_node_nums = torch.tensor([], dtype=torch.int)
        rings_attr = torch.tensor([], dtype=torch.float).reshape(0, len(ring_attr_names))

    return mol_rings_nums, rings_node_index, rings_node_nums, mol_rings_node_nums, rings_attr


def merge_individual_data_to_block(indiv_data_dir, merged_data_dir, bundle_size: int = 200000):
    """ Merge individual data into block data """
    list_data = []
    total = 0
    for i, p in enumerate(tqdm(glob(osp.join(indiv_data_dir, "*.pt")), 'Merging data'), 1):
        if torch.__version__ >= '2.6':
            list_data.append(torch.load(p, weights_only=False))
        else:
            list_data.append(torch.load(p))

        if i % bundle_size == 0:
            torch.save(list_data, osp.join(merged_data_dir, f"{i}.pt"))
            list_data = []
            total += len(list_data)

    if list_data:
        total += len(list_data)
        torch.save(list_data, osp.join(merged_data_dir, f"{total}.pt"))

