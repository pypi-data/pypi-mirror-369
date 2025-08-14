from client.api_sender import ApiSender
from client.instruction_chain import InstructionChain
from client.models.api_result import ApiResult


class BoundInstructionChain(InstructionChain):
    def __init__(self, sender: ApiSender):
        super().__init__()
        self._sender = sender

    def build(self) -> list[ApiResult]:
        return self._sender.build(instructions=self)