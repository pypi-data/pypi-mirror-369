import copy
from dataclasses import dataclass


# --------------------
## configuration values from CLI, and others needed
class Cfg:
    ## logging format with elapsed time and prefixes
    log_format_elapsed = 1
    ## logging format with prefixes only
    log_format_prefix = 2
    ## logging format with no prefixes or elapsed time
    log_format_none = 3

    ## the full path to the log file (if any)
    path = None
    ## holds the logging mode (None, normal, ut, etc.
    mode = None
    ## verbosity; if True print all lines, if not print only errors, excp ad bug lines
    verbose = True
    ## holds the last time a full DTS was written to the log; printed at the beginning and once per hour
    start_time = 0.0
    ## current number of dots printed
    dots = 0
    ## max number of dots to display
    max_dots = 25

    ## the log display format to use; default: elapsed time + prefixes
    log_format = None

    ## used in normal mode only to save/restore some values in cfg
    runner_cfg = None
    ## backup for runner_cfg
    backup_cfg = None

    # --------------------
    ## initialize config dataclass used for writing dots in normal mode
    #
    # @return None
    def init_config(self):
        ## used in normal mode only to save/restore some values in cfg
        @dataclass
        class RunnerCfg:
            ## the maximum entries to hold in the queue before saving to the file
            max_entries: int
            ## the maximum number of loops before the queue is emptied
            max_count: int
            ## the delay between checking the queue for entries to save
            loop_delay: float

        self.runner_cfg = RunnerCfg(0, 0, 0.0)

    # --------------------
    ## save a copy of the current runner cfg to a backup
    #
    # @return None
    def save_config(self):
        self.backup_cfg = copy.deepcopy(self.runner_cfg)

    # --------------------
    ## restore current runner cfg from backup
    #
    # @return None
    def restore_config(self):
        self.runner_cfg = copy.deepcopy(self.backup_cfg)

    # --------------------
    ## abort the session with a non-zero rc (1)
    #
    # @param msg   the message to print to stdout
    # @return does not return, exits the script
    def abort(self, msg):
        print(f'BUG abort {msg}')
        import sys
        sys.stdout.flush()
        sys.exit(1)


cfg = Cfg()
