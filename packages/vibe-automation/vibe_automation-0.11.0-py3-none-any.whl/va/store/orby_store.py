import logging
from collections import defaultdict
from typing import Any

from va.models import ReviewStatus, ReviewModal
from va.store.store import Store
from va.clients.execution_service_client import (
    request_review,
    get_review_status,
    update_execution_status,
)
from va.protos.orby.va.public.execution_messages_pb2 import ExecutionStatus
from va.utils import is_test_execution


logger = logging.getLogger(__name__)


class ExecutionState:
    executed_steps: list[str] = []
    executing_steps: list[str] = []
    input: Any
    data: dict[str, Any] = dict()
    reviews: dict[str, ReviewModal] = dict()


class OrbyStore(Store):
    execution_state: dict[str, ExecutionState]

    def __init__(self):
        self.execution_state = defaultdict(ExecutionState)

    def save_execution_data(self, execution_id: str, key: str, value: Any):
        logger.info(f"save_execution_data {key} {value}")
        self.execution_state[execution_id].data[key] = value

    def get_execution_data(self, execution_id: str, key: str):
        logger.info(f"get_execution_data {key}")
        return self.execution_state[execution_id].data[key]

    def get_execution_input(self, execution_id: str):
        logger.info("get_execution_input")
        return self.execution_state[execution_id].input

    def mark_step_executed(self, execution_id: str, step: str):
        logger.info(f"mark_step_executed {step}")
        execution_state = self.execution_state[execution_id]
        execution_state.executing_steps.remove(step)
        execution_state.executed_steps.append(step)

    def mark_step_executing(self, execution_id: str, step: str):
        logger.info(f"mark_step_executing {step}")
        self.execution_state[execution_id].executing_steps.append(step)

    def create_review(self, execution_id: str, review: ReviewModal):
        logger.info(f"create_review {review}")
        review.id = request_review(execution_id, review.instruction)
        self.execution_state[execution_id].reviews[review.id] = review

    def get_review(self, execution_id: str, review_id: str):
        logger.info(f"get_review {review_id}")
        status = get_review_status(review_id)
        if status == ReviewStatus.READY.value:
            self.set_review_status(execution_id, review_id, ReviewStatus.READY)
        return self.execution_state[execution_id].reviews.get(review_id)

    def set_execution_input(self, execution_id: str, input: Any):
        logger.info(f"set_execution_input {input}")
        self.execution_state[execution_id].input = input

    def set_review_status(
        self, execution_id: str, review_id: str, status: ReviewStatus
    ):
        logger.info(f"set_review_status {review_id} {status}")
        self.execution_state[execution_id].reviews[review_id].status = status

    def set_review_data(self, execution_id: str, review_id: str, data: Any):
        logger.info(f"set_review_data {review_id} {data}")
        self.execution_state[execution_id].reviews[review_id].data = data

    def _update_execution_status(
        self, execution_id: str, status: ExecutionStatus.ValueType
    ) -> None:
        if not is_test_execution(execution_id):
            logger.info(f"update_execution_status {status}")
            update_execution_status(execution_id, status)

    def mark_start(self, execution_id: str) -> None:
        logger.info("mark_start")
        self._update_execution_status(execution_id, ExecutionStatus.RUNNING)

    def mark_stop(
        self,
        execution_id: str,
        status: ExecutionStatus.ValueType = ExecutionStatus.COMPLETED,
    ) -> None:
        logger.info("mark_stop")
        self._update_execution_status(execution_id, status)

    def mark_for_review(
        self,
        execution_id: str,
    ) -> None:
        logger.info("mark_for_review")
        self._update_execution_status(execution_id, ExecutionStatus.WAITING_FOR_REVIEW)

    def mark_resume(
        self,
        execution_id: str,
    ) -> None:
        logger.info("mark_resume")
        self._update_execution_status(execution_id, ExecutionStatus.RUNNING)
