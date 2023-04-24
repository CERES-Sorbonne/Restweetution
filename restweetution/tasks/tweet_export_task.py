import asyncio
import logging

from restweetution import data_view
from restweetution.data_view.view_exporter import ViewExporter
from restweetution.models.linked.storage_collection import StorageCollection
from restweetution.models.storage.custom_data import CustomData
from restweetution.models.storage.queries import ExportQuery
from restweetution.models.view_types import ViewType
from restweetution.storages.exporter.exporter import Exporter, FileExporter
from restweetution.storages.postgres_jsonb_storage.postgres_jsonb_storage import PostgresJSONBStorage
from restweetution.tasks.server_task import ServerTask


logger = logging.getLogger('ViewExportTask')

class ViewExportTask(ServerTask):
    def __init__(self,
                 storage: PostgresJSONBStorage,
                 query: ExportQuery,
                 exporter: Exporter):
        super().__init__(name='Exporter')
        self.storage = storage
        self.query = query
        self.exporter = exporter
        self.view_type = query.query.view_type
        view = data_view.get_view(query.query.view_type)
        self.view_exporter = ViewExporter(view=view, exporter=exporter)
        self.key = query.key

    async def _task_routine(self):
        print('start task routine')
        count = await self.storage.query_count(self.query.query)
        self._max_progress = count

        # define query function according to view type
        if self.view_type == ViewType.TWEET:
            storage_stream_function = self.storage.query_tweets_stream
        elif self.view_type == ViewType.MEDIA:
            storage_stream_function = self.storage.query_medias_stream
        else:
            raise ValueError(f'<<{self.view_type}>> view is not valid')

        async for res in storage_stream_function(self.query.query.collection, chunk_size=1000):
            try:
                coll = StorageCollection(self.storage, res)
                # view specific steps
                # save count of result
                if self.view_type == ViewType.TWEET:
                    count = len(res.tweets)
                    await coll.load_all_from_tweets()
                elif self.view_type == ViewType.MEDIA:
                    count = len(res.medias)

                view = coll.build_view(self.view_type, self.query.fields)
                datas = [CustomData(key=self.key, id=d.id(), data=d) for d in view.view]
                await self.exporter.save_custom_datas(datas)

                self._progress += count
            except Exception as e:
                logger.error(e)

            await asyncio.sleep(0)

    def get_info(self):
        info = super().get_info()
        info.key = self.key
        return info


class ViewExportFileTask(ViewExportTask):
    exporter: FileExporter

    def __init__(self,
                 storage: PostgresJSONBStorage,
                 query: ExportQuery,
                 exporter: FileExporter):
        super().__init__(storage=storage, query=query, exporter=exporter)
        self.name = 'FileExporter'

    async def _task_routine(self):
        await self.exporter.clear_key(self.key)
        await super()._task_routine()
        self.result['path'] = (self.exporter.get_root() / self.key).__str__()
