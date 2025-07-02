import datetime
import string
import aiosqlite


async def init_dbs():
    async with aiosqlite.connect("tg_bot_db") as db:

        exe_str = f"CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, tg_id INTEGER, name TEXT, tg_name TEXT)"
        await db.execute(exe_str)
        await db.commit()

        exe_str = f"CREATE TABLE IF NOT EXISTS groups (id INTEGER PRIMARY KEY, name TEXT)"
        await db.execute(exe_str)
        await db.commit()

        exe_str = f"CREATE TABLE IF NOT EXISTS purchase (id INTEGER PRIMARY KEY, purchase_name TEXT, cost INTEGER, buyer TEXT, created_at datetime, note TEXT, group_id INTEGER NOT NULL, FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE)"
        await db.execute(exe_str)
        await db.commit()

        exe_str = f"CREATE TABLE IF NOT EXISTS purchase_users (purchase_id INTEGER NOT NULL, user_id INTEGER NOT NULL, status BOOL, PRIMARY KEY (purchase_id, user_id), FOREIGN KEY (purchase_id) REFERENCES purchase(id) ON DELETE CASCADE, FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE)"
        await db.execute(exe_str)
        await db.commit()

        exe_str = f"CREATE TABLE IF NOT EXISTS users_group (user_id INTEGER NOT NULL, group_id INTEGER NOT NULL, PRIMARY KEY (user_id, group_id), FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE, FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE)"
        await db.execute(exe_str)
        await db.commit()


async def add_user(
        tg_id : int,
        name : str,
        username : str):
    async with aiosqlite.connect("tg_bot_db") as db:
        exe_str = f"INSERT INTO users (tg_id, name, tg_name) VALUES ({tg_id}, '{name}', '{username}')"
        await db.execute(exe_str)
        await db.commit()


async def add_group(
        tg_id : int,
        name : str) -> bool:
    async with aiosqlite.connect("tg_bot_db") as db:
        exe_str = f"SELECT name From users WHERE (name = '{name}') and (id in (SELECT group_id FROM users_group WHERE user_id = (SELECT id from users WHERE tg_id = {tg_id})))"
        cursor = await db.execute(exe_str)
        group_name = await cursor.fetchall()
        if len(group_name) != 0:
            return False

        exe_str = f"INSERT INTO groups (name) VALUES ('{name}')"
        cursor = await db.execute(exe_str)
        _id = cursor.lastrowid
        exe_str = f"INSERT INTO users_group (user_id, group_id) VALUES ((select id from users where tg_id = {tg_id}), {_id})"
        await db.execute(exe_str)
        await db.commit()
        return True


async def get_group_id(
        tg_id : int,
        name : str) -> int:
    async with aiosqlite.connect("tg_bot_db") as db:
        exe_str = f"select id from groups where name = '{name}' and id in (SELECT group_id FROM users_group WHERE user_id = (select id from users where tg_id = {tg_id}))"
        async with db.execute(exe_str) as cursor:
            _id = await cursor.fetchall()
            if len(_id) == 0:
                return 0
            return _id[0][0]


async def get_users_from_group(
        group_id : int) -> list:
    async with aiosqlite.connect("tg_bot_db") as db:
        exe_str = f"SELECT name FROM users WHERE id in (SELECT user_id FROM users_group WHERE group_id = {group_id})"
        async with db.execute(exe_str) as cursor:
            users = await cursor.fetchall()
            return [i[0] for i in users]


async def find_user_by_username(
        username : str) -> int:
    async with aiosqlite.connect("tg_bot_db") as db:
        exe_str = f"SELECT id FROM users WHERE tg_name = '{username}'"
        async with db.execute(exe_str) as cursor:
            _id = await cursor.fetchall()
            return _id[0][0]


async def connect_user_to_group(
        owner_id : int,
        group_name: str,
        local_id : int) -> bool:
    async with aiosqlite.connect("tg_bot_db") as db:
        exe_str = f"select id from groups where (id in (select group_id from users_group where user_id = (select id from users where tg_id = {owner_id}))) and (name = '{group_name}')"
        cursor = await db.execute(exe_str)
        group_id = await cursor.fetchall()

        exe_str = f"SELECT tg_id from users WHERE id = (SELECT user_id from users_group where group_id = {group_id[0][0]} LIMIT 1)"
        cursor = await db.execute(exe_str)
        _id = await cursor.fetchall()
        if _id[0][0] != owner_id:
            return False


        exe_str = f"INSERT INTO users_group VALUES ({local_id}, {group_id[0][0]})"
        await db.execute(exe_str)
        await db.commit()
        return True


async def find_user(
        tg_id : int) -> bool:
    async with aiosqlite.connect("tg_bot_db") as db:
        exe_str = f"SELECT tg_id FROM users WHERE tg_id = {tg_id}"
        async with db.execute(exe_str) as cursor:
            _id = await cursor.fetchall()
            if len(_id) == 0:
                return False
            else:
                return True


async def get_userdata_by_tg_id(
        tg_id : int) -> list:
    async with aiosqlite.connect("tg_bot_db") as db:
        exe_str = f"SELECT id, tg_id, name, tg_name FROM users WHERE tg_id = {tg_id}"
        async with db.execute(exe_str) as cursor:
            data = await cursor.fetchall()
            return data[0]



async def find_users_in_group_by_name(
        names : list,
        group_id : int) -> list:
    async with aiosqlite.connect("tg_bot_db") as db:
        exe_str = f"SELECT tg_id, name FROM users WHERE id in (SELECT user_id from users_group where group_id = {group_id})"
        async with db.execute(exe_str) as cursor:
            tmp = await cursor.fetchall()
            _dict = {i[1] : i[0] for i in tmp}
            res = [_dict[i] for i in names]
            return res


async def get_groups_id_name(
        tg_id : int) -> dict:
    async with aiosqlite.connect("tg_bot_db") as db:
        exe_str = f"SELECT id, name FROM groups WHERE id in (SELECT group_id FROM users_group WHERE user_id = (select id from users where tg_id = {tg_id}))"
        async with db.execute(exe_str) as cursor:
            groups = await cursor.fetchall()
            return {i[1] : i[0] for i in groups}


async def add_purchase(
        purchase_name : string,
        cost : int,
        payers : list,
        buyer : int,
        group_id : int,
        note : str = ""):
    async with aiosqlite.connect("tg_bot_db") as db:

        exe_str = f"INSERT INTO purchase (purchase_name, cost, buyer, created_at, note, group_id) VALUES ('{purchase_name}', {cost}, {buyer}, '{datetime.datetime.now()}', '{note}', {group_id})"
        cursor = await db.execute(exe_str)
        _id = cursor.lastrowid

        for payer in payers:
            exe_str = f"SELECT id FROM users WHERE tg_id = {payer}"
            cursor = await db.execute(exe_str)
            local_id = await cursor.fetchall()

            exe_str = f"INSERT INTO purchase_users (purchase_id, user_id, status) VALUES ({_id}, {local_id[0][0]}, FALSE)"
            await db.execute(exe_str)
            await db.commit()


async def make_payment(user_id :int):
    async with aiosqlite.connect("tg_bot_db") as db:
        exe_str = f"update purchase_users set status = TRUE where user_id = {user_id}"
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


async def get_bill(payer: int, group_id: int) -> list:
    async with aiosqlite.connect("tg_bot_db") as db:
        exe_str = f"SELECT sum(cost), buyer FROM purchase WHERE (group_id = '{group_id}') AND (id in (select purchase_id from purchase_users where (status = FALSE) and (user_id = (select id from users where tg_id = {payer})))) group by buyer"
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