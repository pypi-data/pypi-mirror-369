from fuglu.shared import AppenderPlugin, Suspect
from fuglu.scansession import TrackTimings


class TimingAction(AppenderPlugin):
    """
    Plugin appender example which can be the base for performing actions
    based on previous plugin timings
    """
    def __init__(self, config, section=None):
        super().__init__(config)
        self.logger = self._logger()

    def process(self, suspect: Suspect, decision):
        self.logger.debug(f"{suspect.id} In process -> get access to time tracker...")
        tt: TrackTimings = suspect.timetracker
        if tt:
            self.logger.debug(f"{suspect.id} Timetracker extracted -> now extract milter plugin timings")

            mtimings = tt.gettime_dict(mplugins=True)
            self.logger.debug(f"{suspect.id} Extracted {len(mtimings)} milter plugin timings")
            for tag, timing in mtimings.items():
                self.logger.debug(f"{suspect.id} mtiming: {tag} -> {timing}s")

            ptimings = tt.gettime_dict(plugins=True)
            self.logger.debug(f"{suspect.id} Extracted {len(mtimings)} plugin timings")
            for tag, timing in ptimings.items():
                self.logger.debug(f"{suspect.id} ptiming: {tag} -> {timing}s")

        else:
            self.logger.error(f"{suspect.id} Could not extract timetracker!")
