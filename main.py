from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery, Message
from config import Config, load_config
import logging
from logging import StreamHandler, Formatter
import sys
import datetime
import keyboards
import body


config: Config = load_config('bot.env')
BOT_TOKEN: str = config.tg_bot.token

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

logging.basicConfig(filename='logs.txt', filemode='a', level=logging.INFO)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = StreamHandler(stream=sys.stdout)
handler.setFormatter(Formatter(fmt='[%(asctime)s: %(levelname)s] %(message)s'))
logger.addHandler(handler)

# id, datetime, name, buyer, payers, price, status, other
user_dict: dict[int, dict[str, str or int or list or datetime]] = {}
users_db: dict[int, str] = {}

class FSMFillForm(StatesGroup):
    history = State()
    name_await = State()
    pay_suggestion = State()
    add_item_name = State()
    add_item_price = State()
    add_item_payer = State()
    add_item_other = State()
    add_item_confirm = State()


@dp.message(Command(commands='save_data_159260'))
async def process_save_command(message: Message):
    with open("data.csv", 'w', encoding="utf-8") as f:
        for i in user_dict:
            ans = str(i) + ';'
            for j in user_dict[i]:
                if j == 'history_state':
                    continue
                ans += str(user_dict[i][j]) + ';'
            print(ans)
            f.write(ans + '\n')


@dp.message(Command(commands='load_data_159260'))
async def process_load_command(message: Message, state: FSMContext):
    with open("data.csv", 'r', encoding="utf-8") as f:
        text = f.readline()[:-1]
        while text != '':
            arr = text.split(';')
            user_dict[int(arr[0])] = {}
            user_dict[int(arr[0])]['name'] = arr[1]
            user_dict[int(arr[0])]['price'] = int(arr[2])
            user_dict[int(arr[0])]['payer'] = arr[3][2:-2].split("', '")
            user_dict[int(arr[0])]['buyer'] = str(arr[4])
            user_dict[int(arr[0])]['datetime'] = datetime.datetime.strptime(arr[5], '%Y-%m-%d').date()
            #user_dict[int(arr[0])]['datetime'] = datetime.datetime.strptime(arr[5], '%d.%m.%Y').date()
            tmp_arr = list()
            for j in arr[6][1:-1].split(', '):
                if j == '':
                    break
                tmp_arr.append(int(j))
            user_dict[int(arr[0])]['status'] = tmp_arr
            text = f.readline()[:-1]


@dp.message(Command(commands='menu'))
async def process_menu_command(message: Message, state: FSMContext):
    if (message.from_user.id in users_db):
        logger.debug('user_bd_check successful')
        await message.answer(
            text='Меню',
            reply_markup=keyboards.main_menu_kb
        )
        logger.debug('entered menu state')
        await state.set_state(default_state)
    else:
        logger.warning('user_bd_check failed')
        await message.answer(text='Введите свой псевдоним')
        await state.set_state(FSMFillForm.name_await)


@dp.message(Command(commands='start'))
async def process_start_command(message: Message, state: FSMContext):
    if (message.from_user.id in users_db):
        logger.debug('user_bd_check successful')
        await message.answer(
            text='Меню',
            reply_markup=keyboards.main_menu_kb
        )
        logger.debug('entered menu state')
        await state.set_state(default_state)
    else:
        logger.warning('user_bd_check failed')
        await message.answer(text='Введите свой псевдоним')
        await state.set_state(FSMFillForm.name_await)


@dp.message(StateFilter(FSMFillForm.name_await))
async def process_payer_command(message: Message, state: FSMContext):
    if True:
        users_db[message.from_user.id] = message.text
        await message.answer(
            text='ОК',
            reply_markup=keyboards.main_menu_kb
        )
        logger.info('nickname added ' + message.text)
        logger.debug('entered menu state')
        await state.set_state(default_state)
    else:
        await message.answer(
            text='Неправильный псевдоним'
        )
        logger.warning('wrong nickname')
        await state.set_state(FSMFillForm.name_await)


