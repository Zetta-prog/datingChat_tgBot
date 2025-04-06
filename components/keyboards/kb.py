from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

start_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Найти собеседника 🔎', callback_data='start_dialogue')],
    [InlineKeyboardButton(text='Моя анкета 👀', callback_data='my_form'),
        InlineKeyboardButton(text='Фильтры', callback_data='filters')]
])

gender_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Мужской', callback_data='gender_man'),
        InlineKeyboardButton(text='Женский', callback_data='gender_woman')],
    [InlineKeyboardButton(text='Назад 🔙', callback_data='back')]
])

back_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Назад 🔙', callback_data='back')]
])

edit_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Возраст', callback_data='edit_age'),
        InlineKeyboardButton(text='Пол', callback_data='edit_gender'),
        InlineKeyboardButton(text='Имя', callback_data='edit_name')],
    [InlineKeyboardButton(text='Назад 🔙', callback_data='back')]
])

add_form = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Создать анкету ✔️', callback_data='add_form')],
    [InlineKeyboardButton(text='Назад 🔙', callback_data='back')]
])

edit_gender = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Мужской', callback_data='edit_gender_man'),
        InlineKeyboardButton(text='Женский', callback_data='edit_gender_woman')],
    [InlineKeyboardButton(text='Назад 🔙', callback_data='back')]
])

finish_search = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Отменить ❌', callback_data='finish_search')]
])

filters_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Сбросить ❌', callback_data='filter_reset')],
    [InlineKeyboardButton(text='Мужской', callback_data='filter_man'),
        InlineKeyboardButton(text='Женский', callback_data='filter_woman')],
    [InlineKeyboardButton(text='Назад 🔙', callback_data='back')]
])

back_new_message_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Назад 🔙', callback_data='back_new_message')]
])

def rating(to_user_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='👍', callback_data=f'like_user_{to_user_id}'),
            InlineKeyboardButton(text='👎', callback_data=f'dislike_user_{to_user_id}')]
    ])