from datetime import timedelta

from .cfg import cfg
from .format_base_facet import FormatBaseFacet


# --------------------
## functions for format "elapsed"
class FormatElapsedFacet(FormatBaseFacet):
    # --------------------
    ## build a line text based on the given info. Use "elapsed" format.
    #
    # @param info   the line info
    # @return the full text of the line
    def build_line(self, info):
        dts = info[2]
        elapsed = dts - cfg.start_time
        if elapsed >= 3600.0:
            cfg.start_time = dts
            elapsed = 0
        t_str = self._get_elapsed_str(elapsed)

        prefix = info[3]
        if prefix is None and info[4] == (None,):
            full_line = self.get_full_dts(info[2])
        elif info[3] == '.' and info[4] == (None,):
            full_line = '.'
        elif prefix is None:  # raw line
            full_line = ' '.join(map(str, info[4]))
        else:
            line = ' '.join(map(str, info[4]))
            full_line = f'{t_str} {prefix: <4} {line}'
        return full_line

    # --------------------
    ## generate the string of the given elapsed time
    #
    # @param elapsed   the elapsed time to format
    # @return the string ("MM.SS.nnn")
    def _get_elapsed_str(self, elapsed):
        t_str = timedelta(seconds=elapsed)
        # rare case: str(timedelta) makes the ".000000" optional if the number of microseconds is 0
        if t_str.microseconds == 0:  # pragma: no cover
            # bump the number of microseconds by 1 to make sure the full string is formatted
            t_str = timedelta(seconds=elapsed + 0.000001)
        return str(t_str)[2:11]
