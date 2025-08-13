import atexit
import json
import time
import traceback

from .cfg import cfg
from .constants_version import ConstantsVersion


# --------------------
## holds logging functions that replace common python logger functions
class FalconLogger:  # pylint: disable=too-many-public-methods
    # --------------------
    ## constructor
    #
    # @param path         None for stdout, or full path to the logger file
    # @param max_entries  (optional) maximum number of entries before a flush is done; default 10
    # @param loop_delay   (optional) time between checking queue; default 0.250 seconds
    # @param mode         (optional) logging mode: default is None
    #                      None or "normal": log all lines as set by configuration, format, etc.
    #                      "immediate": same as normal, but print directly to stdout, no bg thread.
    #                      "ut" or "mock": for UT purposes, saves lines in ut_lines array
    #                      "null": do no logging; see verbosity for an alternative
    def __init__(self, path=None, max_entries=10, loop_delay=0.250, mode=None):
        ## holds reference to the current mode
        self._mode_facet = None

        # initialize cfg from CLI
        cfg.mode = mode
        cfg.path = path
        cfg.max_entries = max_entries
        cfg.loop_delay = loop_delay

        # other cfg
        cfg.verbose = True
        cfg.log_format = cfg.log_format_elapsed
        cfg.start_time = 0.0
        cfg.dots = 0
        cfg.max_dots = 25
        self._cfg_init(max_entries, loop_delay)
        # set log mode; done once, cannot be changed
        if cfg.mode is None or cfg.mode == 'normal':
            from .mode_normal_facet import ModeNormalFacet
            self._mode_facet = ModeNormalFacet()
        elif cfg.mode == 'immediate':
            from .mode_immediate_facet import ModeImmediateFacet
            self._mode_facet = ModeImmediateFacet()
        elif cfg.mode in ['ut', 'mock']:
            cfg.mode = 'ut'  # reset mock; there may be differences in the future
            from .mode_ut_facet import ModeUtFacet
            self._mode_facet = ModeUtFacet()
        elif cfg.mode == 'null':
            from .mode_null_facet import ModeNullFacet
            self._mode_facet = ModeNullFacet()
        else:
            cfg.abort(f'Unknown mode: "{cfg.mode}", '
                      'choose "normal", "immediate", "ut", "mock" or "null"')

        self._mode_facet.set_log_it_fn()
        ## holds the function to call to log the given content
        self._log_it = self._mode_facet.log_it

        # try ensure at least one save() and thread cleanup is done
        ## term(), see below
        atexit.register(self.term)

    # --------------------
    ## initialize the configuration variables for the loop in elapsed mode
    #
    # @param max_entries   the max number of entries in the queue
    # @param loop_delay    how long to wait between checks of the queue
    # @return None
    def _cfg_init(self, max_entries, loop_delay):
        cfg.init_config()
        self.set_max_entries(max_entries)
        self.set_loop_delay(loop_delay)
        cfg.save_config()

    # --------------------
    ## return the current version
    # @return the current version
    @property
    def version(self):
        return ConstantsVersion.version

    # --------------------
    ## set verbosity
    #
    # @param value  (bool) verbosity level
    # @return None
    def set_verbose(self, value):
        cfg.verbose = value

    # --------------------
    ## set log line format.
    #
    # @param form  (str) either "elapsed" or "prefix" or throws excp
    # @return None
    def set_format(self, form):
        # flush all queue entries with the current format
        self.save()

        # set the new format for future lines
        if form == 'elapsed':
            cfg.log_format = cfg.log_format_elapsed
        elif form == 'prefix':
            cfg.log_format = cfg.log_format_prefix
        elif form == 'none':
            cfg.log_format = cfg.log_format_none
        else:
            cfg.abort(f'Unknown format: "{form}", choose "elapsed", "prefix" or "none"')

        self._mode_facet.set_log_it_fn()

    # --------------------
    ## set max entries to allow in the queue before printing them
    #
    # @param value  (int) number of entries; default: 10
    # @return None
    def set_max_entries(self, value):
        cfg.runner_cfg.max_entries = value
        if cfg.runner_cfg.max_entries <= 0:
            cfg.abort('max_entries must be greater than 0')

    # --------------------
    ## set loop delay to check the queue
    #
    # @param loop_delay (float) number of seconds; default: 0.250
    # @return None
    def set_loop_delay(self, loop_delay):
        cfg.runner_cfg.loop_delay = loop_delay
        if cfg.runner_cfg.loop_delay < 0.001:
            cfg.abort('loop_delay must be >= 0.001 seconds')

        # print every loop_delay seconds even if less than max_entries are in the queue
        cfg.runner_cfg.max_count = int(round(1 / cfg.runner_cfg.loop_delay, 1))

    # --------------------
    ## set how many dots to print on one line before printing a newline
    #
    # @param value  (int) number of dots
    # @return None
    def set_max_dots(self, value):
        cfg.max_dots = value
        if cfg.max_dots <= 0:
            cfg.abort('max_dots must be greater than 0')

    # === cleanup functions

    # --------------------
    ## terminate
    # stop the thread, save any remaining line in the internal queue
    #
    # @return None
    def term(self):
        try:
            # since this will be called during atexit() handling,
            # stdout and/or file can be closed. Protect against this case.
            self._mode_facet.save()
        except Exception:  # pylint: disable=broad-exception-caught # pragma: no cover
            pass
        self._mode_facet.term_step2()

    # --------------------
    ## do a save at this point
    #
    # @return None
    def save(self):
        self._mode_facet.save()

    # === log functions

    # --------------------
    ## add an item to write the full date-time-stamp to the log
    #
    # @param pfx     the user-requested prefix
    # @param color   the color to use
    # @return None
    def full_dts(self, pfx=None, color=None):
        # the None msgs/line causes the full dts to display
        self._log_it((False, cfg.verbose, time.time(), None, (None,), pfx, color))

    # --------------------
    ## indicate some activity is starting
    #
    # @param msgs    the message to log
    # @param pfx     the user-requested prefix
    # @param color   the color to use
    # @return None
    def start(self, /, *msgs, pfx=None, color=None):
        self._log_it((False, cfg.verbose, time.time(), '====', msgs, pfx, color))

    # --------------------
    ## write line with no prefix
    #
    # @param msgs    the message to log
    # @param pfx     the user-requested prefix
    # @param color   the color to use
    # @return None
    def line(self, /, *msgs, pfx=None, color=None):
        self._log_it((False, cfg.verbose, time.time(), '', msgs, pfx, color))

    # --------------------
    ## write a highlight line
    #
    # @param msgs    the message to log
    # @param pfx     the user-requested prefix
    # @param color   the color to use
    # @return None
    def highlight(self, /, *msgs, pfx=None, color=None):
        self._log_it((False, cfg.verbose, time.time(), '--->', msgs, pfx, color))

    # --------------------
    ## write an ok line
    #
    # @param msgs    the message to log
    # @param pfx     the user-requested prefix
    # @param color   the color to use
    # @return None
    def ok(self, /, *msgs, pfx=None, color=None):
        self._log_it((False, cfg.verbose, time.time(), 'OK', msgs, pfx, color))

    # --------------------
    ## write an error line
    #
    # @param msgs    the message to log
    # @param pfx     the user-requested prefix
    # @param color   the color to use
    # @return None
    def err(self, /, *msgs, pfx=None, color=None):
        self._log_it((True, cfg.verbose, time.time(), 'ERR', msgs, pfx, color))

    # --------------------
    ## write an warn line
    #
    # @param msgs    the message to log
    # @param pfx     the user-requested prefix
    # @param color   the color to use
    # @return None
    def warn(self, /, *msgs, pfx=None, color=None):
        self._log_it((False, cfg.verbose, time.time(), 'WARN', msgs, pfx, color))

    # --------------------
    ## write a debug line
    #
    # @param msgs    the message to log
    # @param pfx     the user-requested prefix
    # @param color   the color to use
    # @return None
    def bug(self, /, *msgs, pfx=None, color=None):
        self._log_it((True, cfg.verbose, time.time(), 'BUG', msgs, pfx, color))

    # --------------------
    ## write a debug line
    #
    # @param msgs    the message to log
    # @param pfx     the user-requested prefix
    # @param color   the color to use
    # @return None
    def dbg(self, /, *msgs, pfx=None, color=None):
        self._log_it((False, cfg.verbose, time.time(), 'DBG', msgs, pfx, color))

    # --------------------
    ## write a raw line (no prefix)
    #
    # @param msgs    the message to log
    # @param pfx     the user-requested prefix
    # @param color   the color to use
    # @return None
    def raw(self, /, *msgs, pfx=None, color=None):
        self._log_it((False, cfg.verbose, time.time(), None, msgs, pfx, color))

    # -------------------
    ## write an output line with the given message
    #
    # @param lineno  (optional) the current line number for each line printed
    # @param msgs    the message to write
    # @param pfx     the user-requested prefix
    # @param color   the color to use
    # @return None
    def output(self, /, lineno, *msgs, pfx=None, color=None):
        if lineno is None:
            new_args = ('    ',) + msgs
        else:
            new_args = (f'{lineno: >3}]',) + msgs
        self._log_it((False, cfg.verbose, time.time(), ' --', new_args, pfx, color))

    # -------------------
    ## write a list of lines using output()
    #
    # @param lines   the lines to write
    # @param pfx     the user-requested prefix
    # @param color   the color to use
    # @return None
    def num_output(self, lines, pfx=None, color=None):
        lineno = 0
        for line in lines:
            lineno += 1
            self.output(lineno, line, pfx=pfx, color=color)

    # --------------------
    ## if ok is True, write an OK line, otherwise an ERR line.
    #
    # @param ok      condition indicating ok or err
    # @param msgs    the message to log
    # @param pfx     the user-requested prefix
    # @param color   the color to use
    # @return None
    def check(self, ok, /, *msgs, pfx=None, color=None):
        if ok:
            self.ok(*msgs, pfx=pfx, color=color)
        else:
            self.err(*msgs, pfx=pfx, color=color)

    # --------------------
    ## log a series of messages. Use ok() or err() as appropriate.
    #
    # @param ok      the check state
    # @param title   the line indicating what the check is about
    # @param lines   individual list of lines to print
    # @param pfx     the user-requested prefix
    # @param color   the color to use
    # @return None
    def check_all(self, ok, title, lines, pfx=None, color=None):
        self.check(ok, f'{title}: {ok}', pfx=pfx, color=color)
        for line in lines:
            self.check(ok, f'   - {line}', pfx=pfx, color=color)

    # -------------------
    ## add an item to write a 'line' message and a json object to the log
    #
    # @param j       the json object to write
    # @param msgs    the message to write
    # @param pfx     the user-requested prefix
    # @param color   the color to use
    # @return None
    def json(self, j, /, *msgs, pfx=None, color=None):
        now = time.time()
        self._log_it((False, cfg.verbose, now, ' ', msgs, pfx, color))

        if isinstance(j, str):
            j = json.loads(j)

        for line in json.dumps(j, indent=2).splitlines():
            self._log_it((False, cfg.verbose, now, ' >', (line,), pfx, color))

    # -------------------
    ## add an item to write a 'line' message and a data buffer to the log in hex
    #
    # @param data    the data buffer to write; can be a string or a bytes array
    # @param msgs    the messages to write
    # @param pfx     the user-requested prefix
    # @param color   the color to use
    # @return None
    def hex(self, data, *msgs, pfx=None, color=None):
        now = time.time()
        self._log_it((False, cfg.verbose, now, ' ', msgs, pfx, color))
        i = 0
        line = f'{i:>3} 0x{i:02X}:'
        if isinstance(data, str):
            data = bytes(data, 'utf-8')

        col = 0
        for i, ch in enumerate(data):
            if col >= 16:
                self._log_it((False, cfg.verbose, now, '', (' ', line), pfx, color))
                col = 0
                line = f'{i:>3} 0x{i:02X}:'

            line += f' {ch:02X}'
            col += 1
            if col == 8:
                line += '  '

        # print if there's something left over
        self._log_it((False, cfg.verbose, now, ' ', (' ', line), pfx, color))

    # --------------------
    ## write a dot to stdout
    #
    # @param color   the color to use
    # @return None
    def dot(self, /, color=None):
        self._log_it((False, cfg.verbose, time.time(), '.', (None,), None, color))

    # === (some) compatibility with python logger

    # --------------------
    ## log a debug line
    #
    # @param msgs    the line to print
    # @param pfx     the user-requested prefix
    # @param color   the color to use
    # @return None
    def debug(self, /, *msgs, pfx=None, color=None):
        self._log_it((False, cfg.verbose, time.time(), 'DBG', msgs, pfx, color))

    # --------------------
    ## log an info line
    #
    # @param msgs    the line to print
    # @param pfx     the user-requested prefix
    # @param color   the color to use
    # @return None
    def info(self, *msgs, pfx=None, color=None):
        self._log_it((False, cfg.verbose, time.time(), '', msgs, pfx, color))

    # --------------------
    ## log a warning line
    #
    # @param msgs    the line to print
    # @param pfx     the user-requested prefix
    # @param color   the color to use
    # @return None
    def warning(self, /, *msgs, pfx=None, color=None):
        self._log_it((False, cfg.verbose, time.time(), 'WARN', msgs, pfx, color))

    # --------------------
    ## log an error line
    #
    # @param msgs    the line to print
    # @param pfx     the user-requested prefix
    # @param color   the color to use
    # @return None
    def error(self, /, *msgs, pfx=None, color=None):
        self._log_it((True, cfg.verbose, time.time(), 'ERR', msgs, pfx, color))

    # --------------------
    ## log a critical line
    #
    # @param msgs    the line to print
    # @param pfx     the user-requested prefix
    # @param color   the color to use
    # @return None
    def critical(self, /, *msgs, pfx=None, color=None):
        self._log_it((True, cfg.verbose, time.time(), 'CRIT', msgs, pfx, color))

    # --------------------
    ## log an exception
    #
    # @param excp       the exception to print
    # @param max_lines  (optional) max lines of the excp to print
    # @param pfx        the user-requested prefix
    # @param color      the color to use
    # @return None
    def exception(self, excp, /, max_lines=None, pfx=None, color=None):
        now = time.time()
        self._log_it((True, cfg.verbose, now, 'EXCP', (str(excp),), pfx, color))
        lineno = 1
        done = False
        for line in traceback.format_exception(excp):
            for line2 in line.splitlines():
                if max_lines is not None and lineno >= max_lines:
                    done = True
                    break

                self._log_it((True, cfg.verbose, now, 'EXCP', (line2,), pfx, color))
                lineno += 1
            if done:
                break

    # === ut related

    # --------------------
    ## get access to ut_lines
    @property
    def ut_lines(self):
        return self._mode_facet.ut_lines

    # --------------------
    ## backwards compatibility; clears ut_lines
    #
    # @return None
    def ut_clear(self):
        self._mode_facet.ut_clear()

    # --------------------
    ## for UT only; move the start_time by the given delta
    #
    # @param delta  the time to adjust the start_time to
    # @return None
    def ut_adjust_time(self, delta):
        cfg.start_time += delta
