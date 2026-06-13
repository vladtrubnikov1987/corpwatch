from dataclasses import dataclass
from typing import Optional


@dataclass
class MonitoringTarget:
    id: Optional[int]
    user_id: int
    name: str
    url: str
    expected_status: int = 200
    timeout_seconds: int = 5
    max_response_time_ms: int = 1000
    check_interval_seconds: int = 60
    failure_threshold: int = 3
    consecutive_failures: int = 0
    is_active: bool = True