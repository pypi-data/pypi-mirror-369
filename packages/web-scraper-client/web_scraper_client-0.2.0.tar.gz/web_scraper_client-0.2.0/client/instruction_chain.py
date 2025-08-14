from copy import deepcopy

from client.enums.action_type import ActionType
from client.enums.block_type import BlockType
from client.enums.element_type import ElementCondition
from client.enums.identificator_type import ElementIdentification


class InstructionChain:
    def __init__(self):
        self._instructions: list[object] = []

    def to_list(self) -> list[object]:
        return deepcopy(self._instructions)

    def wait_for(self, seconds: int, by: ElementIdentification, wait_for: ElementCondition,
                 element_id: str, ignore_error: bool = False):
        self._instructions.append({
            'action_type': ActionType.WAIT_FOR.value,
            'action_value': {
                'seconds': seconds,
                'by': by.value,
                'wait_for': wait_for.value,
                'id': element_id
            },
            'action_ignore_error': ignore_error
        })
        return self

    def find(self, by: ElementIdentification, element_id: str, ignore_error: bool = False):
        self._instructions.append({
            'action_type': ActionType.FIND.value,
            'action_value': {
                'by': by.value,
                'id': element_id
            },
            'action_ignore_error': ignore_error
        })
        return self

    def click(self, ignore_error: bool = False):
        self._instructions.append({
            'action_type': ActionType.CLICK.value,
            'action_ignore_error': ignore_error
        })
        return self

    def scroll(self, block: BlockType, seconds: int = 5, ignore_error: bool = False):
        self._instructions.append({
            'action_type': ActionType.SCROLL.value,
            'action_value': {
                'block': block.value,
                'seconds': seconds
            },
            'action_ignore_error': ignore_error
        })
        return self

    def wait(self, seconds: int):
        self._instructions.append({
            'action_type': ActionType.WAIT.value,
            'action_value': {
                'seconds': seconds
            }
        })
        return self

    def input(self, text: str):
        self._instructions.append({
            'action_type': ActionType.INPUT.value,
            'action_value': {
                'text': text
            }
        })
        return self

    def select_by_value(self, value: str):
        self._instructions.append({
            'action_type': ActionType.SELECT_BY_VALUE.value,
            'action_value': {
                'value': value
            }
        })
        return self

    def repeat_while(self, instructions: "InstructionChain", max_iterations: int, by: ElementIdentification, element_id: str,
                     while_: ElementCondition, wait_for_seconds: int = 1, element_text: str = ''):
        self._instructions.append({
            'action_type': ActionType.REPEAT_WHILE.value,
            'action_value': {
                'instructions': instructions.to_list(),
                'by': by.value,
                'id': element_id,
                'while_': while_.value,
                'wait_for_seconds': wait_for_seconds,
                'element_text': element_text,
                'max_iterations': max_iterations
            }
        })
        return self

    def get_page_source(self):
        self._instructions.append({
            'action_type': ActionType.GET_PAGE_SOURCE.value
        })
        return self

    def get_xhr(self, document_name: str):
        self._instructions.append({
            'action_type': ActionType.GET_XHR.value,
            'action_value': {
                'document_name': document_name
            }
        })
        return self

    def finish(self):
        self._instructions.append({
            'action_type': ActionType.FINISH.value
        })
        return self
