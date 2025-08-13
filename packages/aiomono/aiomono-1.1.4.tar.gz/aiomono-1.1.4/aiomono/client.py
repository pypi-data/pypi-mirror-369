import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Union

import httpx

from aiomono.exceptions import MonoException, ToManyRequests
from aiomono.types import ClientInfo, Currency, StatementItem
from aiomono.utils import validate_token

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('mono')

API_ENDPOINT = 'https://api.monobank.ua'


class MonoClient:

    def __init__(self):
        self._session: Optional[httpx.AsyncClient] = None

    async def get_currency(self) -> List[Currency]:
        """Returns list of courses"""
        currency_list = await self._get('/bank/currency')
        return [Currency(**currency) for currency in currency_list]

    async def _check_response(self, response: httpx.Response) -> Union[List, Dict]:
        logger.debug(f'({response.status_code}) Response: '
                     f'{response.text}, {response.json()}, {response.headers}')
        if not response.status_code == 200:
            if response.status_code == 429:
                raise ToManyRequests(response.text)
            raise MonoException(response.text)
        return response.json()

    async def _request(self, method, endpoint, **kwargs) -> Any:
        return await self._check_response(await self.session.request(method, API_ENDPOINT + endpoint, **kwargs))

    async def _get(self, endpoint: str, **kwargs) -> Union[List, Dict]:
        return await self._request('GET', endpoint, **kwargs)

    async def _post(self, endpoint: str, **kwargs) -> Union[List, Dict]:
        return await self._request('POST', endpoint, **kwargs)

    @property
    def session(self) -> httpx.AsyncClient:
        if not self._session or self._session.is_closed:
            self._session = httpx.AsyncClient()
        return self._session

    async def close(self) -> None:
        await self._session.aclose()

    def __enter__(self):
        raise RuntimeError('Use "async with" instead of simple "with" context manager')

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    async def __aenter__(self):
        self._session = httpx.AsyncClient()
        return self

    async def __aexit__(self, *args):
        await self.close()


class PersonalMonoClient(MonoClient):
    def __init__(self, token: str):
        super().__init__()

        self.__token = token
        self.__headers = {'X-Token': self.__token}

        validate_token(self.__token)

    async def client_info(self) -> ClientInfo:
        """Returns client info"""
        client_info = await self._get('/personal/client-info', headers=self.__headers)
        return ClientInfo(**client_info)

    async def set_webhook(self, webhook_url: str) -> httpx.Response:
        """Setting new webhook url"""
        payload = {"webHookUrl": webhook_url}
        response = await self._post('/personal/webhook', json=payload, headers=self.__headers)
        return response

    async def get_statement(
        self,
        account_id: str,
        date_from: datetime = datetime.now(timezone.utc) - timedelta(days=31, hours=1),
        date_to: datetime = datetime.now(timezone.utc),
    ):
        """Returns list of statement items"""
        date_from = int(date_from.replace(tzinfo=timezone.utc).timestamp())
        date_to = int(date_to.replace(tzinfo=timezone.utc).timestamp())
        endpoint = f'/personal/statement/{account_id}/{date_from}/{date_to}'
        statement_items = await self._get(endpoint, headers=self.__headers)
        return [StatementItem(**statement_item) for statement_item in statement_items]


class CorporateMonoClient(MonoClient):
    def __init__(self, token: str):
        raise NotImplementedError('Corporate Mono Client is not implemented yet')
