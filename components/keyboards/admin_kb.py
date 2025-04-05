from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

kb_admin = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Сделать раcсылку', callback_data='mailing')]
])

kb_cancel = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Отмена', callback_data='cancel')]
])