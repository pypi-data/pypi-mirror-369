from enum import Enum


class AdminAnnouncementsListFieldItem(str, Enum):
    ACTIVE_FROM = "active_from"
    ACTIVE_TO = "active_to"
    CREATED = "created"
    DESCRIPTION = "description"
    IS_ACTIVE = "is_active"
    TYPE = "type"
    UUID = "uuid"

    def __str__(self) -> str:
        return str(self.value)
