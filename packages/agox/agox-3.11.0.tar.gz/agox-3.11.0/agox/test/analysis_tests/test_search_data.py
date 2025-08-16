import numpy as np
import pytest

from agox.analysis.search_data import SearchData


def test_search_id(search_data: SearchData) -> None:
    identifiers = search_data.get_all_identifiers()
    assert isinstance(identifiers, list)
    assert isinstance(identifiers[0], str)


def test_search_files(search_data: SearchData) -> None:
    files = search_data.get_files()
    assert isinstance(files, list)


def test_search_num_restarts(search_data: SearchData) -> None:
    n_restarts = search_data.get_number_of_restarts()
    assert n_restarts == 5


def test_search_get_energies_shape(search_data: SearchData) -> None:
    energies = search_data.get_all_energies(fill=np.nan)
    assert energies.shape[0] == search_data.get_number_of_restarts()


def test_search_get_energies_fill(search_data: SearchData) -> None:
    energies = search_data.get_all_energies(fill=np.nan)
    energies_inf = search_data.get_all_energies(fill=np.inf)
    np.testing.assert_allclose(np.nanmin(energies), np.min(energies_inf))


def test_search_get_candidate_has_energy(search_data: SearchData) -> None:
    candidate = search_data.get_candidate(0, 0)
    assert isinstance(candidate.get_potential_energy(), float)


def test_search_get_candidate_restart_index(search_data: SearchData) -> None:
    with pytest.raises(IndexError):
        search_data.get_candidate(6, 0)


def test_search_get_candidate_iteration_index(search_data: SearchData) -> None:
    with pytest.raises(IndexError):
        search_data.get_candidate(0, 1001)


def test_search_get_best_candidates_shape(search_data: SearchData) -> None:
    candidates = search_data.get_best_candidates()
    assert len(candidates) == search_data.get_number_of_restarts()


def test_search_get_best_candidates_energy(search_data: SearchData) -> None:
    candidates = search_data.get_best_candidates()
    energies = [c.get_potential_energy() for c in candidates]


def test_search_print(search_data: SearchData) -> None:
    print(search_data)


def test_search_save_load(search_data: SearchData) -> None:
    energies_b = search_data.get_all_energies()
    search_data.save()
    search_data.load()
    energies_a = search_data.get_all_energies()

    np.testing.assert_allclose(energies_b, energies_a)
