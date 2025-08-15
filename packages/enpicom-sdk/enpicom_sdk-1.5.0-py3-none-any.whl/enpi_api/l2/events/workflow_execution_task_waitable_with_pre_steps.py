from typing import Callable, Generic, Optional, TypeVar

from enpi_api.l2.events.workflow_execution_task_waitable import WorkflowExecutionTaskWaitable
from enpi_api.l2.types.task import TaskState
from enpi_api.l2.types.workflow import WorkflowExecutionId, WorkflowExecutionTaskId, WorkflowTaskTemplateName

T = TypeVar("T")


class WorkflowExecutionTaskWaitableWithPreSteps(Generic[T]):
    def __init__(
        self,
        pre_steps: Callable[[], tuple[WorkflowExecutionId, WorkflowTaskTemplateName]],
        on_complete: Optional[Callable[[WorkflowExecutionTaskId, TaskState], T]] = None,
    ) -> None:
        self.pre_steps = pre_steps
        self.on_complete = on_complete

    def wait(self) -> None:
        workflow_execution_id, task_template_name = self.pre_steps()

        if type(workflow_execution_id) not in [WorkflowExecutionId, int]:
            raise TypeError("pre_steps function must return a valid WorkflowExecutionId")

        waitable = WorkflowExecutionTaskWaitable(workflow_execution_id, task_template_name, self.on_complete)

        waitable.wait()

        return None

    def wait_and_return_result(self) -> T:
        workflow_execution_id, task_template_name = self.pre_steps()

        if type(workflow_execution_id) not in [WorkflowExecutionId, int]:
            raise TypeError("pre_steps function must return a valid WorkflowExecutionId")

        waitable = WorkflowExecutionTaskWaitable(workflow_execution_id, task_template_name, self.on_complete)

        result = waitable.wait_and_return_result()

        assert result is not None
        return result
