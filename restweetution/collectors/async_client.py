import logging
import traceback
from typing import Callable, List
from urllib.parse import urljoin

import aiohttp

from restweetution.models.stream_rule import RuleResponse


class AsyncClient(aiohttp.ClientSession):
    def __init__(self, token: str, base_url: str = "https://api.twitter.com/2/", error_handler: Callable = None):
        super().__init__()
        self.base_url = base_url
        self.headers.update({"Authorization": f"Bearer {token}"})
        self._error_handler = error_handler
        self._logger = logging.getLogger("ApiClient")

    def set_error_handler(self, error_handler: Callable):
        self._error_handler = error_handler

    def _request(self, method, url, **kwargs):
        modified_url = urljoin(self.base_url, url)
        try:
            res = super()._request(method, modified_url, **kwargs)
            return res
        except aiohttp.ClientResponseError as e:
            self._error_handler(str(e), e.message)

    async def connect_tweet_stream(self, params, line_callback, error_callback=None):
        async with self as session:
            async with session.get("https://api.twitter.com/2/tweets/search/stream", params=params) as resp:
                async for line in resp.content:
                    try:
                        line_callback(line)
                    except BaseException as e:
                        if error_callback:
                            error_callback(e)
                        else:
                            self._logger.exception(traceback.format_exc())

    async def remove_rules(self, ids: List[str]):
        """
                Remove rules by ids
                :param ids: a list of ids of rules to remove
                """

        uri = "tweets/search/stream/rules"
        async with self.post(uri, json={
            "delete": {
                "ids": ids
            }
        }) as r:
            res = await r.json()

            # if everything went fine we return the ids of the deleted rules
            if "errors" not in res:
                self._logger.info(f'Removed {res["meta"]["summary"]["deleted"]} rule(s)')
                return ids

            # if not, return no ids as we can't know what rule failed or not
            self._logger.error(res)
            return []

    async def get_rules(self, ids: List[str] = None):
        """
        Return the list of rules defined to collect tweets during a stream
        from the Twitter API
        :param ids: an optional list of ids to fetch only specific rules
        :return: the list of rules
        """

        uri = "tweets/search/stream/rules"
        if ids:
            uri += f"?ids={','.join(ids)}"
        async with self.get(uri) as r:
            res = await r.json()
            if not res.get('data'):
                res['data'] = []
            res = RuleResponse(**res)
            # print(res)
            return res.data

    async def add_rules(self, rules):
        uri = "tweets/search/stream/rules"
        async with self.post(uri, json={
            "add": rules
        }) as r:
            res = await r.json()
            valid_rules = []
            if 'errors' in res:
                errs = res['errors']
                for err in errs:
                    self._logger.info(f"add_rules Error: {err['title']} Rule: {err['value']}")
            if 'data' in res:
                valid_rules = res['data']
            return valid_rules
