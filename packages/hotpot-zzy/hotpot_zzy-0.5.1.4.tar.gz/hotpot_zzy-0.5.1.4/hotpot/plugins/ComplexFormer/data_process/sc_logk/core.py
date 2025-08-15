# -*- coding: utf-8 -*-
"""
===========================================================
 Project   : hotpot
 File      : sc_logk
 Created   : 2025/7/7 13:21
 Author    : zhang
 Python    : 
-----------------------------------------------------------
 Description
 ----------------------------------------------------------
 
===========================================================
"""
import os.path as osp
from tqdm import tqdm

import numpy as np
import pandas as pd

import torch

import hotpot as hp
from hotpot.utils.mp import mp_run
from hotpot.plugins.PyG.data.utils import *

from hotpot.plugins.ComplexFormer.data_process.sc_logk.data import ExtractionData


__all__ = [
    'mp_process_SclogK'
]


# Define constants in ScLogK database
_exclude_ions = {'UO2', 'VO', 'NpO2', 'PuO2', 'PuO', 'PoO', 'MoO2', 'AmO2', 'PaO2', 'TcO', 'ZrO', 'Hg2'}
sc_cols = [
    'W', 'number', 'Tech.', 'SMILES', 'Metal', 'Medium', 'Med_cid', 'Sol1',
    'Sol1_cid', 'Sol2', 'Sol2_cid', 'Sol1Ratio', 'Sol2Ratio', 'RatioMetric',
    't', 'I-str', 'pH', 'P/bar', 'logK1'
]
med_info_names = ['names', 'CASs', 'formulas', 'smiless', 'Cid']
med_attr_names = [
    'MW', 'similarity_variables', 'Vmg_STPs', 'rhog_STPs',
    'rhog_STPs_mass', 'similarity_variable', 'Cpg', 'Cpgm', 'Cpl',
    'Cplm', 'Cps', 'Cpsm', 'Cvg', 'Cvgm', 'isentropic_exponent', 'JTg',
    'kl', 'rhog', 'SGg', 'Density_medium (kg/m3)',
    'Molar Mass_medium (g/mol)', 'Tm_medium (K)'
]
sol_info_names = ['names', 'CASs', 'formulas', 'Cid', 'smiless']
sol_attr_names = [
    'Hvap_298s', 'Hvap_298s_mass', 'Hvap_Tbs', 'Hvap_Tbs_mass', 'MW', 'omegas',
    'Parachors', 'Pcs', 'Psat_298s', 'Pts', 'rhol_STPs', 'rhol_STPs_mass',
    'similarity_variables', 'StielPolars', 'Tbs', 'Tcs', 'Tms', 'Tts',
    'Van_der_Waals_areas', 'Van_der_Waals_volumes', 'Vml_STPs', 'Vml_Tms',
    'UNIFAC_Rs', 'UNIFAC_Qs', 'rhos_Tms', 'Vms_Tms', 'rhos_Tms_mass',
    'Vml_60Fs', 'rhol_60Fs', 'rhol_60Fs_mass', 'rhog_STPs_mass',
    'sigma_STPs', 'sigma_Tms', 'sigma_Tbs'
]

def split_metal(metal_info: str):
    if '+' in metal_info:
        sign = '+'
    elif '-' in metal_info:
        sign = '-'
    else:
        raise ValueError('Invalid metal_info')

    metal, charge = metal_info.split('+')
    metal = metal.strip()
    charge = int(charge.strip())

    if sign == '-':
        charge = -charge

    return metal, charge


