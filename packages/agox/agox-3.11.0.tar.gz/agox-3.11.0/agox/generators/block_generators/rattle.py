
import numpy as np

from agox.generators.block_generators.ABC_block import BlockGeneratorBaseClass


class RattleBlockGenerator(BlockGeneratorBaseClass):
    name = "RattleBlockGenerator"

    def __init__(
        self, blocks_to_rattle=2, rotation_min=0, rotation_max=15, displacement_min=0, displacement_max=2, **kwargs
    ):
        super().__init__(**kwargs)
        self.blocks_to_rattle = blocks_to_rattle
        self.rotation_min = rotation_min
        self.rotation_max = rotation_max
        self.displacement_min = displacement_min
        self.displacement_max = displacement_max

    def _get_candidates(self, candidate, parents, environment):
        # Block information:
        inter_block_indices = parents[0].meta_information.get("block_indices", None)
        if inter_block_indices is None:
            return []
        N_blocks = len(inter_block_indices)
        block_probs = np.ones(N_blocks) / N_blocks

        # Number of blocks to rattle:
        blocks_to_rattle = self.blocks_to_rattle  # Simple for now.
        atleast_one = False

        for n in range(blocks_to_rattle):
            progress = False
            attempt = 0
            while not progress and attempt <= 1000:
                attempt += 1

                # Pick a block to move:
                block_index = np.random.choice(np.arange(N_blocks), size=1, p=block_probs)[0]
                inter_indices = np.array(inter_block_indices[block_index], dtype=int)
                block = self.extract_block(candidate, inter_indices)

                self.rattle_block(block)  # Now we have a rattled block. In place.

                # CHeck if the block obeys confinement:
                if not self.check_confinement(block.positions).any():
                    continue

                if self.check_distances(candidate, block, inter_indices, present=True):
                    self.block_move(candidate, block, inter_indices)

                    # Renormalize distribution:
                    block_probs[block_index] = 0
                    if np.sum(block_probs) > 0:
                        block_probs /= np.sum(block_probs)

                    atleast_one = True
                    progress = True

        if not atleast_one:
            return []

        blocks_used = parents[0].meta_information.get("blocks_used")
        candidate.add_meta_information("blocks_used", blocks_used)
        candidate.add_meta_information("block_indices", inter_block_indices)

        return [candidate]

    def rattle_block(self, block):
        for a in range(3):
            axis = np.zeros(3)
            axis[a] = 1
            angle = np.random.rand() * (self.rotation_max - self.rotation_min) + self.rotation_min
            sign = np.random.choice([-1, 1], size=1)[0]
            block.rotate(sign * angle, axis, center="COP")

        radius = np.random.rand() * (self.displacement_max - self.displacement_min) + self.displacement_min
        d = self.get_displacement_vector(radius)
        block.positions += d

    def get_number_of_parents(self, sampler):
        return 1
