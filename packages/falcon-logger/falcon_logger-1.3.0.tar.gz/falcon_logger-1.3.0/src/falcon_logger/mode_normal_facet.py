import queue
import sys
import threading
import time

from .cfg import cfg
from .mode_base_facet import ModeBaseFacet


# --------------------
## holds functions for mode "normal"
class ModeNormalFacet(ModeBaseFacet):
    # --------------------
    ## constructor
    def __init__(self):
        super().__init__()

        # === runner() related
        ## file pointer to destination file or stdout
        self._fp = None
        ## the bg thread used to run
        self._thread = None
        ## the queue used
        self._queue = None
        ## flag to the thread to end the loop
        self._finished = False

        self._init()

    # --------------------
    ## since it's normal mode, put the logging info on the queue.
    #
    # @param info  the line info
    # @return None
    def log_it(self, info):
        self._queue.put(info)

    # --------------------
    ## initialize the file pointer and start the bg thread
    #
    # @return None
    def _init(self):
        # initialize destination file pointer
        if cfg.path is None:
            self._fp = sys.stdout
        else:
            self._fp = open(cfg.path, 'w', encoding='UTF-8')  # pylint: disable=consider-using-with

        self._init_thread()

    # --------------------
    ## step2 of the terminate sequence.
    # closes the bg thread
    #
    # @return None
    def term_step2(self):
        self._finished = True
        if self._thread is not None and self._thread.is_alive():  # pragma: no cover
            # coverage: always taken in tests
            self._thread.join(5)

    # --------------------
    ## save any entries in the queue to the file
    #
    # @return None
    def save(self):  # pylint: disable=too-many-branches, too-many-statements
        # if stdout or file is none/closed then nothing to do
        if self._fp is None:  # pragma: no cover
            # coverage: can not be replicated
            # probably redundant to finish but do it anyway
            self._finished = True
            return

        sys.stdout.flush()
        count = self._queue.qsize()
        while count > 0:
            # in some closing/race conditions, the file may be closed in the middle of a loop
            # note this can be applied to stdout as well.
            if self._fp.closed:  # pragma: no cover
                break

            try:
                #     0             1      2     3      4       5       6
                # (always_print, verbose, dts, prefix, msgs, user_pfx, color)
                info = self._queue.get_nowait()
                count -= 1
            except queue.Empty:  # pragma: no cover
                # coverage: since count is qsize, this will not normally occur
                # queue is empty, exit the loop
                break

            # not verbose and ok not to print
            if not info[1] and not info[0]:
                continue

            # uncomment to debug
            # print(f'{always_print} {verbose} "{prefix}"  {dts}  "{line}"')

            #    msgs                 prefix
            if info[4][0] is None and info[3] == '.':
                self._handle_dots(info)
                continue

            # at this point, not a dot

            # last call was a dot, so reset and print a newline ready for the new log line
            if cfg.dots != 0:
                cfg.dots = 0
                self._fp.write('\n')
                cfg.restore_config()

            if cfg.start_time == 0.0 and cfg.log_format not in [cfg.log_format_elapsed]:
                cfg.start_time = time.time()
            else:
                # cfg.start_time != 0.0 or cfg.log_format == elapsed
                #          dts
                elapsed = info[2] - cfg.start_time
                # approximately once an hour, restart the time period
                if elapsed >= 3600.0:
                    # display the time at the moment the log line was saved
                    self._handle_full_dts(info[2])

            line1 = self.format.build_line(info)
            full_line = self.format.add_color_user_pfx(info, line1)
            self._fp.write(full_line)
            self._fp.write('\n')

        # flush lines to stdout/file; protect with except in case
        try:
            if not self._fp.closed:
                self._fp.flush()
        except BrokenPipeError:  # pragma: no cover
            # coverage: rare case: if stdout/file is closed this will throw an exception
            pass

    # --------------------
    ## initialize and start the thread
    #
    # @return None
    def _init_thread(self):
        self._queue = queue.Queue()
        self._finished = False

        self._thread = threading.Thread(target=self._runner)
        self._thread.daemon = True
        self._thread.start()

        # wait for thread to start
        time.sleep(0.1)

    # --------------------
    ## the thread runner
    # wakes periodically to check if the queue has max_entries or more in it
    # if so, the lines are written to the file
    # if not, it sleeps
    #
    # @return None
    def _runner(self):
        # wrap with try/except for catching ctrl-c
        # usually fails in sleep() so may not call finally clause
        try:
            count = 0
            while not self._finished:
                # sleep until:
                #  - there are enough entries in the queue
                #  - the max delay is reached
                if self._queue.qsize() < cfg.runner_cfg.max_entries and count < cfg.runner_cfg.max_count:
                    count += 1
                    time.sleep(cfg.runner_cfg.loop_delay)
                    continue

                # write out all the current entries
                count = 0
                self.save()
        finally:
            # save any remaining entries
            self.save()

            # close the file if necessary
            if cfg.path and self._fp is not None:  # pragma: no cover
                # coverage: can't be replicated in UTs
                self._fp.close()
                self._fp = None

    # --------------------
    ## If past max_dots, print a newline. Then print a dot.
    #
    # @param info  logging info (e.g. color)
    # @return none
    def _handle_dots(self, info):
        if cfg.dots == 0:
            # save delay and count
            cfg.save_config()
            # print faster
            cfg.runner_cfg.loop_delay = 0.001
            cfg.runner_cfg.max_entries = 1
            cfg.runner_cfg.max_count = 1

        if cfg.dots >= cfg.max_dots:
            self._fp.write('\n')
            cfg.dots = 0

        line1 = '.'
        full_line = self.format.add_color_user_pfx(info, line1)
        self._fp.write(full_line)
        cfg.dots += 1

    # --------------------
    ## print full DTS stamp
    #
    # @param dts   the dts of the current log line
    # @return None
    def _handle_full_dts(self, dts):
        full_dts = self.format.get_full_dts(dts)
        self._fp.write(full_dts)
        self._fp.write('\n')
