from .format_base_facet import FormatBaseFacet


# --------------------
## functions for format "elapsed"
class FormatPrefixFacet(FormatBaseFacet):
    # --------------------
    ## build a line text based on the given info. Use "prefix" format.
    #
    # @param info   the line info
    # @return the full text of the line
    def build_line(self, info):
        prefix = info[3]
        if prefix is None and info[4] == (None,):
            full_line = self.get_full_dts(info[2])
        elif info[3] == '.' and info[4] == (None,):
            full_line = '.'
        elif prefix is None:
            full_line = ' '.join(map(str, info[4]))
        else:
            line = ' '.join(map(str, info[4]))
            full_line = f'{prefix: <4} {line}'
        return full_line
