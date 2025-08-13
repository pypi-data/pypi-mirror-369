from .mode_base_facet import ModeBaseFacet


# --------------------
## holds functions for mode "null"
class ModeNullFacet(ModeBaseFacet):
    # no save() needed
    # no term_step2() needed

    # --------------------
    ## callback function to log a line in immediate mode
    #
    # @param info   the line info
    # @return None
    def log_it(self, info):  # pylint: disable=unused-argument
        # ignored for null mode
        pass
