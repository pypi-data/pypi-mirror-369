import requests

from client.instruction_chain import InstructionChain
from client.models.api_result import ApiResult
from client.models.driver_options import DriverOptions
from client.util.exceptions import ScrapeException


class ApiSender:
    def __init__(self, base_url: str, api_key: str, page_url: str, options: DriverOptions):
        self._url: str = base_url
        self._api_key: str = api_key
        self._page_url: str = page_url
        self._options: DriverOptions = options

    def build(self, instructions: InstructionChain) -> list[ApiResult]:
        headers = {'Content-Type': 'application/json', 'x-api-key': self._api_key}
        data = {
            'url': self._page_url,
            'options': self._options.__dict__() if self._options else None,
            'instructions': instructions.to_list()
        }
        resp = requests.post(url=f'{self._url}/api/v1/instructions', json=data, headers=headers)
        if resp.status_code in (403, 422, 500):
            raise ScrapeException(resp.text)
        resp.raise_for_status()
        return [ApiResult.model_validate(item) for item in resp.json()]
