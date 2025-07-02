import datetime
import databases as db
import logging
from logging import StreamHandler, Formatter
import sys


logging.basicConfig(filename='logs.txt', filemode='a', level=logging.DEBUG)
logger = logging.getLogger()
handler = StreamHandler(stream=sys.stdout)
handler.setFormatter(Formatter(fmt='[%(asctime)s: %(levelname)s] %(message)s'))
logger.addHandler(handler)


async def check_user_db(message):
    if await db.find_user(message.from_user.id):
        logger.debug('user_bd_check successful')
    else:
        if message.from_user.first_name:
            name = message.from_user.first_name
        elif message.from_user.last_name:
            name = message.from_user.last_name
        elif message.from_user.username:
            name = message.from_user.username
        else:
            name = "User"
        await db.add_user(message.from_user.id, name, message.from_user.username)
        logger.warning('user is not in db')


async def get_groups_srt(tg_id: int) -> str:
    tmp = await db.get_groups_id_name(tg_id)
    res = list(tmp.keys())
    if len(res) == 0:
        return "Нет групп"
    res_text = ""
    for raw in res:
        res_text += f"Состоит в группе {raw}\n"
    res_text += f"Введите название группы, которую хотите настроить, или создайте новую"
    return res_text


async def get_group_info(tg_id: int, name: str) -> str:
    res_text = f"Группа {name} состоит из:\n"
    group_id = await db.get_group_id(tg_id, name)
    if group_id == 0:
        return ""
    res = await db.get_users_from_group(group_id)
    if len(res) == 0:
        res_text = ''
    for raw in res:
        res_text += f"{raw}\n"
    return res_text


async def get_history_srt(tg_id : int, history_state: int) -> (str, int):
    groups = await db.get_groups_id_name(tg_id)


    db_size = await db.get_size()
    if db_size == 0:
        return "Таблица пуста", history_state
    res_text = ""
    for raw in range(10 * history_state, min(10 * (history_state + 1), db_size)):
        raw_data = await db.get_raw(raw + 1)
        data = {
            'name': raw_data[1],
            'price': raw_data[2],
            'payer': raw_data[3].split("', '"),
            'buyer': raw_data[4],
            'datetime': raw_data[5],
            'status': raw_data[6].split("', '"),
            'note': raw_data[7]}

        res_text += f"{data['name']} - {data['price']}руб. - платят: {", ".join(data['payer'])} - нужно оплатить: {", ".join([item for m, item in zip(data['status'], data['payer']) if m])} - кому: {data['buyer']}\n"
    res_text += ('С ' + str(10 * history_state + 1) + ' по ' + str(min(10 * (history_state + 1), db_size)) + ' записи из ' + str(db_size) + '\n')
    if (history_state + 1) * 10 < db_size:
        history_state = history_state + 1
    else:
        history_state = 0
    return res_text, history_state


async def get_bill_str(payer: int) -> str:
    groups = await db.get_groups_id_name(payer)
    res_text = ''
    for i in groups:
        bill = await db.get_bill(payer, groups[i])
        if len(bill) == 0:
            continue
        res_text += f"В группе {groups[i]}:\n"
        for j in bill:
            #if j[1] == payer or j[0] == 0:
            #    continue
            name = (await db.get_userdata_by_tg_id(j[1]))[2]
            res_text += f"Долг перед {name} составляет {j[0]}\n"
    return res_text


async def add_data(data: dict, buyer: int):
    if 'other' in data:
        await db.add_purchase(
            purchase_name=data['name'],
            cost=data['price'],
            payers=await db.find_users_in_group_by_name(data['payer'], data['group']),
            buyer=buyer,
            group_id=data['group'],
            note=data['other']
        )
    else:
        await db.add_purchase(
            purchase_name=data['name'],
            cost=data['price'],
            payers=await db.find_users_in_group_by_name(data['payer'], data['group']),
            buyer=buyer,
            group_id=data['group']
        )


async def payment(payer : int):
    local_id = (await db.get_userdata_by_tg_id(payer))[0]
    await db.make_payment(local_id)