@dp.message(Command(commands='history'), StateFilter(default_state, FSMFillForm.history))
async def process_history_command(message: Message, state: FSMContext):
    if (message.from_user.id in users_db):
        logger.debug('user_bd_check successful')
        if await state.get_state() == 'FSMFillForm:history':
            tmp = await state.get_data()
            history_state = tmp['history_state']
        else:
            history_state = 0
        res_text, history_state = body.get_history_srt(history_state, user_dict)
        await state.update_data(history_state=history_state)
        if res_text == '':
            res_text = 'Нет истории'
            logger.warning('empty history')
        await message.answer(
            text=res_text,
            reply_markup=keyboards.history_kb
        )
        logger.info('getting history - ' + users_db[message.from_user.id])
        logger.debug('entered history state')
        await state.set_state(FSMFillForm.history)
    else:
        logger.warning('user_bd_check failed')
        await message.answer(text='Введите свой псевдоним')
        await state.set_state(FSMFillForm.name_await)


@dp.message(Command(commands='personal_bill'), StateFilter(default_state))
async def process_history_command(message: Message, state: FSMContext):
    if (message.from_user.id in users_db):
        logger.debug('user_bd_check successful')
        res_text = body.get_bill_str(users_db[message.from_user.id], user_dict)
        logger.info(('getting personal bill - ' + users_db[message.from_user.id]))
        if res_text == '':
            await message.answer(
                text='Нет долга',
                reply_markup=keyboards.main_menu_kb
            )
            logger.warning('empty bill')
            logger.debug('entered pay menu state')
            await state.set_state(default_state)
        else:
            await message.answer(
                text=res_text,
                reply_markup=keyboards.pay_suggestion_kb
            )
            logger.debug('entered pay suggestion state')
            await state.set_state(FSMFillForm.pay_suggestion)
    else:
        logger.warning('user_bd_check failed')
        await message.answer(text='Введите свой псевдоним')
        await state.set_state(FSMFillForm.name_await)


@dp.message(Command(commands=['pay', 'menu']), StateFilter(FSMFillForm.pay_suggestion))
async def process_history_command(message: Message, state: FSMContext):
    if message.text == '/pay':
        global user_dict
        user_dict = body.payment(user_dict, users_db[message.from_user.id])
        logger.info(users_db[message.from_user.id] + ' payed')
        await message.answer(
            text='Оплачено\nМеню',
            reply_markup=keyboards.main_menu_kb
        )
    else:
        await message.answer(
            text='Меню',
            reply_markup=keyboards.main_menu_kb
        )
    logger.debug('entered pay menu state')
    await state.set_state(default_state)



@dp.message(Command(commands='add_item'), StateFilter(default_state))
async def process_add_command(message: Message, state: FSMContext):
    if (message.from_user.id in users_db):
        logger.debug('user_bd_check successful')
        await message.answer(
            text='Введите название покупки',
            reply_markup=keyboards.add_item_kb
        )
        logger.debug('entered add_item_name state')
        await state.set_state(FSMFillForm.add_item_name)
    else:
        logger.warning('user_bd_check failed')
        await message.answer(text='Введите свой псевдоним')
        await state.set_state(FSMFillForm.name_await)


@dp.message(StateFilter(FSMFillForm.add_item_name))
async def process_name_command(message: Message, state: FSMContext):
    if True:
        await state.update_data(name=message.text)
        await message.answer(
            text='Введите цену покупки',
            reply_markup=keyboards.add_price_kb
        )
        logger.debug('entered add_item_price state')
        await state.set_state(FSMFillForm.add_item_price)
    else:
        await message.answer(
            text='Введите название покупки',
            reply_markup=keyboards.add_item_kb
        )
        logger.warning('wrong item_name')


@dp.message(StateFilter(FSMFillForm.add_item_price))
async def process_price_command(message: Message, state: FSMContext):
    if message.text.isdigit():
        if int(message.text) > 0:
            await state.update_data(price=int(message.text))
            await message.answer(
                text='Введите платильщиков по покупке',
                reply_markup=keyboards.add_payer_kb
            )
            await state.update_data(payer=[])
            logger.debug('entered add_item_payer state')
            await state.set_state(FSMFillForm.add_item_payer)
        else:
            await message.answer(
                text='Введите цену покупки',
                reply_markup=keyboards.add_price_kb
            )
            logger.warning('wrong_item_price')
    else:
        await message.answer(
            text='Введите цену покупки',
            reply_markup=keyboards.add_price_kb
        )
        logger.warning('wrong_item_price')


