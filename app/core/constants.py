from enum import Enum


class ServiceStatus(str, Enum):
    scheduled = "scheduled"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"
    no_show = "no_show"
    delayed = "delayed"
    paused = "paused"
