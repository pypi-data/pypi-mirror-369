from typing import List

import numpy as np

from agox.candidates import Candidate
from agox.environments import Environment
from agox.generators.block_generators.ABC_block import BlockGeneratorBaseClass


class RandomBlockGenerator(BlockGeneratorBaseClass):
    name = "RandomBlockGenerator"

    def _get_candidates(
        self, candidate: Candidate, parents: List[Candidate], environment: Environment
    ) -> List[Candidate]:
        blocks_placed = np.zeros(len(self.building_blocks))
        block_indices = []
        blocks_used = []

        n_atoms_template = len(candidate)
        conf_template_indices = np.argwhere(self.check_confinement(candidate.positions)).flatten()

        while np.sum(blocks_placed) < np.sum(self.N_blocks):
            block, block_index = self.get_building_block(blocks_placed, random_rotation=True)

            if (blocks_placed == 0).all():
                suggested_position = self.get_box_vector()
            else:
                r_min = 1
                r_max = 3.5
                radius = np.random.rand() * (r_max - r_min) + r_min
                displacement = self.get_displacement_vector(radius)

                valid_indices = np.concatenate([conf_template_indices, 
                                                np.arange(n_atoms_template, len(candidate))])

                xyz0 = candidate.positions[np.random.choice(valid_indices)].reshape(3)
                suggested_position = xyz0 + displacement

                if not self.check_confinement(suggested_position):
                    continue

            block.positions += suggested_position

            # Checks confinement for all atoms in the building block at once.
            if not self.check_confinement(block.positions).any():
                continue

            # Checks that distances are not too bad.
            # This implementation does NOT care about PBCs.
            if not self.check_distances(candidate, block, present=False):
                continue

            block_indices += [(np.arange(len(candidate), len(candidate) + len(block)))]
            candidate += block
            blocks_placed[block_index] += 1
            blocks_used.append(block_index)

        candidate.add_meta_information("blocks_used", np.array(blocks_used))
        candidate.add_meta_information("block_indices", np.array(block_indices, dtype=object))

        if self.apply_constraint:
            constraint = self.get_fix_internal_constraint(blocks_used)
            candidate.set_constraint(constraint)

        return [candidate]

    def get_number_of_parents(self, sampler):
        return 0
