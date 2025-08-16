from typing import List, Optional

import numpy as np
import torch
from ase import Atoms
from ase.calculators.calculator import Calculator
from ase.calculators.mixing import SumCalculator as SumCalculatorASE

from agox import Module


class BlockCalculator(Calculator):
    implemented_properties = ["energy", "forces"]

    def __init__(self, blocks: List[Atoms], power: float = 4.0, factor: float = 1.0) -> None:
        super().__init__()
        self.blocks = blocks
        self.process_blocks(blocks)

        self.power = power
        self.factor = factor

    def calculate(self, atoms: Atoms, properties: Optional[List] = None, system_changes: Optional[List] = None) -> None:
        super().calculate(atoms, properties, system_changes)

        # Extract information about the blocks
        blocks_used = atoms.meta_information["blocks_used"]
        block_indices = atoms.meta_information["block_indices"]

        # Get the block indices
        edge_index = torch.tensor(self.get_edge_indices(block_indices, blocks_used), dtype=torch.long)
        positions = torch.tensor(atoms.get_positions(), requires_grad=True)

        # Calculate the distances
        r = positions[edge_index[:, 0]] - positions[edge_index[:, 1]]
        r_norm = torch.norm(r, dim=1)
        r_blocks = self.get_block_distances(blocks_used)

        # Calculate the energy
        r_diff = r_norm - r_blocks
        block_bond_energy = (self.factor * r_diff) ** self.power 
        energy = torch.sum(block_bond_energy)

        # Calculate the forces
        forces = -torch.autograd.grad(energy, positions)[0]

        self.results["energy"] = energy.detach().numpy().item()
        self.results["forces"] = forces.detach().numpy()

    def get_edge_indices(self, block_indices: np.ndarray, blocks_used: np.ndarray) -> np.ndarray:
        stacked_block_indices = []

        for atoms_idx, block_idx in zip(block_indices, blocks_used):
            stacked_block_indices.append(self.edge_indices[block_idx] + min(atoms_idx))

        z = np.concatenate(stacked_block_indices, axis=0).astype(np.int32)
        return z

    def get_initial_index_array(self, block_indices: np.ndarray) -> np.ndarray:
        stacked_block_indices = []

        for block_index in block_indices:
            i, j = np.meshgrid(block_index, block_index)
            tri_index = np.triu_indices(len(block_index), k=1)
            ij = np.stack([i[tri_index].flatten(), j[tri_index].flatten()], axis=1)
            stacked_block_indices.append(ij)

        z = np.concatenate(stacked_block_indices, axis=0).astype(np.int32)
        return z

    def process_blocks(self, blocks: List[Atoms]) -> None:
        """
        Could add a cutoff in this function so that not all inter-block distances are 
        calculated. This could allow blocks to flex. 
        """
        block_distances = []
        edge_indices = []

        for block in blocks:
            edge_index = self.get_initial_index_array([np.arange(len(block))])
            positions = torch.tensor(block.get_positions())
            r = positions[edge_index[:, 0]] - positions[edge_index[:, 1]]
            r_norm = torch.norm(r, dim=1)
            block_distances.append(r_norm)
            edge_indices.append(edge_index)

        self.block_distances = block_distances
        self.edge_indices = edge_indices

    def get_block_distances(self, blocks_used: np.ndarray) -> torch.Tensor:
        block_distances = torch.concatenate([self.block_distances[i] for i in blocks_used])
        return block_distances


class SumCalculator(SumCalculatorASE, Module):

    def __init__(self, calc1: Calculator, calc2: Calculator) -> None:
        SumCalculatorASE.__init__(self, calcs=[calc1, calc2])
        Module.__init__(self)
        self.calc1 = calc1
        self.calc2 = calc2
        self.ready_state = True







