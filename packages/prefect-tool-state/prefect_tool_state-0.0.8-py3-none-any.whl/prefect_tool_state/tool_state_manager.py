from .tool_state_publisher import get_tool_state_publisher
from .tool_state import ToolState
from typing import List


class ToolStateManager:
    def __init__(self, tool_name: str, steps: List[str]):
        self.publisher = get_tool_state_publisher()
        self.tool_state = ToolState(
            tool_name=tool_name,
            step_name="",
            message="",
            total_files=0,
            processed_files=0,
            steps=steps,
            current_file_name=""
        )

    def starting_tool(self):
        new_state = self.tool_state.build(state="RUNNING")
        self.publisher.publish_data(new_state)

    def completed_tool(self):
        new_state = self.tool_state.build(state="COMPLETED")
        self.publisher.publish_data(new_state)

    def failed_tool(self, error_message: str):
        new_state = self.tool_state.build(state="FAILED", message=error_message)
        self.publisher.publish_data(new_state)

    def publish_step_details(self, **kwargs):
        new_state = self.tool_state.build(**kwargs)
        self.publisher.publish_data(new_state)
    
    def finish(self):
        self.publisher.shutdown()
