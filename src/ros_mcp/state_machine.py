"""ROS node lifecycle state machine — adapted from mujoco-mcp's SimStateMachine.

States: IDLE -> NODE_REGISTERED -> RUNNING -> STOPPING -> STOPPED -> CRASHED

Simpler than the MuJoCo version because ROS nodes don't have physics state
(mesh loading, rendering, etc.). This tracks background process lifecycle
for ros2 launch and ros2 bag jobs.
"""

from __future__ import annotations

import enum
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


class RosState(enum.Enum):
    """Finite states for a ROS process lifecycle."""

    IDLE = "idle"
    NODE_REGISTERED = "node_registered"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    CRASHED = "crashed"
    ERROR = "error"

    def terminal(self) -> bool:
        return self in (RosState.STOPPED, RosState.CRASHED, RosState.ERROR)

    def can_start(self) -> bool:
        return self in (RosState.NODE_REGISTERED, RosState.STOPPED, RosState.CRASHED)


@dataclass
class RosJob:
    """Stateful ROS process job with lifecycle tracking."""

    job_id: str
    label: str
    job_type: str  # "launch" | "bag_record" | "bag_play"
    state: RosState = RosState.IDLE

    process: Any = None
    pid: int | None = None

    created_at: float = field(default_factory=time.time)
    started_at: float | None = None
    stopped_at: float | None = None
    state_changed_at: float = field(default_factory=time.time)

    error_message: str | None = None
    exit_code: int | None = None

    _on_enter_state: dict[RosState, list[Callable]] = field(default_factory=dict)

    def transition_to(self, new_state: RosState, reason: str = "") -> None:
        valid = self._valid_transitions().get(self.state, set())
        if new_state not in valid and self.state != new_state:
            logger.warning(
                "Invalid transition %s -> %s for job %s",
                self.state.value,
                new_state.value,
                self.job_id,
            )
            self.state = RosState.ERROR
            self.error_message = f"Invalid transition: {self.state.value} -> {new_state.value}"
            return

        old = self.state
        self.state = new_state
        self.state_changed_at = time.time()
        logger.info(
            "Job %s: %s -> %s%s",
            self.job_id,
            old.value,
            new_state.value,
            f" ({reason})" if reason else "",
        )

        for cb in self._on_enter_state.get(new_state, []):
            try:
                cb(self)
            except Exception as e:
                logger.exception("State callback failed: %s", e)

    def uptime(self) -> float:
        if self.started_at and not self.stopped_at:
            return time.time() - self.started_at
        if self.started_at and self.stopped_at:
            return self.stopped_at - self.started_at
        return 0.0

    def info(self) -> dict[str, Any]:
        return {
            "job_id": self.job_id,
            "label": self.label,
            "job_type": self.job_type,
            "state": self.state.value,
            "state_changed_at": self.state_changed_at,
            "pid": self.pid,
            "uptime_s": round(self.uptime(), 1),
            "error": self.error_message,
            "exit_code": self.exit_code,
        }

    @staticmethod
    def _valid_transitions() -> dict[RosState, set[RosState]]:
        return {
            RosState.IDLE: {RosState.NODE_REGISTERED, RosState.ERROR},
            RosState.NODE_REGISTERED: {RosState.RUNNING, RosState.IDLE, RosState.ERROR},
            RosState.RUNNING: {RosState.STOPPING, RosState.CRASHED, RosState.ERROR},
            RosState.STOPPING: {RosState.STOPPED, RosState.CRASHED, RosState.ERROR},
            RosState.STOPPED: {RosState.NODE_REGISTERED, RosState.IDLE, RosState.ERROR},
            RosState.CRASHED: {RosState.NODE_REGISTERED, RosState.IDLE, RosState.ERROR},
            RosState.ERROR: {RosState.IDLE},
        }


# ---------------------------------------------------------------------------
# Transition helpers
# ---------------------------------------------------------------------------


def on_enter(job: RosJob, state: RosState, fn: Callable) -> None:
    if state not in job._on_enter_state:
        job._on_enter_state[state] = []
    job._on_enter_state[state].append(fn)


def transition_registered(job: RosJob, process: Any, label: str, job_type: str) -> None:
    assert job.state == RosState.IDLE, f"Cannot register from {job.state.value}"
    job.process = process
    job.pid = process.pid if process else None
    job.label = label
    job.job_type = job_type
    job.started_at = time.time()
    job.transition_to(RosState.NODE_REGISTERED, f"type={job_type}, label={label}")


def transition_running(job: RosJob) -> None:
    job.transition_to(RosState.RUNNING)


def transition_stopping(job: RosJob) -> None:
    job.transition_to(RosState.STOPPING)


def transition_stopped(job: RosJob, exit_code: int = 0) -> None:
    job.exit_code = exit_code
    job.stopped_at = time.time()
    job.process = None
    job.transition_to(RosState.STOPPED, f"exit={exit_code}")


def transition_crashed(job: RosJob, reason: str, exit_code: int | None = None) -> None:
    job.error_message = reason
    job.exit_code = exit_code
    job.stopped_at = time.time()
    job.process = None
    job.transition_to(RosState.CRASHED, reason)


def transition_reset(job: RosJob) -> None:
    assert job.state.terminal(), f"Can only reset from terminal states, got {job.state.value}"
    job.process = None
    job.error_message = None
    job.exit_code = None
    job.transition_to(RosState.IDLE)
