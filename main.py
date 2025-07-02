from aiogram import Bot, Dispatcher
from aiogram.filters import Command, StateFilter
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message
from config import Config, load_config
import logging
from logging import StreamHandler, Formatter
import sys
import datetime
import keyboards
import body
import databases as db


config: Config = load_config('bot.env')
BOT_TOKEN: str = config.tg_bot.token
bot = Bot(BOT_TOKEN)
dp = Dispatcher()
logger = body.logger


class FSMFillForm(StatesGroup):
    history = State()
    group_management = State()
    group_config = State()
    add_group_user = State()
    add_group_name = State()
    name_await = State()
    pay_suggestion = State()
    add_item_name = State()
    add_item_price = State()
    add_item_group = State()
    add_item_payer = State()
    add_item_other = State()
    add_item_confirm = State()


@dp.message(Command(commands='init'))
async def process_load_command(message: Message, state: FSMContext):
    await db.init_dbs()
    logger.debug('Db initialized')


@dp.message(Command(commands=['menu', 'start']))
async def process_menu_command(message: Message, state: FSMContext):
    await body.check_user_db(message)
    logger.debug('entered menu state')


    await message.answer(
        text='Меню',
        reply_markup=keyboards.main_menu_kb
    )
    await state.set_state(default_state)


@dp.message(Command(commands='group_management'), StateFilter(default_state))
async def process_group_management_command(message: Message, state: FSMContext):
    await body.check_user_db(message)
    logger.debug('entered group management state')


    res_text = await body.get_groups_srt(message.from_user.id)
    group_names = list((await db.get_groups_id_name(message.from_user.id)).keys())
    group_names.append('/create_group')
    await message.answer(
        text=res_text,
        reply_markup=keyboards.get_kb(group_names)
    )
    logger.info(f"Getting group list of {message.from_user.id}")
    await state.set_state(FSMFillForm.group_management)


@dp.message(Command(commands='create_group'), StateFilter(FSMFillForm.group_management))
async def process_create_group_command(message: Message, state: FSMContext):
    await message.answer(
        text='Введите название новой группы',
        reply_markup=keyboards.txt_input_kb
    )
    logger.debug('entered create_group state')
    await state.set_state(FSMFillForm.add_group_name)


@dp.message(StateFilter(FSMFillForm.add_group_name))
async def process_configurate_group_command(message: Message, state: FSMContext):
    if await db.add_group(message.from_user.id, message.text):
        await message.answer(
            text='Группа создана',
            reply_markup=keyboards.main_menu_kb
        )
        logger.debug(f'group {message.text} created')
        await state.set_state(default_state)
    else:
        await message.answer(
            text='Неверное имя группы',
            reply_markup=keyboards.txt_input_kb
        )
        logger.warning(f'wrong group name')
        await state.set_state(FSMFillForm.add_group_name)


@dp.message(StateFilter(FSMFillForm.group_management))
async def process_configurate_group_command(message: Message, state: FSMContext):
    group_names = list((await db.get_groups_id_name(message.from_user.id)).keys())
    if message.text in group_names:
        group_info = await body.get_group_info(message.from_user.id, message.text)
        await state.update_data(group_name=message.text)
        await message.answer(
            text=group_info,
            reply_markup=keyboards.group_config_kb
        )
        logger.debug('entered configurate_group state')
        await state.set_state(FSMFillForm.group_config)
    else:
        tmp = group_names.copy()
        tmp.append('/create_group')
        await message.answer(
            text="Группа не из списка\n" + group_names,
            reply_markup=keyboards.get_kb(tmp)
        )
        logger.info(f"Getting group list of {message.from_user.id}")
        await state.set_state(FSMFillForm.group_management)


@dp.message(Command(commands='add_user'), StateFilter(FSMFillForm.group_config))
async def process_group_user_adding_command(message: Message, state: FSMContext):
    await message.answer(
        text='Введите tg username имя (без @) нового пользователя группы',
        reply_markup=keyboards.txt_input_kb
    )
    logger.debug('entered create_group state')
    await state.set_state(FSMFillForm.add_group_user)


@dp.message(StateFilter(FSMFillForm.add_group_user))
async def process_add_group_user_command(message: Message, state: FSMContext):
    user_local_id = await db.find_user_by_username(message.text)
    logger.debug('entered add_group_user state')
    if user_local_id != 0:
        tmp = await state.get_data()
        group_name = tmp['group_name']
        await db.connect_user_to_group(message.from_user.id, group_name, user_local_id)
        await message.answer(
            text=f'Пользователь {message.text} добавлен',
            reply_markup=keyboards.main_menu_kb
        )
        await state.set_state(default_state)
    else:
        await message.answer(
            text='Неверное имя пользователя или его не в системе бота',
            reply_markup=keyboards.txt_input_kb
        )
        logger.warning('wrong user name')
        await state.set_state(FSMFillForm.add_group_user)


@dp.message(Command(commands='history'), StateFilter(default_state, FSMFillForm.history))
async def process_history_command(message: Message, state: FSMContext):
    await body.check_user_db(message)
    logger.debug('entered history state')


    if await state.get_state() == 'FSMFillForm:history':
        tmp = await state.get_data()
        history_state = tmp['history_state']
    else:
        history_state = 0
    res_text, history_state = await body.get_history_srt(message.from_user.id, history_state)
    await state.update_data(history_state=history_state)
    if res_text == '':
        res_text = 'Нет истории'
        logger.warning('empty history')
    await message.answer(
        text=res_text,
        reply_markup=keyboards.history_kb
    )
    logger.info(f'getting history of {message.from_user.id}')
    await state.set_state(FSMFillForm.history)


