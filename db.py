import datetime
import string

import aiosqlite

async def init_db():
    async with aiosqlite.connect("tg_bot_db") as db:
        exe_str = f"CREATE TABLE IF NOT EXISTS purchase (id INTEGER PRIMARY KEY, purchase_name TEXT, cost INTEGER, payer TEXT, buyer TEXT, created_at datetime, status TEXT, note TEXT)"
        await db.execute(exe_str)
        await db.commit()

async def add_purchase(
        purchase_name : string,
        cost : int,
        payer : string,
        buyer : string,
        status : str,
        note : str = ""):
    async with aiosqlite.connect("tg_bot_db") as db:
        exe_str = f"INSERT INTO purchase (purchase_name, cost, payer, buyer, created_at, status, note) VALUES ('{purchase_name}', {cost}, '{payer}', '{buyer}', '{datetime.datetime.now()}', '{status}', '{note}')"
        await db.execute(exe_str)
        await db.commit()

async def make_payment(raw : int, new_str: string):
    async with aiosqlite.connect("tg_bot_db") as db:
        exe_str = f"update purchase set status = {new_str} where id = {raw}"
        await db.execute(exe_str)
        await db.commit()


async def get_size():
    async with aiosqlite.connect("tg_bot_db") as db:
        exe_str = f"SELECT COUNT(*) FROM purchase"
        async with db.execute(exe_str) as cursor:
            size = await cursor.fetchall()
            return size[0][0]



async def get_raw(raw: int):
    async with aiosqlite.connect("tg_bot_db") as db:
        exe_str = f"SELECT * FROM purchase WHERE id = {raw}"
        async with db.execute(exe_str) as cursor:
            data = await cursor.fetchall()
            return data[0]



async def get_bill(payer: string):
    async with aiosqlite.connect("tg_bot_db") as db:
        exe_str = f"SELECT * FROM purchase WHERE (payer like '%{payer}%') AND (status like '%0%')"
        async with db.execute(exe_str) as cursor:
            data = await cursor.fetchall()
            return data



async def get_purchases():
    async with aiosqlite.connect("tg_bot_db") as db:
        res = []
        exe_str = f"SELECT * FROM purchase"
        async with db.execute(exe_str) as cursor:
            rows = await cursor.fetchall()
            for row in rows:
                res.append(row)
        return res