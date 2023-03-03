from typing import List, Protocol

from restweetution.storages.storage import Storage


class StorageJoinFunction(Protocol):
    async def __call__(self, storages: List[Storage], get_lambda, id_lambda=lambda o: o.id) -> None: ...


async def get_no_duplicate(storages: List[Storage],
                           get_lambda,
                           id_lambda=lambda o: o.id,
                           ids: List[str] = None,
                           no_ids: List[str] = None,
                           fields: List[str] = None,
                           **kwargs):
    ignore_ids = []
    if no_ids:
        ignore_ids.extend(no_ids)
    result = []
    for s in storages:
        res = await get_lambda(s)(ids=ids, no_ids=ignore_ids, fields=fields, **kwargs)
        ignore_ids.extend([id_lambda(r) for r in res])
        result.extend(res)
    return result


class FirstFoundJoin:
    @staticmethod
    async def get_tweets(storages: List[Storage], **kwargs):
        return await get_no_duplicate(storages, lambda s: s.get_tweets, **kwargs)

    @staticmethod
    async def get_users(storages: List[Storage], **kwargs):
        return await get_no_duplicate(storages, lambda s: s.get_users, **kwargs)

    @staticmethod
    async def get_rules(storages: List[Storage], **kwargs):
        return await get_no_duplicate(storages, lambda s: s.get_rules, **kwargs)

    @staticmethod
    async def get_polls(storages: List[Storage], **kwargs):
        return await get_no_duplicate(storages, lambda s: s.get_polls, **kwargs)

    @staticmethod
    async def get_places(storages: List[Storage], **kwargs):
        return await get_no_duplicate(storages, lambda s: s.get_places, **kwargs)

    @staticmethod
    async def get_medias(storages: List[Storage], **kwargs):
        return await get_no_duplicate(storages,
                                      get_lambda=lambda s: s.get_medias,
                                      id_lambda=lambda m: m.media_key,
                                      **kwargs)