@dp.message(Command(commands='personal_bill'), StateFilter(default_state))
async def process_personal_bill_command(message: Message, state: FSMContext):
    await body.check_user_db(message)
    logger.debug('entered personal bill state')


    res_text = await body.get_bill_str(message.from_user.id)
    logger.info((f'getting personal bill'))
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


@dp.message(Command(commands=['pay', 'menu']), StateFilter(FSMFillForm.pay_suggestion))
async def process_billing_command(message: Message, state: FSMContext):
    if message.text == '/pay':
        await body.payment(message.from_user.id)
        logger.info(str(message.from_user.id) + ' payed')
        await message.answer(
            text='Оплачено\nМеню',
            reply_markup=keyboards.main_menu_kb
        )
    else:
        await message.answer(
            text='Меню',
            reply_markup=keyboards.main_menu_kb
        )
    await state.set_state(default_state)



@dp.message(Command(commands='add_item'), StateFilter(default_state))
async def process_add_command(message: Message, state: FSMContext):
    await message.answer(
        text='Введите название покупки',
        reply_markup=keyboards.txt_input_kb
    )
    logger.debug('entered add_item_name state')
    await state.set_state(FSMFillForm.add_item_name)


@dp.message(StateFilter(FSMFillForm.add_item_name))
async def process_name_command(message: Message, state: FSMContext):
    await body.check_user_db(message)
    logger.debug('entered add_item_name state')


    await state.update_data(name=message.text)
    await message.answer(
        text='Введите цену покупки',
        reply_markup=keyboards.txt_input_kb
    )
    logger.debug('entered add_item_price state')
    await state.set_state(FSMFillForm.add_item_price)


@dp.message(StateFilter(FSMFillForm.add_item_price))
async def process_price_command(message: Message, state: FSMContext):
    if message.text.isdigit():
        if int(message.text) > 0:
            await state.update_data(price=int(message.text))
            group_list = await db.get_groups_id_name(message.from_user.id)
            group_names = list(group_list.keys())
            if len(group_list) > 1:
                await message.answer(
                    text='Выберите группу',
                    reply_markup=keyboards.get_kb(group_names)
                )
                await state.update_data(payer=[])
                logger.debug('entered add_item_group state')
                await state.set_state(FSMFillForm.add_item_group)
            elif len(group_list) == 1:
                await state.update_data(group=group_list[0][0])
                payer_list = await db.get_users_from_group(group_list[0][0])
                await message.answer(
                    text='Введите платильщиков по покупке',
                    reply_markup=keyboards.get_kb(payer_list)
                )
                await state.update_data(payer=[])
                logger.debug('entered add_item_payer state')
                await state.set_state(FSMFillForm.add_item_payer)
            else:
                await message.answer(
                    text='Нет доступных групп',
                    reply_markup=keyboards.main_menu_kb
                )
                logger.warning('no possible groups')
                await state.set_state(default_state)
        else:
            await message.answer(
                text='Введите цену покупки',
                reply_markup=keyboards.txt_input_kb
            )
            logger.warning('wrong_item_price')
    else:
        await message.answer(
            text='Введите цену покупки',
            reply_markup=keyboards.txt_input_kb
        )
        logger.warningawait ('wrong item price')


@dp.message(StateFilter(FSMFillForm.add_item_group))
async def process_add_item_group_command(message: Message, state: FSMContext):
    group_dict = await db.get_groups_id_name(message.from_user.id)
    if message.text in group_dict:
        await state.update_data(group=group_dict[message.text])
        payers_list = await db.get_users_from_group(group_dict[message.text])
        await message.answer(
            text='Введите платильщиков по покупке',
            reply_markup=keyboards.get_kb(payers_list)
        )
        await state.update_data(payer=[])
        logger.debug('entered add_item_payer state')
        await state.set_state(FSMFillForm.add_item_payer)
    else:
        await message.answer(
            text='Выберите группу',
            reply_markup=keyboards.get_kb(list(group_dict.keys()))
        )
        logger.warning('wrong group name')
        await state.set_state(FSMFillForm.add_item_group)


@dp.message(Command(commands='end'), StateFilter(FSMFillForm.add_item_payer))
async def process_payer_alt_command(message: Message, state: FSMContext):
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
    tmp = await state.get_data()
    group_id = tmp['group']
    payer_added = tmp['payer']
    db_list = await db.get_users_from_group(group_id)
    payer_list = list(set(db_list) - set(payer_added))


    if message.text in payer_list:
        lst = (await state.get_data())['payer']
        lst.append(message.text)
        await state.update_data(payer=lst)


        tmp = await state.get_data()
        payer_added = tmp['payer']
        payer_list = list(set(db_list) - set(payer_added))
        if len(payer_list) == 0:
            await message.answer(
                text='Подтвердите информацию по покупке\n' + str((await state.get_data())['name']) + ' ' + str((await state.get_data())['price']) + 'р ' + str((await state.get_data())['payer']),
                reply_markup=keyboards.ok_kb
            )
            logger.debug('entered add_item_confirm state')
            await state.set_state(FSMFillForm.add_item_confirm)
        else:
            await message.answer(
                text='Введите платильщиков по покупке',
                reply_markup=keyboards.get_kb(payer_list)
            )
    else:
        await message.answer(
            text='Неверный платильщик',
            reply_markup=keyboards.get_kb(payer_list)
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
    await body.add_data(await state.get_data(), message.from_user.id)
    await message.answer(
        text='Успешно добавлено',
        reply_markup=keyboards.main_menu_kb
    )
    logger.info('added new item')
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
