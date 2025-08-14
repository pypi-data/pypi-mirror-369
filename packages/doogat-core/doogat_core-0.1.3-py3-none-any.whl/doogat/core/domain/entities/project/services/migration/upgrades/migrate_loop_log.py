"""
This module provides functionality to migrate log entries from zettel metadata and sections into a structured log format.

It includes functions to parse log entries from text content and metadata and update the zettel data structure accordingly.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from doogat.core.domain.value_objects.zettel_data import ZettelData


@dataclass
class NextAction:
    """Properties of next action extracted from zettel data.

    :param gtd_list: List according ti GTD method
    :param priority: Priority = icon (emoji) recognized by Obsidian Tasks plugin: ⏬ 🔽 🔼 ⏫
    :param dates: Action milestones
    """

    gtd_list: str
    priority: str
    dates: str


def migrate_loop_log(zettel_data: ZettelData) -> None:
    """
    Migrate log entries from the first section of the zettel data to a new log section.

    :param zettel_data: The zettel data to be processed.
    :type zettel_data: :class:`ZettelData`
    :return: None. The function modifies the `zettel_data` in place.
    """
    header, content = zettel_data.sections[0]
    log_entries, remaining_content = extract_log_entries(content)
    next_action = get_next_action_properties(zettel_data)
    formatted_log = format_log_entries(
        log_entries,
        next_action=next_action,
    )

    zettel_data.sections[0] = (header, "\n".join(remaining_content))
    if formatted_log:
        zettel_data.sections.append(("## Log", formatted_log))


def extract_log_entries(
    content: str,
) -> tuple[list[tuple[datetime, str, str]], list[str]]:
    """
    Extract log entries from the provided content string.

    :param content: The content from which to extract log entries.
    :type content: str
    :return: A tuple containing a list of log entries and a list of unmatched lines.
    :rtype: tuple[list[tuple[datetime, str, str]], list[str]]
    """
    log_pattern = r"(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}) - (.*?)(?: => (.*))?$"
    matches = []
    unmatched_lines = []

    for line in content.split("\n"):
        match = re.match(log_pattern, line.strip())
        if match:
            date_str, before, after = match.groups()
            date_obj = datetime.strptime(date_str, "%d.%m.%Y %H:%M").astimezone()
            matches.append((date_obj, before.strip(), after.strip() if after else ""))
        else:
            if line.strip():
                unmatched_lines.append(line.strip())

    return matches, unmatched_lines


def get_next_action_properties(zettel_data: ZettelData) -> NextAction:
    """
    Determine next action properties from project metadata.

    :param zettel_data: The zettel data to be processed
    :type zettel_data: ZettelData
    :return: NextAction instance containing GTD list, priority, and dates
    :rtype: NextAction
    """
    PRIORITY_MAP = {"could": "⏬", "would": "🔽", "should": "🔼", "must": "⏫"}

    BEFORE_MAP = {"start": "start", "end": "before", "complete": "before"}

    def process_metadata_key(key: str, target_date: str) -> tuple[str, str, str]:
        importance, action = key.split("-")

        if PRIORITY_MAP.get(importance):
            priority = PRIORITY_MAP[importance]
        else:
            return "", "", ""

        if action == "wait":
            gtd_list = "#gtd/wait"
        else:
            gtd_list = f"#gtd/act/{determine_gtd_list_from_target_date(target_date)}"

        milestone = parse_date_string(target_date)
        if action in BEFORE_MAP:
            milestone.before = BEFORE_MAP[action]

        dates = create_dates_section(milestone)
        del zettel_data.metadata[key]

        return gtd_list, priority, dates

    # Find the first matching metadata key
    for key, target_date in zettel_data.metadata.items():
        if "-" in key:
            next_action = NextAction(*process_metadata_key(key, target_date))
            return next_action

    # Default values if no matching metadata found
    return NextAction("#gtd/inbox", "🔼", "")


def create_dates_section(milestone: DateParseResult) -> str:
    """
    Determine dates section for a next action from a milestone.

    :param milestone: DateParseResult instance representing a point in time.
    :type milestone: :class:DateParseResult
    :return: Dates section understood by Obsidian Tasks plugin.
    :rtype: str
    """
    if not milestone.date:
        return ""

    if milestone.before == "" or milestone.before == "before":
        return f"📅 {milestone.date.strftime('%Y-%m-%d')}"

    if milestone.before == "start" or milestone.before == "after":
        return f"🛫 {milestone.date.strftime('%Y-%m-%d')}"

    if milestone.before == "on":
        return f"⏳ {milestone.date.strftime('%Y-%m-%d')}"

    return ""


def determine_gtd_list_from_target_date(target_date: str) -> str:
    """
    Determine GTD list from target date.

    :param target_date: Date or word describing point in time.
    :type target_date: str
    :return: Name of corresponding GTD list.
    :rtype: str
    """
    next_action = parse_date_string(target_date)

    if (
        next_action.before == "now"
        or next_action.before == "next"
        or next_action.before == "someday"
        or next_action.before == "later"
    ):
        return next_action.before
    return "now"


@dataclass
class DateParseResult:
    """Result of parsing a string containing a date.

    :param date: Parsed datetime object or None if no date found
    :param before: Text before the date (or entire text if no date)
    :param after: Text after the date (empty if no date)
    """

    date: Optional[datetime]
    before: str
    after: str


def parse_date_string(input_string: str) -> DateParseResult:
    """Parse a string to extract a date in yyyy-mm-dd format and surrounding text.

    This function searches for a date pattern in the input string and splits the
    string into three parts: the date (as datetime object) and the text before
    and after the date.

    :param input_string: String that may contain a date in yyyy-mm-dd format
    :type input_string: str
    :returns: DateParseResult object with date, text before and after date
    :rtype: DateParseResult

    :Example:

    >>> parse_date_string("until 2024-11-27")
    DateParseResult(date=datetime(2024, 11, 27), before="until", after="")

    >>> parse_date_string("no date here")
    DateParseResult(date=None, before="no date here", after="")
    """
    date_pattern = r"(\b\d{4}-\d{2}-\d{2}\b)"
    input_string = str(input_string)
    match = re.search(date_pattern, input_string)
    if match:
        date_str = match.group(0)
        date_object = datetime.strptime(date_str, "%Y-%m-%d")
        before = input_string[: match.start()].strip()
        after = input_string[match.end() :].strip()
        return DateParseResult(date=date_object, before=before, after=after)
    else:
        before = input_string.strip()
        return DateParseResult(date=None, before=before, after="")


def format_log_entries(
    log_entries: list[tuple[datetime, str, str]],
    *,
    next_action: NextAction | None = None,
) -> str:
    """
    Format log entries into a structured log string.

    :param log_entries: List of log entries.
    :type log_entries: list[tuple[datetime, str, str]]
    :param next_action: NextAction instance
    :type next_action: :class:'NextAction'
    :return: Formatted log string.
    :rtype: str
    """
    log_content = ""
    task_status = " "

    if next_action:
        priority = next_action.priority
        gtd_list = next_action.gtd_list
        dates = next_action.dates
    else:
        priority = "🔼"
        gtd_list = "#gtd/act/now"
        dates = ""

    for date, before, after in log_entries:
        task_props = ""

        if not after:
            log_content += f"- [i] {date.strftime('%Y-%m-%d %H:%M')} - {before}\n"
        else:
            if gtd_list:
                gtd_list = f" {gtd_list} "
            else:
                gtd_list = " "

            if dates:
                task_props = f" |{gtd_list}{priority} {dates}"
            else:
                task_props = f" |{gtd_list}{priority}"
            log_content += f"- [{task_status}] {date.strftime('%Y-%m-%d %H:%M')} - {before} => {after}{task_props}\n"
            task_status = "x"
            gtd_list = ""
    return log_content
