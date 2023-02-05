import asyncio
import logging
import time
from typing import Dict

import aiohttp
import tweepy
from oauthlib.oauth1 import Client as OAuthClient
from pydantic import BaseModel
from tweepy import BadRequest, Unauthorized, Forbidden, NotFound, TooManyRequests, TwitterServerError, HTTPException, \
    Response
from tweepy.asynchronous import AsyncClient
from yarl import URL

log = logging.getLogger(__name__)


class RateLimit(BaseModel):
    limit: int
    remaining: int
    reset: int

    def time_to_reset(self):
        now = time.time()
        if now > self.reset:
            return -1
        return self.reset - now


class Client(AsyncClient):
    def __init__(
            self, bearer_token=None, consumer_key=None, consumer_secret=None,
            access_token=None, access_token_secret=None, *, return_type=Response,
            wait_on_rate_limit=False
    ):
        super().__init__(bearer_token, consumer_key, consumer_secret, access_token, access_token_secret,
                         return_type=return_type, wait_on_rate_limit=wait_on_rate_limit)
        self.rates: Dict[str, RateLimit] = {}

    async def request(
            self, method, route, params=None, json=None, user_auth=False
    ):
        try:
            response = await super().request(method, route, params=params, json=json, user_auth=user_auth)
            rate = RateLimit(limit=response.headers['x-rate-limit-limit'], reset=response.headers['x-rate-limit-reset'],
                             remaining=response.headers['x-rate-limit-remaining'])
            self.rates[route] = rate
            return response
        except tweepy.HTTPException as e:
            response = e.response
            rate = RateLimit(limit=response.headers['x-rate-limit-limit'], reset=response.headers['x-rate-limit-reset'],
                             remaining=response.headers['x-rate-limit-remaining'])
            self.rates[route] = rate
            raise e
