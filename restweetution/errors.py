from restweetution.utils import get_full_class_name


class RESTweetutionError(Exception):
    """Base class for all Custom Errors"""


class NetworkError(RESTweetutionError):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.raw_text = kwargs.get('url')


class UnreadableResponseError(RESTweetutionError):
    def __init__(self, *args):
        super().__init__(*args)


class ResponseParseError(RESTweetutionError):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.raw_text = kwargs.get('raw_text')
        self.data = kwargs.get('data')


class TwitterAPIError(RESTweetutionError):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.data = kwargs.get('data')


class PydanticValidationError(RESTweetutionError):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.data = kwargs.get('data')


class TweetResponseHandleError(RESTweetutionError):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.data = kwargs.get('data')


class StorageError(RESTweetutionError):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.data = kwargs.get('data')
        self.storage_name = kwargs.get('storage_name')
        self.storage_type = kwargs.get('storage_type')
        self.storage_function = kwargs.get('storage_function')


class FunctionNotImplementedError(RESTweetutionError):
    def __init__(self, *args):
        super().__init__(*args)


async def default_handler(e: Exception):
    print("Default Error Handler!!")
    print(e)


# print(err)
ERROR_HANDLER = default_handler


def set_error_handler(callback):
    global ERROR_HANDLER
    # print('set error handler')
    ERROR_HANDLER = callback


def handle_error(fn):
    """
    default error handler for async functions that are called in a new task
    it allows catch errors in tasks that are not awaited
    """

    async def wrapper(*args, **kwargs):
        try:
            if kwargs:
                result = await fn(*args, **kwargs)
            else:
                result = await fn(*args)
            return result
        except Exception as e:
            global ERROR_HANDLER
            await ERROR_HANDLER(e)

    return wrapper


def handle_storage_save_error(datatype='bulk'):
    """
    special error handler for storages functions
    allows to keep trace of which storage had an error and listen to errors in un-awaited tasks
    """

    def inner(fn):
        @handle_error
        async def wrapper(*args, **kwargs):
            try:
                result = await fn(*args, **kwargs)
                return result
            except Exception:
                to_save = args[1].dict()
                if datatype and datatype != 'bulk':
                    to_save = {datatype: to_save}
                # print(to_save)
                raise StorageError('Failed Save in Storage',
                                   data=to_save,
                                   storage_name=args[0].name,
                                   storage_type=get_full_class_name(args[0]),
                                   storage_function=fn.__name__)

        return wrapper

    return inner
