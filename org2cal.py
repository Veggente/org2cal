"""Converts LOGBOOK entries in an emacs org file to iCalendar format."""
from typing import List
import datetime
import orgparse


class OrgFile:
    """Emacs org file."""

    def __init__(self, filename: str) -> None:
        """Initialization.

        Args:
            filename: Org file name.

        Returns:
            None.
        """
        with open(filename) as f:
            self.root = orgparse.load(f)

    def export_clock(self, dates: List[datetime.date], outfile: str) -> None:
        """Exports clock report to ICS format.

        Args:
            dates: Dates to export.
            outfile: Output file.

        Returns:
            Writes file.
        """
        with open(outfile, "w") as f:
            f.write(
                """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Veggente//EN
CALSCALE:GREGORIAN\n"""
            )
            for node in self.root[1:]:
                ancestor_headings = [
                    node.get_parent(n).heading for n in range(1, node.level)
                ] + [node.heading]
                for event in node.clock:
                    if event.start.date() in dates:
                        f.write(self.to_ics(event, ancestor_headings))
            f.write("""END:VCALENDAR\n""")

    @staticmethod
    def to_ics(event: orgparse.date.OrgDateClock, ancestor_headings: List[str]) -> str:
        """Converts an event to ICS format.

        Args:
            event: Single event.
            ancestor_headings: Ancestor headings.

        Returns:
            String in iCalendar format.
        """
        to_str = lambda date: date.isoformat().replace("-", "").replace(":", "")
        start = to_str(event.start)
        end = to_str(event.end)
        return """BEGIN:VEVENT
DTEND;TZID=US-Eastern:{}
SUMMARY:{}
DESCRIPTION:{}
DTSTART;TZID=US-Eastern:{}
END:VEVENT\n""".format(
            end,  # pylint: disable=bad-continuation
            ancestor_headings[-1],  # pylint: disable=bad-continuation
            " -> ".join(ancestor_headings),  # pylint: disable=bad-continuation
            start,  # pylint: disable=bad-continuation
        )


def clock_report(
    orgfile: str, outfile: str, start: datetime.date, end: datetime.date  # pylint: disable=bad-continuation
) -> None:
    """Gets clock report in iCalendar format.

    Args:
        orgfile: Org input file.
        outfile: Output file.
        start: Starting date.
        end: Ending date.

    Returns:
        Writes iCalendar output file.
    """
    log_file = OrgFile(orgfile)
    num_days = (end - start).days + 1
    dates = [start + datetime.timedelta(n) for n in range(num_days)]
    log_file.export_clock(dates, outfile)
