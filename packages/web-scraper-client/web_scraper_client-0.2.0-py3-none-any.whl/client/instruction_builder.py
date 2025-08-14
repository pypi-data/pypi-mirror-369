from client.models.driver_options import DriverOptions

from client.api_sender import ApiSender
from client.bound_instruction_chain import BoundInstructionChain


class InstructionBuilder:
    def __init__(self, url: str, api_key: str, page_url: str, options: DriverOptions):
        self._sender = ApiSender(url, api_key, page_url, options)

    def chain(self) -> BoundInstructionChain:
        return BoundInstructionChain(self._sender)

    def build(self) -> ApiSender:
        return self._sender