"""
This module defines the ProjectZettel class, which extends the functionality of the :class:`Zettel` class by integrating project-specific migration and consistency services.

The module imports necessary classes from the `doogat.core.domain.entities.project.services.consistency` and
`doogat.core.domain.entities.project.services.migration` packages, specifically for handling the consistency
and migration of project Zettels.

Classes:
    ProjectZettel: Represents a project-specific Zettel with additional methods for migration and consistency checks.

Imports:
    ProjectZettelConsistencyService: A service class from `project.services.consistency` used to ensure data consistency.
    ProjectZettelMigrationService: A service class from `project.services.migration` used to handle data migration.
    Zettel: The base class for Zettel objects, extended by ProjectZettel to include project-specific functionality.
"""

from doogat.core.domain.entities.project.services.consistency.project_zettel_consistency_service import (
    ProjectZettelConsistencyService,
)
from doogat.core.domain.entities.project.services.migration.project_zettel_migration_service import (
    ProjectZettelMigrationService,
)
from doogat.core.domain.entities.zettel.zettel import Zettel


class ProjectZettel(Zettel):
    """
    Represents a Zettel specific to projects, providing custom migration and consistency services.

    Inherits from :class:`Zettel` and adds project-specific methods for data migration and consistency checks.
    """

    def __init__(self: "ProjectZettel") -> None:
        """Initialize the ProjectZettel instance by calling the initializer of the superclass :class:`Zettel`."""
        super().__init__()

    def _migrate(self: "ProjectZettel") -> None:
        """
        Perform migration operations specific to project Zettels.

        This method extends the base migration method by also invoking the project-specific migration service.

        :return: None. The function modifies the internal state in place.
        """
        super()._migrate()
        ProjectZettelMigrationService.migrate(self._data)

    def _ensure_consistency(self: "ProjectZettel") -> None:
        """
        Ensure consistency of the project Zettel's data.

        This method extends the base consistency check by also invoking the project-specific consistency service.

        :return: None. The function modifies the internal state in place.
        """
        super()._ensure_consistency()
        ProjectZettelConsistencyService.ensure_consistency(self._data)

    @property
    def log(self: "ProjectZettel") -> str:
        """
        Retrieve the log section from the Zettel's data.

        This property scans through the sections of the Zettel's data, looking for a section titled "## Log"
        and returns its content if found, otherwise returns an empty string.

        :return: The content of the log section if it exists, otherwise an empty string.
        :rtype: str
        """
        return next(
            (section[1] for section in self._data.sections if section[0] == "## Log"),
            "",
        )

    @property
    def us(self: "ProjectZettel") -> str | None:
        """
        Retrieve user story from Zettel's data.

        This property will return reference with key us if found.

        :return: The content of reference field with us key.
        :rtype: str | None
        """
        return self._data.reference.get("us", None)

    @us.setter
    def us(self: "ProjectZettel", value: str) -> None:
        self._data.reference["us"] = value

    def add_log_entry(self: "ProjectZettel", entry: str) -> None:
        """
        Add a new entry to the log section of the Zettel.

        This method appends the provided entry to the log section of the Zettel's data.

        :param entry: The new log entry to add.
        :type entry: str
        :return: None. The function modifies the internal state in place.
        """
        updated_sections = []
        for section in self._data.sections:
            title, content = section
            if title == "## Log":
                new_content = f"{entry.strip()}{content}"
                updated_sections.append((title, new_content))
            else:
                updated_sections.append(section)
        self._data.sections = [sec for sec in updated_sections if sec[0] != ""]
        self._ensure_consistency()
        self._migrate()
        self._ensure_consistency()
        self._alias_attributes()
