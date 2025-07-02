from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_kb(data : list, menu_button : bool = True) -> ReplyKeyboardMarkup:
    tmp_list = [[KeyboardButton(text=f'{i}')] for i in data]
    if menu_button:
        tmp_list.append([KeyboardButton(text='/menu')])
    res_kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=tmp_list)
    return res_kb


main_menu_kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard = [
    #[KeyboardButton(text='/history')],
    [KeyboardButton(text='/personal_bill')],
    [KeyboardButton(text='/group_management')],
    [KeyboardButton(text='/add_item')],
])

txt_input_kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard = [
    [KeyboardButton(text='/menu')],
])

history_kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard = [
    [KeyboardButton(text='/menu')],
    [KeyboardButton(text='/history')],
])

group_config_kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard = [
    [KeyboardButton(text='/menu')],
    [KeyboardButton(text='/add_user')],
])

pay_suggestion_kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard = [
    [KeyboardButton(text='/menu')],
    [KeyboardButton(text='/pay')],
])

add_other_kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard = [
    [KeyboardButton(text='/end')],
    [KeyboardButton(text='/menu')],
])

ok_kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard = [
    [KeyboardButton(text='/ok')],
    [KeyboardButton(text='/cancel')],
    [KeyboardButton(text='/add_note')],
])