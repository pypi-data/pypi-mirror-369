from .cfg import cfg
from .mode_base_facet import ModeBaseFacet


# --------------------
## holds functions for mode "ut" or "mock"
class ModeUtFacet(ModeBaseFacet):
    # --------------------
    ## constructor
    def __init__(self):
        super().__init__()

        ## holds lines during UTs; must be a public attribute
        self._ut_lines = []
        ## holds the current dots in the line
        self._dot_line = ''

    # no save() needed
    # no term_step2() needed

    # --------------------
    ## return current set of UT lines
    # @return current set of UT lines
    @property
    def ut_lines(self):
        return self._ut_lines

    # --------------------
    ## clear out current UT lines
    # @return none
    def ut_clear(self):
        self._ut_lines = []

    # --------------------
    ## callback function to log a line in immediate mode
    #
    # @param info   the line info
    # @return None
    def log_it(self, info):
        if not info[0] and not info[1]:  # !always_print and !verbose
            return

        line1 = self.format.build_line(info)
        full_line = self.format.add_color_user_pfx(info, line1)
        self._print_line(info, full_line)

    # --------------------
    ## print a line in immediate mode with the given colors and user_prefixes.
    # it is printed to stdout, which is then flushed
    #
    # @param info        the line info
    # @param full_line   the text of the line
    # @return None
    def _print_line(self, info, full_line):
        if info[3] == '.' and info[4] == (None,):
            self._handle_dots(full_line)
        else:
            # last call was a dot, so reset and print a newline ready for the new log line
            self._reset_dots()
            self._ut_lines.append(full_line)

    # --------------------
    ## If past max_dots, print a newline. Then print a dot (may have color codes).
    #
    # @param line   dot with or without color codes
    # @return none
    def _handle_dots(self, line):
        if cfg.dots >= cfg.max_dots:
            self._ut_lines.append(self._dot_line)
            self._dot_line = ''
            cfg.dots = 0

        self._dot_line += line
        cfg.dots += 1

    # --------------------
    ## reset the dots count and print a newline as needed
    #
    # @return None
    def _reset_dots(self):
        if cfg.dots != 0:
            self._ut_lines.append(self._dot_line)
            self._dot_line = ''
            cfg.dots = 0
