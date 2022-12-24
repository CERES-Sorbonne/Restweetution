import asyncio
import logging
from typing import Callable, List

import aiohttp
from aiohttp import ClientTimeout

from restweetution.models.config.query_fields import QueryFields
from restweetution.models.config.user_config import RuleConfig
from restweetution.models.rule import StreamRuleResponse, StreamAPIRule


class TwitterClient:
    def __init__(self, token: str, base_url: str = "https://api.twitter.com", error_handler: Callable = None):
        super().__init__()
        self.base_url = base_url
        self._headers = {"Authorization": f"Bearer {token}"}
        self._error_handler = error_handler
        self._logger = logging.getLogger("ApiClient")
        self._client = None

    def _get_client(self):
        connector = aiohttp.TCPConnector(force_close=True, enable_cleanup_closed=True)
        self._client = aiohttp.ClientSession(headers=self._headers,
                                             timeout=ClientTimeout(),
                                             base_url=self.base_url,
                                             connector=connector)
        return self._client

    def set_error_handler(self, error_handler: Callable):
        self._error_handler = error_handler

    async def connect_tweet_stream(self, params: QueryFields):
        self._logger.info('Connect to stream')
        wait_time = 0
        while True:
            try:
                async with self._get_client() as session:
                    async with session.get("/2/tweets/search/stream", params=params.twitter_format(join='.')) as resp:
                        async for line in resp.content:
                            # print(resp.headers)
                            yield line
            except KeyboardInterrupt as e:
                raise e
            except BaseException as e:
                self._logger.warning(f'Tweet Stream {e}')
                raise e
            print('wait: ', wait_time)
            await asyncio.sleep(wait_time)
            wait_time = min(max(wait_time * 2, 1), 30)

    async def remove_rules(self, ids: List[str]):
        """
                Remove rules by ids
                :param ids: a list of ids of rules to remove
                """

        uri = "/2/tweets/search/stream/rules"
        # session = self._get_client()
        async with self._get_client() as session:
            async with session.post(uri, json={"delete": {"ids": ids}}) as r:
                res = await r.json()

                # if everything went fine we return the ids of the deleted rules
                if "errors" not in res:
                    self._logger.info(f'Removed {res["meta"]["summary"]["deleted"]} rule(s)')
                    return ids

                # if not, return no ids as we can't know what rule failed or not
                self._logger.error(res)
            return []

    async def get_rules(self, ids: List[str] = None) -> List[StreamAPIRule]:
        """
        Return the list of rules defined to collect tweets during a stream
        from the Twitter API
        :param ids: an optional list of ids to fetch only specific rules
        :return: the list of rules
        """

        uri = "/2/tweets/search/stream/rules"
        if ids:
            uri += f"?ids={','.join(ids)}"
        # session = self._get_client()
        async with self._get_client() as session:
            async with session.get(uri) as r:
                res = await r.json()
                if not res.get('data'):
                    res['data'] = []
                # print(res)
                res = StreamRuleResponse(**res)
                # rules = [StreamerRule(tag=r.tag, query=r.value, api_id=r.id) for r in res.data]
                rules = res.data
                return rules

    async def add_rules(self, rules: List[StreamAPIRule]):
        uri = "/2/tweets/search/stream/rules"
        rules_data = [{'tag': r.tag, 'value': r.value} for r in rules]
        async with self._get_client() as session:
            async with session.post(uri, json={"add": rules_data}) as r:
                res = await r.json()
                valid_rules = []
                if 'errors' in res:
                    errs = res['errors']
                    for err in errs:
                        self._logger.info(f"add_rules Error: {err['title']} Rule: {err['value']}")
                if 'data' in res:
                    valid_rules = res['data']
                return [StreamAPIRule(**r) for r in valid_rules]

    async def test_rule(self, rule: RuleConfig):
        uri = "/2/tweets/search/stream/rules"
        rule_data = [{'tag': rule.tag, 'value': rule.query}]
        async with self._get_client() as session:
            async with session.post(uri, json={"add": rule_data}, params={'dry_run': 'true'}) as r:
                res = await r.json()
                valid = 'errors' not in res
                error = None if valid else res['errors']
                return {'valid': valid, 'error': error}
