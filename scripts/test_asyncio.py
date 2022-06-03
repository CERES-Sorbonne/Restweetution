import asyncio

from restweetution.models.bulk_data import BulkData


async def cancel_me():
    print('cancel_me(): before sleep')

    # Wait for 1 hour
    await asyncio.sleep(3600)


async def main():
    # Create a "cancel_me" Task
    task = asyncio.create_task(cancel_me())

    # Wait for 1 second
    await asyncio.sleep(1)

    # task.cancel()
    # await task
    print("main(): cancel_me is cancelled now")


asyncio.run(main())

# a = BulkData()
# b = BulkData()
#
# a.rules = [{'tag': 'a', 'id': '1'}]
# b.rules = [{'tag': 'b', 'id': '2'}]
#
# c = a+b
# c = c + c
# print(c.rules)
