import time
from datetime import datetime

from .cfg import cfg


# --------------------
## holds common functions for format facets
class FormatBaseFacet:
    # --------------------
    ## add color and user prefix if any to the given line
    #
    # @param info   the logging info
    # @param line1  the current line text
    # @return the full line text, should be ready to print
    def add_color_user_pfx(self, info, line1):
        # add colors and user prefix if any
        color_pfx, color_sfx = self._get_color(info[6])
        if info[5] is None:
            user_pfx = ''
        else:
            user_pfx = f'{info[5]: <4} '

        full_line = f'{color_pfx}{user_pfx}{line1}{color_sfx}'
        return full_line

    # --------------------
    ## get color code required for the given color.
    # if it is not a recognized color, the value given is used for the code.
    # if the color code is empty, then no color code is returned ('').
    #
    # @param color   the color to use or the color code to use
    # @return the color code prefix, the color code suffix
    def _get_color(self, color):
        clr_sfx = '\033[0m'
        if color == 'green':
            clr_pfx = '\033[92m'
        elif color == 'yellow':
            clr_pfx = '\033[33m'
        elif color == 'red':
            clr_pfx = '\033[31m'
        elif color == 'blue':
            clr_pfx = '\033[1;36m'
        elif color is not None:
            clr_pfx = color
        else:
            clr_pfx = ''
            clr_sfx = ''

        return clr_pfx, clr_sfx

    # --------------------
    ## get the text for a full DTS line.
    #
    # @param dts     the current datetime value
    # @return the dts text
    def get_full_dts(self, dts):
        # restart the timer; user wants the full DTS and elapsed is since that absolute time
        cfg.start_time = dts

        cfg.save_config()
        dts_str = time.strftime("%Y/%m/%d", time.localtime(cfg.start_time))
        t_str = datetime.fromtimestamp(cfg.start_time).strftime('%H:%M:%S.%f')[:12]
        full_dts = f'{"DTS": <4} {dts_str} {t_str}'
        if cfg.log_format == cfg.log_format_elapsed:
            full_dts = f'{"": <9} {full_dts}'
        return full_dts
