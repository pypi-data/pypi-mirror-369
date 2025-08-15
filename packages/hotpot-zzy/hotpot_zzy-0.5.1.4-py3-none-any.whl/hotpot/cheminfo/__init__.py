"""
python v3.9.0
@Project: hotpot0.5.0
@File   : __init__.py
@Auther : Zhiyuan Zhang
@Data   : 2024/6/1
@Time   : 17:23
"""
from ._io import MolReader, MolWriter
from .core import Molecule, Atom, Bond
from .mol_assemble import *

from .mol_statistics import ComplexStatistics


def read_mol(src, fmt=None, **kwargs):
    return next(MolReader(src, fmt, **kwargs))
