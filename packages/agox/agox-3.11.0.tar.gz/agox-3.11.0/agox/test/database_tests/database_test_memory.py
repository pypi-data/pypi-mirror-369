from typing import Dict, List

import numpy as np

from agox.candidates import Candidate
from agox.databases import Database


def test_number_of_candidates(database_created: Database, dataset: List[Candidate]) -> None:
    assert len(database_created) == len(dataset)


def test_positions(database_created: Database, dataset: List[Candidate]) -> None:
    for db_cand, data_cand in zip(database_created.get_all_candidates(), dataset):
        np.testing.assert_allclose(db_cand.positions, data_cand.positions)


def test_cell(database_created: Database, dataset: List[Candidate]) -> None:
    for db_cand, data_cand in zip(database_created.get_all_candidates(), dataset):
        np.testing.assert_allclose(db_cand.cell, data_cand.cell)


def test_pbc(database_created: Database, dataset: List[Candidate]) -> None:
    for db_cand, data_cand in zip(database_created.get_all_candidates(), dataset):
        np.testing.assert_allclose(db_cand.pbc, data_cand.pbc)


def test_meta_keys(database_created: Database, dataset: List[Candidate], meta_dict: Dict) -> None:
    meta_data_names = list(meta_dict.keys())
    for db_cand, data_cand in zip(database_created.get_all_candidates(), dataset):
        for meta_data_name in meta_data_names:
            assert db_cand.get_meta_information(meta_data_name) is not None
            assert data_cand.get_meta_information(meta_data_name) is not None


def test_meta_values(database_created: Database, dataset: List[Candidate], meta_dict: Dict) -> None:
    meta_data_names = list(meta_dict.keys())
    for db_cand, data_cand in zip(database_created.get_all_candidates(), dataset):
        for meta_data_name in meta_data_names:
            db_meta = db_cand.get_meta_information(meta_data_name)
            data_meta = data_cand.get_meta_information(meta_data_name)
            assert np.array(db_meta == data_meta).all()


def test_energies(database_created: Database, dataset: List[Candidate]) -> None:
    database_created_energies = np.array(
        [atoms.get_potential_energy() for atoms in database_created.get_all_candidates()]
    )
    database_loaded_energies = np.array([atoms.get_potential_energy() for atoms in dataset])
    assert (database_created_energies == database_loaded_energies).all()


def test_forces(database_created: Database, dataset: List[Candidate]) -> None:
    database_created_forces = np.array([atoms.get_forces() for atoms in database_created.get_all_candidates()])
    database_loaded_forces = np.array([atoms.get_forces() for atoms in dataset])
    assert (database_created_forces == database_loaded_forces).all()
