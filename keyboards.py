from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

main_menu_kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard = [
    [KeyboardButton(text='/history')],
    [KeyboardButton(text='/personal_bill')],
    [KeyboardButton(text='/add_item')],
])

history_kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard = [
    [KeyboardButton(text='/menu')],
    [KeyboardButton(text='/history')],
])

pay_suggestion_kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard = [
    [KeyboardButton(text='/menu')],
    [KeyboardButton(text='/pay')],
])

add_item_kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard = [
    [KeyboardButton(text='/menu')],
])

add_price_kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard = [
    [KeyboardButton(text='/menu')],
])

add_payer_kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard = [
    [KeyboardButton(text='/end')],
    [KeyboardButton(text='/menu')],
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