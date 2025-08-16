from enum import Enum


class EventSinkType(str, Enum):
    PAGERDUTY = "PagerDuty"
    SLACK = "Slack"
    TINES = "Tines"
    WEBHOOK = "Webhook"

    def __str__(self) -> str:
        return str(self.value)
