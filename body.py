import datetime
import db


async def get_history_srt(history_state: int) -> (str, int):
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


async def get_bill_str(name: str):
    bill = await db.get_bill(name)
    tmp_dict: dict[str, int] = {}
    for i in range(len(bill) - 1, -1, -1):
        raw = bill[i]
        tmp = [item for m, item in zip(raw[3].split(", "), [int(x) for x in raw[6].split(", ")]) if (m == 'pay')]
        if tmp[0] == 0:
            if raw[4] in tmp_dict:
                tmp_dict[raw[4]] += raw[2]
            else:
                tmp_dict[raw[4]] = raw[2]
        else:
            bill.pop(i)
    res_text = ''
    for i in tmp_dict:
        res_text += 'Долг перед ' + i + ' составляет ' + str(int(tmp_dict[i])) + '\n'
    return res_text, bill


async def add_data(data: dict, buyer: str):
    await db.add_purchase(data['name'], data['price'], ", ".join(data['payer']), buyer, ", ".join(['0'] * len(data['payer'])))


async def payment(bill, name: str):
    for raw in bill:
        tmp = [str(val) if (m != name) else "1" for m, val in zip(raw[3].split(", "), [int(x) for x in raw[6].split(", ")])]
        await db.make_payment(raw[0], f"\'{", ".join(tmp)}\'")

        if tmp[0] == 0:
            if raw[4] in tmp_dict:
                tmp_dict[raw[4]] += raw[2]
            else:
                tmp_dict[raw[4]] = raw[2]