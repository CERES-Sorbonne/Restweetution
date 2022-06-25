# import asyncio
# import time
#
# from fastapi import FastAPI
#
# app = FastAPI()
#
#
# @app.get("/")
# async def root():
#     return {"message": "Hello World"}
#
#
# async def loop():
#     while True:
#         print(time.time())
#         await asyncio.sleep(2)
#
# task = asyncio.create_task(loop())
