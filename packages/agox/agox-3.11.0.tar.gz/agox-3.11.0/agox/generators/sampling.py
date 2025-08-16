from agox.generators.ABC_generator import GeneratorBaseClass


class SamplingGenerator(GeneratorBaseClass):
    """
    Samples without pertubation from a sampler.

    The generator just returns a member of the sampler, which can then be processed by any
    postprocessors, such as relaxation in an updated model.
    """

    name = "SamplingGenerator"

    def __init__(self, replace=True, **kwargs):
        super().__init__(replace=replace, **kwargs)

    def _get_candidates(self, candidate, parents, environment):
        candidates = parents

        if len(candidates) == 0:
            return []

        return candidates

    def get_number_of_parents(self, sampler):
        return len(sampler)
