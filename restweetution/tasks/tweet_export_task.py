import asyncio

from restweetution.data_view.data_view import DataView
from restweetution.data_view.view_exporter import ViewExporter
from restweetution.models.storage.queries import TweetCountQuery, TweetRowQuery, CollectedTweetQuery
from restweetution.storages.exporter.exporter import Exporter, FileExporter
from restweetution.storages.extractor import Extractor
from restweetution.storages.postgres_jsonb_storage.postgres_jsonb_storage import PostgresJSONBStorage
from restweetution.tasks.server_task import ServerTask


class TweetExportTask(ServerTask):
    def __init__(self,
                 storage: PostgresJSONBStorage,
                 query: TweetRowQuery,
                 view: DataView,
                 exporter: Exporter,
                 key: str):
        super().__init__(name='TweetExporter')
        self.storage = storage
        self.query = query

        self.exporter = exporter
        self.extractor = Extractor(self.storage)
        self.view_exporter = ViewExporter(view=view, exporter=exporter)
        self.key = key

    async def _task_routine(self):
        print('start task routine')
        count_query = TweetCountQuery(**self.query.dict())
        count = await self.storage.get_tweets_count(**count_query.dict())
        self._max_progress = count
        tweet_query = CollectedTweetQuery(**self.query.dict())

        async for res in self.storage.get_collected_tweets_stream(**tweet_query.dict()):
            tweet_ids = set([c.tweet_id for c in res])
            print(f'receive {len(tweet_ids)}')
            bulk = await self.extractor.expand_collected_tweets(res)
            await self.view_exporter.export(bulk_data=bulk, key=self.key, only_ids=list(tweet_ids),
                                            fields=self.query.row_fields)
            self._progress += len(tweet_ids)
            await asyncio.sleep(0)

    def get_info(self):
        info = super().get_info()
        info.key = self.key
        return info


class TweetExportFileTask(TweetExportTask):
    exporter: FileExporter

    def __init__(self,
                 storage: PostgresJSONBStorage,
                 query: TweetRowQuery,
                 view: DataView,
                 exporter: FileExporter,
                 key: str):
        super().__init__(storage=storage, query=query, view=view, exporter=exporter, key=key)
        self.name = 'TweetExportFile'

    async def _task_routine(self):
        await self.exporter.clear_key(self.key)
        await super()._task_routine()
        self.result['path'] = (self.exporter.get_root() / self.key).__str__()
