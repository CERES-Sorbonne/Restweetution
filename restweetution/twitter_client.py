import asyncio
import logging
import traceback
from typing import Callable, List

import aiohttp
from aiohttp import ClientTimeout

from restweetution.models.storage.stream_rule import RuleResponse

default_timeout = ClientTimeout(total=300, sock_read=300, connect=300, sock_connect=300)


class TwitterClient:
    def __init__(self, token: str, base_url: str = "https://api.twitter.com", error_handler: Callable = None):
        super().__init__()
        self.base_url = base_url
        self._headers = {"Authorization": f"Bearer {token}"}
        self._error_handler = error_handler
        self._logger = logging.getLogger("ApiClient")

    def _get_client(self):
        return aiohttp.ClientSession(headers=self._headers, timeout=default_timeout, base_url=self.base_url)

    def set_error_handler(self, error_handler: Callable):
        self._error_handler = error_handler

    async def connect_tweet_stream(self, params, line_callback):
        while True:
            try:
                async with self._get_client() as session:
                    async with session.get("/2/tweets/search/stream", params=params) as resp:
                        async for line in resp.content:
                            asyncio.create_task(line_callback(line))
            except Exception as e:
                trace = traceback.format_exc()
                self._logger.exception(trace)
                self._logger.exception(e)

    async def remove_rules(self, ids: List[str]):
        """
                Remove rules by ids
                :param ids: a list of ids of rules to remove
                """

        uri = "/2/tweets/search/stream/rules"
        async with self._get_client() as session:
            async with session.post(uri, json={"delete": {"ids": ids}}) as r:
                res = await r.json()

                # if everything went fine we return the ids of the deleted rules
                if "errors" not in res:
                    self._logger.info(f'Removed {res["meta"]["summary"]["deleted"]} rule(s)')
                    return ids

                # if not, return no ids as we can't know what rule failed or not
                self._logger.error(res)
            # await session.close()
            return []

    async def get_rules(self, ids: List[str] = None):
        """
        Return the list of rules defined to collect tweets during a stream
        from the Twitter API
        :param ids: an optional list of ids to fetch only specific rules
        :return: the list of rules
        """

        uri = "/2/tweets/search/stream/rules"
        if ids:
            uri += f"?ids={','.join(ids)}"
        async with self._get_client() as session:
            async with session.get(uri) as r:
                res = await r.json()
                if not res.get('data'):
                    res['data'] = []
                res = RuleResponse(**res)
                # print(res)
                return res.data

    async def add_rules(self, rules):
        uri = "/2/tweets/search/stream/rules"
        async with self._get_client() as session:
            async with session.post(uri, json={"add": rules}) as r:
                res = await r.json()
                valid_rules = []
                if 'errors' in res:
                    errs = res['errors']
                    for err in errs:
                        self._logger.info(f"add_rules Error: {err['title']} Rule: {err['value']}")
                if 'data' in res:
                    valid_rules = res['data']
                return valid_rules
