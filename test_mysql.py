from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_scoped_session
from urllib.parse import quote
from sqlalchemy.engine import create_engine
import pymysql
import aiomysql
import sqlalchemy as sa
# from aiomysql.sa import create_engine
import os
import asyncio
from time import time

# password = quote('ehfvkfdl123@')
password = 'ehfvkfdl123@'
# engine = create_engine(
#     f'mysql+pymysql://root:{password}@localhost:3306/KOR_DB')

# conn = engine.connect()


conn = pymysql.connect(
    host=os.environ.get('MYSQL_HOST'),
    port=3306,
    db='KOR_DB',
    user='root',
    passwd=password,
    autocommit=True
)


cur = conn.cursor()
code = '005930'
start_date = '2022-01-01'
start_date = '1995-05-01'
end_date = '2022-03-31'
sql = f"SELECT * FROM daily_price WHERE date >= '{start_date}' and date <= '{end_date}' LIMIT 1000000"

ts1 = time()
with conn.cursor() as cur:
    cur.execute(sql)
    result = cur.fetchall()
ts2 = time()

print(result)
print(f"elapsed time: {ts2 - ts1}sec")


# engine = create_async_engine(
#     "mysql+aiomysql://root:{password}@localhost:3306/KOR_DB", encoding='utf-8', echo=True)

# metadata = sa.MetaData()
# tbl = sa.Table(
#     'daily_price',
#     metadata,
#     sa.Column('code', sa.String(255), primary_key=True)
# )


# async def async_main():

#     async with engine.connect() as conn:

#         print("??")
#         # query = tbl.select()
#         # print(query)
#     #     # result = await conn.execute(t1))

# loop = asyncio.get_event_loop()
# loop.run_until_complete(async_main())


# async def get_db_session() -> AsyncSession:
#     sess = AsyncSession(bind=engine)
#     try:
#         yield sess
#     finally:
#         await sess.close()


# async def async_main():

#     async with engine.connect() as conn:
#         result = await conn.execute(select)
#         print(result.fetchall())

# loop.run_until_complete(async_main())


# asyncio.run(async_main())

# import asyncio
# import aiomysql
# import sqlalchemy as sa
# from aiomysql.sa import create_engine
# import os

# metadata = sa.MetaData()
# tbl = sa.Table(
#     'daily_price',
#     metadata,
#     sa.Column('code', sa.String(255), primary_key=True)
#     )

# async def go(loop):
#     engine = await create_engine(
#         host=os.environ.get('MYSQL_HOST'),
#         port=3306,
#         user=os.environ.get('MYSQL_USER'),
#         password=os.environ.get('MYSQL_ROOT_PASSWORD'),
#         db='KOR_DB',
#         loop=loop)


#     async with engine.acquire() as conn:
#         query = tbl.select()
#         res = await conn.execute(query)
#         async for row in res:
#             print(row)
#         # results = await engine.fetch_all(query)

#         print(query)


#     # sql = f"SELECT * FROM daily_price WHERE code = '005930' and date >= '2021-01-01' and date <= '2022-01-01';"

# #         async with conn.cursor() as cur:
# #             await cur.execute(sql)
# #             print(cur.description)
# #             result = await cur.fetchall()
# #             print(result)
# #     pool.close()
# #     await pool.wait_closed()
