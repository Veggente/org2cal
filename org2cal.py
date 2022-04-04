#!/usr/bin/env python3
"""Converts LOGBOOK entries in an emacs org file to iCalendar format."""
import datetime
import argparse
import configparser
from os.path import expanduser
import subprocess
import orgparse


class OrgFile:
    """Emacs org file.

    Attributes:
        root: orgparse.node.OrgNode
            The root node in the org tree.
    """

    def __init__(self, filename: str) -> None:
        """Initialization.

        Args:
            filename: Org file name.

        Returns:
            None.
        """
        with open(filename) as f:
            self.root = orgparse.load(f)

    def export_clock(self, dates: list[datetime.date], outfile: str) -> None:
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
PRODID:-//User//EN
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
    def to_ics(event: orgparse.date.OrgDateClock, ancestor_headings: list[str]) -> str:
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
            end,
            ancestor_headings[-1],
            " -> ".join(ancestor_headings),
            start,
        )


def clock_report(
    orgfile: str,
    outfile: str,
    start: datetime.date,
    end: datetime.date,
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


def main(args=None):
    """Main script."""
    parser = get_parser()
    args = parser.parse_args(args)
    config = configparser.ConfigParser()
    rcfile = expanduser("~/.org2calrc")
    config.read(rcfile)
    if args.set_source or args.set_output:
        if args.set_source:
            config["DEFAULT"]["source"] = args.set_source
        if args.set_output:
            config["DEFAULT"]["output"] = args.set_output
        with open(rcfile, "w") as f:
            config.write(f)
        return
    try:
        if args.start:
            to_date = lambda date_str: datetime.date(
                *[int(num) for num in date_str.split("-")]
            )
            start = to_date(args.start)
            end = to_date(args.end)
        elif args.yesterday:
            start = end = datetime.date.today() - datetime.timedelta(1)
        else:
            start = end = datetime.date.today()
        default_conf = config["DEFAULT"]
        clock_report(default_conf["source"], default_conf["output"], start, end)
        subprocess.call(("open", default_conf["output"]))
    except KeyError:
        print("Set the source and output first.")


def get_parser():
    """Creates a new argument parser.

    Adapted from a gist by Steffen Exler at
    https://gist.github.com/linuxluigi/0613c2c699d16cb5e171b063c266c3ad
    """
    parser = argparse.ArgumentParser(
        description="Converts org clock report to iCalendar.  Default is for today."
    )
    parser.add_argument(
        "--start", "-s", type=str, help="Starting date in YYYY-(M)M-(D)D format"
    )
    parser.add_argument(
        "--end", "-e", type=str, help="Ending date in YYYY-(M)M-(D)D format"
    )
    parser.add_argument("--yesterday", "-y", action="store_true", help="Yesterday")
    parser.add_argument("--set-source", type=str, help="Set source org file")
    parser.add_argument("--set-output", type=str, help="Set output ics file")
    return parser


if __name__ == "__main__":
    main()
