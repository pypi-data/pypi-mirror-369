from .cfg import cfg


# --------------------
## holds functions for mode facets
class ModeBaseFacet:
    # --------------------
    ## constructor
    def __init__(self):
        ## holds reference to the format facet
        self.format = None

    # --------------------
    ## save any lines.
    # currently ignored in "null" and "ut/mock" modes
    #
    # @return None
    def save(self):
        pass

    # --------------------
    ## any additional termination steps to do
    #
    # @return None
    def term_step2(self):
        pass

    # --------------------
    ## set the format facet based on the current format selected
    #
    # @return None
    def set_log_it_fn(self):
        if cfg.log_format == cfg.log_format_elapsed:
            from .format_elapsed_facet import FormatElapsedFacet
            self.format = FormatElapsedFacet()
        elif cfg.log_format == cfg.log_format_prefix:
            from .format_prefix_facet import FormatPrefixFacet
            self.format = FormatPrefixFacet()
        elif cfg.log_format == cfg.log_format_none:
            from .format_none_facet import FormatNoneFacet
            self.format = FormatNoneFacet()
        else:  # pragma: no cover
            cfg.abort(f'in ModeFacetUt.set_log_it_fn: unhandled log format {cfg.log_format}')

    # --------------------
    ## prevents lint/IDE warnings; ignored in all modes except UT
    # @return no lines
    @property
    def ut_lines(self):
        return []

    # --------------------
    ## prevents lint/IDE warnings; ignored in all modes except UT
    # @return none
    def ut_clear(self):  # pragma: no cover
        pass
