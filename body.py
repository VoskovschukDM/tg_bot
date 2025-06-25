import datetime


def get_history_srt(history_state: int, user_dict: dict) -> (str, int):
    res_text = ''
    if len(user_dict) == 0:
        return (res_text, history_state)
    for i in range(10 * history_state, min(10 * (history_state + 1), len(user_dict))):
        tmp = user_dict[i]
        tmp_list = tmp['payer'].copy()
        for j in range(len(tmp['payer'])):
            if tmp['payer'][j] == tmp['buyer'] or tmp['status'][j] == 1:
                tmp_list.remove(tmp['payer'][j])
        res_text += (tmp['name'] + ' - ' + str(tmp['price']) + 'руб. - платят: ' + ', '.join(
            tmp['payer']) + ' - нужно оплатить: ' + ', '.join(
            tmp_list) + ' - кому: ' + tmp['buyer'] + '\n')
    res_text += ('С ' + str(10 * history_state + 1) + ' по ' + str(
        min(10 * (history_state + 1), len(user_dict))) + ' записи из ' + str(len(user_dict)) + '\n')
    if (history_state + 1) * 10 < len(user_dict):
        history_state = history_state + 1
    else:
        history_state = 0
    return (res_text, history_state)


def get_bill_str(name: str, user_dict: dict) -> str:
    bill = []
    for i in user_dict:
        if name in user_dict[i]['payer'] and name != user_dict[i]['buyer'] and user_dict[i]['status'][user_dict[i]['payer'].index(name)] == 0:
            bill.append((user_dict[i]['price'] / len(user_dict[i]['payer']), user_dict[i]['buyer']))
    tmp_dict: dict[str, int] = {}
    for i in bill:
        if i[1] in tmp_dict:
            tmp_dict[i[1]] += i[0]
        else:
            tmp_dict[i[1]] = i[0]
    res_text = ''
    for i in tmp_dict:
        res_text += 'Долг перед ' + i + ' составляет ' + str(int(tmp_dict[i])) + '\n'
    return res_text


def compact_data(data: dict, buyer: str, date: datetime.date) -> dict:
    tmp = data
    tmp['buyer'] = buyer
    tmp['datetime'] = date
    tmp['status'] = [0] * len(tmp['payer'])
    return tmp


def payment(user_dict: dict, name: str) -> dict:
    for i in user_dict:
        if name in user_dict[i]['payer']:
            tmp = user_dict[i]
            tmp['status'][tmp['payer'].index(name)] = 1
            user_dict[i] = tmp
    return user_dict
