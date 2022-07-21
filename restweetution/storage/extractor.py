from typing import List

from restweetution.storage.document_storages.document_storage import Storage


class BaseExtractor:
    @staticmethod
    async def get_tweets(storages: List[Storage]):
        return await BaseExtractor.get_no_duplicate(storages, lambda s: s.get_tweets)

    @staticmethod
    async def get_users(storages: List[Storage]):
        return await BaseExtractor.get_no_duplicate(storages, lambda s: s.get_users)

    @staticmethod
    async def get_rules(storages: List[Storage]):
        return await BaseExtractor.get_no_duplicate(storages, lambda s: s.get_rules)

    @staticmethod
    async def get_polls(storages: List[Storage]):
        return await BaseExtractor.get_no_duplicate(storages, lambda s: s.get_polls)

    @staticmethod
    async def get_places(storages: List[Storage]):
        return await BaseExtractor.get_no_duplicate(storages, lambda s: s.get_places)

    @staticmethod
    async def get_medias(storages: List[Storage]):
        return await BaseExtractor.get_no_duplicate(storages,
                                                    get_lambda=lambda s: s.get_medias,
                                                    id_lambda=lambda m: m.media_key)

    @staticmethod
    async def get_no_duplicate(storages: List[Storage], get_lambda, id_lambda=lambda o: o.id):
        ignore_ids = []
        result = []
        for s in storages:
            res = await get_lambda(s)(no_ids=ignore_ids)
            ignore_ids.extend([id_lambda(r) for r in res])
            result.extend(res)
        return result