def _process_single_SclogK(
        i: int,
        row: pd.Series,
        sol: pd.DataFrame,
        med: pd.DataFrame,
        data_dir: str
):
    smi = row['SMILES'].strip()
    mol = next(hp.MolReader(smi, fmt='smi'))

    metal_sym, charge = split_metal(row['Metal'])

    try:
        mol.create_atom(
            symbol=metal_sym,
            formal_charge=charge,
        )
    except ValueError:
        return metal_sym

    mol.add_hydrogens()
    graph_data: dict = graph_extraction(mol)

    # Compile solvent info
    sol_attr_length = len(sol_attr_names)
    sol1name, sol1id = row[['Sol1', 'Sol1_cid']]
    sol2name, sol2id = row[['Sol2', 'Sol2_cid']]

    sol1_info = sol.loc[sol1id, sol_info_names]
    sol1_attr = torch.tensor(
        np.float64(sol.loc[sol1id, sol_attr_names].values),
        dtype=torch.float
    ).reshape((1, -1))  # attr Tensor [[0.8541, 1.675, ...]], dim=2
    try:
        sol1_smi = sol1_info['smiless'].strip()
    except Exception as e:
        print(sol1_info['smiless'])
        raise e

    solvent1 = hp.read_mol(sol1_smi, fmt='smi')
    solvent1.add_hydrogens()
    sol1_graph: dict = graph_extraction(solvent1, 'sol1', with_batch=True)

    sol1_info = sol1_info.tolist()

    if not np.isnan(sol2id):
        sol2_info = sol.loc[sol2id, sol_info_names]
        sol2_attr = torch.tensor(
            np.float64(sol.loc[sol2id, sol_attr_names].values),
            dtype=torch.float
        ).reshape((1, -1))

        sol2_smi = sol2_info['smiless'].strip()
        solvent2 = hp.read_mol(sol2_smi, fmt='smi')
        solvent2.add_hydrogens()
        sol2_graph: dict = graph_extraction(solvent2, 'sol2', with_batch=True)

        sol2_info = sol2_info.tolist()

    else:
        sol2_info = []
        sol2_attr = torch.zeros(sol_attr_length, dtype=torch.float).reshape((1, -1))
        sol2_graph: dict = graph_extraction(None, 'sol2', with_batch=True)

    if sol2_info:
        sol_ratio = torch.tensor(row[['Sol1Ratio', 'Sol2Ratio']].tolist(), dtype=torch.float).reshape((1, -1))
        assert not sol_ratio.isnan().any().tolist(), f"Found NaN {sol_ratio} in {i} and number={row['number']}"
        sol_ratio = sol_ratio / torch.sum(sol_ratio)
        sol_ratio_metric = row['RatioMetric']
        if pd.isna(sol_ratio_metric):
            sol_ratio_metric = torch.tensor([0], dtype=torch.int8)
        elif sol_ratio_metric == 'Vol':
            sol_ratio_metric = torch.tensor([1], dtype=torch.int8)
        elif sol_ratio_metric == 'Wgt':
            sol_ratio_metric = torch.tensor([2], dtype=torch.int8)
        elif sol_ratio_metric == 'Mol':
            sol_ratio_metric = torch.tensor([2], dtype=torch.int8)
            sol1_Mw = sol.loc[sol1id, 'MW']
            sol2_Mw = sol.loc[sol2id, 'MW']

            sol_ratio = sol_ratio.flatten()
            weighted_ratio = torch.tensor([sol_ratio[0] * sol1_Mw, sol_ratio[1] * sol2_Mw], dtype=torch.float)
            sum_weight = sol_ratio[0] * sol1_Mw + sol_ratio[1] * sol2_Mw
            sol_ratio = (weighted_ratio / sum_weight).reshape((1, -1))

    else:
        sol_ratio = torch.tensor([[1, 0]], dtype=torch.float)
        sol_ratio_metric = torch.tensor([-1], dtype=torch.int8)

    assert not sol_ratio.isnan().any().tolist()

    # Compile Medium Info
    med_name, med_id = row[['Medium', 'Med_cid']]
    if med_id == 0:
        med_info = ['Inf.Dilute', '0000-00-0', '', 0, '']
        med_attr = torch.zeros(len(med_attr_names), dtype=torch.float).reshape((1, -1))

        med_graph: dict = graph_extraction(None, 'med', with_batch=True)

    else:
        med_info = med.loc[med_id, med_info_names]
        med_attr = torch.tensor(med.loc[med_id, med_attr_names].tolist(), dtype=torch.float).reshape((1, -1))

        med_smi = med_info['smiless'].strip()
        medium = next(hp.MolReader(med_smi, fmt='smi'))
        medium.add_hydrogens()
        med_graph: dict = graph_extraction(medium, 'med', with_batch=True)

        med_info = med_info.tolist()

    mol_level_info_names = ['t', 'I-str', 'pH', 'P/bar']
    mol_level_info = torch.from_numpy(np.float64(row[mol_level_info_names].values.flatten()))

    y_names = ['logK1']
    y = torch.tensor(row[y_names].tolist(), dtype=torch.float).reshape(1, -1)

    other_info_names = ['W', 'Tech.', 'Metal', 'Medium', 'Med_cid', 'Sol1', 'Sol1_cid', 'Sol2', 'Sol2_cid']
    other_info = row[other_info_names].tolist()

    data = ExtractionData(
        sol1_info=sol1_info,
        sol1_attr=sol1_attr,
        sol2_info=sol2_info,
        sol2_attr=sol2_attr,
        sol_info_names=sol_info_names,
        sol_attr_names=sol_attr_names,
        sol_ratio=sol_ratio,
        sol_ratio_metric=sol_ratio_metric,
        med_info=med_info,
        med_attr=med_attr,
        med_info_names=med_info_names,
        med_attr_names=med_attr_names,
        mol_level_info=mol_level_info,
        mol_level_info_names=mol_level_info_names,
        y=y,
        y_names=y_names,
        identifier=str(i),
        smiles=smi,
        other_info=other_info,
        other_info_names=other_info_names,
        **graph_data,
        **sol1_graph,
        **sol2_graph,
        **med_graph
    )
    torch.save(data, osp.join(data_dir, f"{data.identifier}.pt"))
    return None

def mp_process_SclogK(path_raw: str, data_dir: str, store_metal_cluster: bool = False):
    df = pd.read_excel(osp.join(path_raw, 'Sc.xlsx'))
    med = pd.read_excel(osp.join(path_raw, 'MedProp.xlsx'), sheet_name='clean')
    sol = pd.read_excel(osp.join(path_raw, 'SolProp.xlsx'), sheet_name='clean')

    med.index = med['Cid'].tolist()
    sol.index = sol['Cid'].tolist()

    args = [
        (i, row, sol, med, data_dir)
        for i, row in tqdm(df.iterrows(), 'Propering Argumnets', total=len(df))
    ]

    results = mp_run(_process_single_SclogK, args, error_to_None=False)
    results.remove(None)
    metal_clusters = set(results)

    if store_metal_cluster and metal_clusters:
        print(metal_clusters)
        metal_clusters = pd.Series(list(metal_clusters))
        with pd.ExcelWriter(path_raw, mode='a') as writer:
            metal_clusters.to_excel(writer, sheet_name='metal_clusters')