@dp.message(Command(commands='end'), StateFilter(FSMFillForm.add_item_payer))
async def process_payerAlt_command(message: Message, state: FSMContext):
    lst = (await state.get_data())['payer']
    if len(lst) == 0:
        await message.answer(
            text='Недостаточно платильщиков',
            reply_markup=keyboards.add_payer_kb
        )
    else:
        await message.answer(
            text='Подтвердите информацию по покупке\n' + str((await state.get_data())['name']) + ' ' + str((await state.get_data())['price']) + 'р ' + str((await state.get_data())['payer']),
            reply_markup=keyboards.ok_kb
        )
        logger.debug('entered add_item_confirm state')
        await state.set_state(FSMFillForm.add_item_confirm)


@dp.message(StateFilter(FSMFillForm.add_item_payer))
async def process_payer_command(message: Message, state: FSMContext):
    if message.text.isalnum():
        lst = (await state.get_data())['payer']
        lst.append(message.text)
        await state.update_data(payer=lst)
        await message.answer(
            text='Введите платильщиков по покупке',
            reply_markup=keyboards.add_payer_kb
        )
    else:
        await message.answer(
            text='Введите платильщиков по покупке',
            reply_markup=keyboards.add_payer_kb
        )
        logger.warning('wrong payer')


@dp.message(Command(commands='end'), StateFilter(FSMFillForm.add_item_other))
async def process_otherAlt_command(message: Message, state: FSMContext):
    await message.answer(
        text='Подтвердите информацию по покупке\n' + str((await state.get_data())['name']) + ' ' + str((await state.get_data())['price']) + 'р ' + str((await state.get_data())['payer']),
        reply_markup=keyboards.ok_kb
    )
    logger.debug('entered add_item_confirm state')
    await state.set_state(FSMFillForm.add_item_confirm)


@dp.message(StateFilter(FSMFillForm.add_item_other))
async def process_other_command(message: Message, state: FSMContext):
    if message.text != '':
        await state.update_data(other=message.text)
    await message.answer(
        text='Подтвердите информацию по покупке\n' + str((await state.get_data())['name']) + ' ' + str((await state.get_data())['price']) + 'р ' + str((await state.get_data())['payer']),
        reply_markup=keyboards.ok_kb
    )
    logger.debug('entered add_item_confirm state')
    await state.set_state(FSMFillForm.add_item_confirm)


@dp.message(Command(commands='ok'), StateFilter(FSMFillForm.add_item_confirm))
async def process_ok_command(message: Message, state: FSMContext):
    user_dict[len(user_dict)] = body.compact_data(await state.get_data(), users_db[message.from_user.id], message.date.date())
    await message.answer(
        text='Меню',
        reply_markup=keyboards.main_menu_kb
    )
    logger.info('added item with number ' + str(len(user_dict)))
    logger.debug('entered menu state')
    await state.clear()


@dp.message(Command(commands='cancel'), StateFilter(FSMFillForm.add_item_confirm))
async def process_cancel_command(message: Message, state: FSMContext):
    await message.answer(
        text='Меню',
        reply_markup=keyboards.main_menu_kb
    )
    logger.debug('entered menu state')
    await state.clear()


@dp.message(Command(commands='add_note'), StateFilter(FSMFillForm.add_item_confirm))
async def process_confirm2other_command(message: Message, state: FSMContext):
    await message.answer(
        text='Введите заметку к покупке',
        reply_markup=keyboards.add_other_kb
    )
    logger.debug('entered add_item_other state')
    await state.set_state(FSMFillForm.add_item_other)


@dp.message()
async def process_unexpected_command(message: Message):
    logger.warning('unexpected command')
    await message.answer(text='unexpected command')

if __name__ == '__main__':
    dp.run_polling(bot)
