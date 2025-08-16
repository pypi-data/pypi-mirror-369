from agox.postprocessors.ABC_postprocess import PostprocessBaseClass


class WrapperPostprocess(PostprocessBaseClass):
    """
    Wraps a candidate object such that all atoms are in the  first unit cell.

    Parameters
    ----------
    None
    """

    name = "WrapperTheRapper"

    def postprocess(self, candidate):
        candidate.wrap()
        return candidate
