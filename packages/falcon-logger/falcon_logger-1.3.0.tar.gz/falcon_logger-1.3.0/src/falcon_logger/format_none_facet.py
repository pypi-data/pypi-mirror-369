from .format_base_facet import FormatBaseFacet


# --------------------
## functions for format "elapsed"
class FormatNoneFacet(FormatBaseFacet):
    # --------------------
    ## build a line text based on the given info. Use "none" format.
    #
    # @param info   the line info
    # @return the full text of the line
    def build_line(self, info):
        prefix = info[3]
        if prefix is None and info[4] == (None,):
            full_line = self.get_full_dts(info[2])
        elif prefix == '.' and info[4] == (None,):
            full_line = '.'
        else:
            full_line = ' '.join(map(str, info[4]))
        return full_line
