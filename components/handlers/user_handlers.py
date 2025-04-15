from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ContentType
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey

from random import choice

import components.keyboards.kb as kb
from database.crud import (
    check_user, add_user, add_gender, add_name, add_age, 
    commit_form, set_state_exit, get_companion_id, get_filters,
    add_filter_gender, reset_filter_gender, like_user,
    dislike_user, get_companion
)
from components.states.user_states import Form, Dialogue, EditForm
from components.search_companion import search, search_with_filters
from core.init_bot import bot, dp
from config import OPTIONS, DONATE_URL

user_router = Router()


@user_router.message(CommandStart())
async def start(message: Message):
    await add_user(user_id=message.chat.id)
    filter_gender = await get_filters(user_id=message.from_user.id)
    if filter_gender is None:
        filter_gender = 'не указан'
    else:
        filter_gender = 'мужской' if filter_gender.get('gender') == 'man' else 'женский'
    answer_text = f'<b>👋Добро пожаловать в чат-бота для знакомств! Хочешь найти новых друзей или отлично провести время? Скорее ищи собеседника!\nДля работы используй кнопки или команды:\n\n• /start - Запуск\n• /form - Анкета\n• /search - Поиск \n• /info - Правила \n• /stop - Закончить диалог \n• /donate - Поддержать\n\nНе знаешь, о чём поговорить? Используй команду /help а встроенная нейросеть поможет!\n\nФильтр поиска: {filter_gender}</b>'
    await message.answer(answer_text,
                            reply_markup=kb.start_kb)
    await add_user(user_id=message.from_user.id)

@user_router.callback_query(F.data == 'start_dialogue')
async def start_dialogue(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    current_state = await state.get_state()
    if current_state == 'Dialogue:search' or current_state == 'Dialogue:found':
        await callback.message.answer('<b>Нельзя начать поиск во время поиска собеседника или диалога</b>')
        return
    user = await check_user(user_id=callback.message.chat.id)
    if user and user.ready == True:
        await state.set_state(Dialogue.search)
        searching_message = await callback.message.answer('<b><i>Поиск собеседника 🧍</i></b>',
                                        reply_markup=kb.finish_search)
        filters = await get_filters(user_id=callback.message.chat.id)
        if filters:
            companion = await search_with_filters(user_id=callback.message.chat.id)
            if companion:
                companion_id = await get_companion_id(user_id=callback.message.chat.id)
                companion = await get_companion(companion_id=companion_id)
                companion_gender = 'мужской' if companion.gender == 'man' else 'женский'
                await callback.message.answer(f'<b>Пользователь найден, чтобы закончить диалог нажмите /stop\n\nПол: {companion_gender}\nВозраст: {companion.age}\nИмя: {companion.name}</b>')
                await state.set_state(Dialogue.found)
                await searching_message.delete()
        else:
            companion = await search(user_id=callback.message.chat.id)
            if companion:
                companion_id = await get_companion_id(user_id=callback.message.chat.id)
                companion = await get_companion(companion_id=companion_id)
                companion_gender = 'мужской' if companion.gender == 'man' else 'женский'
                await callback.message.answer(f'<b>Пользователь найден, чтобы закончить диалог нажмите /stop\n\nПол: {companion_gender}\nВозраст: {companion.age}\nИмя: {companion.name}</b>')
                await state.set_state(Dialogue.found)
                await searching_message.delete()
    else:
        await callback.message.answer('<b>Для начала надо создать анкету, выберите свой пол</b>',
                                        reply_markup=kb.gender_kb)

@user_router.message(Command('search'))
async def search_func(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == 'Dialogue:search' or current_state == 'Dialogue:found':
        await message.answer('<b>Нельзя начать поиск во время поиска собеседника или диалога</b>')
        return
    user = await check_user(user_id=message.from_user.id)
    if user and user.ready == True:
        await state.set_state(Dialogue.search)
        searching_message = await message.answer('<b><i>Поиск собеседника 🧍</i></b>',
                                        reply_markup=kb.finish_search)
        filters = await get_filters(user_id=message.from_user.id)
        if filters:
            companion = await search_with_filters(user_id=message.from_user.id)
            if companion:
                companion_id = await get_companion_id(user_id=message.chat.id)
                companion = await get_companion(companion_id=companion_id)
                companion_gender = 'мужской' if companion.gender == 'man' else 'женский'
                await message.answer(f'<b>Пользователь найден, чтобы закончить диалог нажмите /stop\n\nПол: {companion_gender}\nВозраст: {companion.age}\nИмя: {companion.name}</b>')
                await state.set_state(Dialogue.found)
                await searching_message.delete()
        else:
            companion = await search(user_id=message.from_user.id)
            if companion:
                companion_id = await get_companion_id(user_id=message.chat.id)
                companion = await get_companion(companion_id=companion_id)
                companion_gender = 'мужской' if companion.gender == 'man' else 'женский'
                await message.answer(f'<b>Пользователь найден, чтобы закончить диалог нажмите /stop\n\nПол: {companion_gender}\nВозраст: {companion.age}\nИмя: {companion.name}</b>')
                await state.set_state(Dialogue.found)
                await searching_message.delete()
    else:
        await message.answer('<b>Для начала надо создать анкету, выберите свой пол</b>',
                                        reply_markup=kb.gender_kb)

@user_router.callback_query(F.data == 'finish_search')
async def finish_search(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    current_state = await state.get_state()
    if current_state != 'Dialogue:search':
        await callback.message.answer('<b>Поиск не активен</b>')
        return
    filter_gender = await get_filters(user_id=callback.message.chat.id)
    if filter_gender is None:
        filter_gender = 'не указан'
    else:
        filter_gender = 'мужской' if filter_gender.get('gender') == 'man' else 'женский'
    answer_text = f'<b>Для работы с ботом используй кнопки или команды:\n\n• /start - Запуск\n• /form - Анкета\n• /search - Поиск \n• /info - Правила \n• /stop - Закончить диалог \n• /donate - Поддержать\n\nНе знаешь, о чём поговорить? Используй команду /help а встроенная нейросеть поможет!\n\nФильтр поиска: {filter_gender}</b>'

    await callback.message.edit_text(f'<b>Поиск отменен\n\n{answer_text}</b>',
                                    reply_markup=kb.start_kb)
    await set_state_exit(user_id=callback.message.chat.id)
    await state.clear()

@user_router.callback_query(F.data == 'back')
async def back(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    current_state = await state.get_state()
    if current_state != 'Dialogue:search' and current_state != 'Dialogue:found':
        await state.clear()
    filter_gender = await get_filters(user_id=callback.message.chat.id)
    if filter_gender is None:
        filter_gender = 'не указан'
    else:
        filter_gender = 'мужской' if filter_gender.get('gender') == 'man' else 'женский'
    answer_text = f'<b>👋Добро пожаловать в чат-бота для знакомств! Хочешь найти новых друзей или отлично провести время? Скорее ищи собеседника!\nДля работы используй кнопки или команды:\n\n• /start - Запуск\n• /form - Анкета\n• /search - Поиск \n• /info - Правила \n• /stop - Закончить диалог \n• /donate - Поддержать\n\nНе знаешь, о чём поговорить? Используй команду /help а встроенная нейросеть поможет!\n\nФильтр поиска: {filter_gender}</b>'

    await callback.message.edit_text(answer_text,
                                    reply_markup=kb.start_kb)

@user_router.callback_query(F.data == 'back_new_message')
async def back(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    current_state = await state.get_state()
    if current_state != 'Dialogue:search' and current_state != 'Dialogue:found':
        await state.clear()
    filter_gender = await get_filters(user_id=callback.message.chat.id)
    if filter_gender is None:
        filter_gender = 'не указан'
    else:
        filter_gender = 'мужской' if filter_gender.get('gender') == 'man' else 'женский'
    answer_text = f'<b>👋Добро пожаловать в чат-бота для знакомств! Хочешь найти новых друзей или отлично провести время? Скорее ищи собеседника!\nДля работы используй кнопки или команды:\n\n• /start - Запуск\n• /form - Анкета\n• /search - Поиск \n• /info - Правила \n• /stop - Закончить диалог \n• /donate - Поддержать\n\nНе знаешь, о чём поговорить? Используй команду /help а встроенная нейросеть поможет!\n\nФильтр поиска: {filter_gender}</b>'

    await callback.message.answer(answer_text,
                                    reply_markup=kb.start_kb)

'''
ADD FORM
'''
@user_router.callback_query(F.data == 'add_form')
async def add_form(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    current_state = await state.get_state()
    if current_state == 'Dialogue:search' or current_state == 'Dialogue:found':
        await callback.message.answer('<b>Нельзя изменить анкету во время поиска собеседника или диалога</b>')
        return
    data = await check_user(user_id=callback.message.chat.id)
    if not data.name or not data.age or not data.gender:
        await callback.message.answer('<b>Для начала надо создать анкету, выберите свой пол</b>',
                                        reply_markup=kb.gender_kb)
    else:
        await callback.message.answer('<b>Анкета уже создана</b>')

@user_router.callback_query(F.data.startswith('gender_'))
async def gender(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    current_state = await state.get_state()
    if current_state == 'Dialogue:search' or current_state == 'Dialogue:found':
        await callback.message.answer('<b>Нельзя изменить анкету во время поиска собеседника или диалога</b>')
        return
    gender = callback.data[7:]
    await add_gender(user_id=callback.message.chat.id, gender=gender)
    await callback.message.answer('<b>Отлично, напишите свое имя</b>', 
                                    reply_markup=kb.back_kb)
    await state.set_state(Form.name)

@user_router.message(Form.name)
async def name(message: Message, state: FSMContext):
    if message.content_type != ContentType.TEXT:
        await message.answer('<b>Неправильный формат</b>',
                                reply_markup=kb.back_kb)
        return
    if len(message.text) > 30 or '/' in message.text or ':' in message.text or '.' in message.text or '@' in message.text : 
        await message.answer('<b>Ошибка в имени, попробуйте еще раз</b>',
                                reply_markup=kb.back_kb)
    else:
        await add_name(user_id=message.from_user.id, name=message.text)
        await message.answer('<b>Отлично, напишите свой возраст</b>',
                                reply_markup=kb.back_kb)
        await state.set_state(Form.age)

@user_router.message(Form.age)
async def age(message: Message, state: FSMContext):
    if message.content_type != ContentType.TEXT:
        await message.answer('<b>Неправильный формат</b>',
                                reply_markup=kb.back_kb)
        return
    if not message.text.isdigit() or int(message.text) < 1 or int(message.text) > 150:
        await message.answer('<b>Ошибка в возрасте, введите еще раз</b>',
                                reply_markup=kb.back_kb)
    else:
        await add_age(user_id=message.from_user.id, age=int(message.text))
        await message.answer('<b>Отлично анкета готова</b>',
                            reply_markup=kb.start_kb)
        await commit_form(user_id=message.from_user.id)
        await state.clear()
'''
CHECK AND EDIT FORM
'''
@user_router.callback_query(F.data == 'my_form')
async def my_form(callback: CallbackQuery):
    await callback.answer()
    
    user = await check_user(user_id=callback.message.chat.id) 
    if user.name and user.age and user.gender:
        gender = 'мужской' if user.gender == 'man' else 'женский'
        name = user.name.replace('<', '&lt;').replace('>', '&gt;')
        await callback.message.edit_text(f'<b><i>ВАША АНКЕТА</i>\n\nПол: {gender}\nИмя: {name}\nВозраст: {user.age}\n\nЕсли хотите что нибудь изменить выберите ниже</b>',
                                        reply_markup=kb.edit_kb)
    else:
        await callback.message.edit_text('<b>Ваша анкета еще не создана</b>', 
                                        reply_markup=kb.add_form)

@user_router.message(Command('form'))
async def form_func(message: Message):
    user = await check_user(user_id=message.from_user.id) 
    if user.name and user.age and user.gender:
        gender = 'мужской' if user.gender == 'man' else 'женский'
        name = user.name.replace('<', '&lt;').replace('>', '&gt;')
        await message.answer(f'<b><i>ВАША АНКЕТА</i>\n\nПол: {gender}\nИмя: {name}\nВозраст: {user.age}\n\nЕсли хотите что нибудь изменить выберите ниже</b>',
                                        reply_markup=kb.edit_kb)
    else:
        await message.answer('<b>Ваша анкета еще не создана</b>', 
                                        reply_markup=kb.add_form)

@user_router.callback_query(F.data == 'edit_gender')
async def choose_gender(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    current_state = await state.get_state()
    if current_state == 'Dialogue:search' or current_state == 'Dialogue:found':
        await callback.message.answer('<b>Нельзя изменить анкету во время поиска собеседника или диалога</b>')
        return
    await callback.message.answer('<b>Выберите свой пол</b>',
                                    reply_markup=kb.edit_gender)

@user_router.callback_query(F.data.startswith('edit_gender_'))
async def edit_gender(callback: CallbackQuery,state: FSMContext):
    await callback.answer()
    
    current_state = await state.get_state()
    if current_state == 'Dialogue:search' or current_state == 'Dialogue:found':
        await callback.message.answer('<b>Нельзя изменить анкету во время поиска собеседника или диалога</b>')
        return
    gender = callback.data[12:]
    await add_gender(user_id=callback.message.chat.id, gender=gender)
    
    gender = 'мужской' if gender == 'man' else 'женский'
    await callback.message.answer(f'<b>Пол успешно изменен на {gender}</b>',
                                    reply_markup=kb.start_kb)

@user_router.callback_query(F.data == 'edit_name')
async def write_name(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    current_state = await state.get_state()
    if current_state == 'Dialogue:search' or current_state == 'Dialogue:found':
        await callback.message.answer('<b>Нельзя изменить анкету во время поиска собеседника или диалога</b>')
        return
    await callback.message.answer('<b>напишите ваше имя</b>',
                                    reply_markup=kb.back_kb)
    await state.set_state(EditForm.name)

@user_router.message(EditForm.name)
async def edit_name(message: Message, state: FSMContext):
    if message.content_type != ContentType.TEXT:
        await message.answer('<b>Неправильный формат</b>',
                                reply_markup=kb.back_kb)
        return
    if len(message.text) > 30 or '/' in message.text or ':' in message.text or '.' in message.text or '@' in message.text : 
        await message.answer('<b>Ошибка в имени, введите еще раз</b>',
                                reply_markup=kb.back_kb)
    else:
        await add_name(user_id=message.from_user.id, name=message.text)
        await message.answer(f'<b>Имя изменено на {message.text}</b>',
                                reply_markup=kb.start_kb)
        await state.clear()

@user_router.callback_query(F.data == 'edit_age')
async def write_age(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    current_state = await state.get_state()
    if current_state == 'Dialogue:search' or current_state == 'Dialogue:found':
        await callback.message.answer('<b>Нельзя изменить анкету во время поиска собеседника или диалога</b>')
        return
    await callback.message.answer('<b>Введите возраст</b>',
                                    reply_markup=kb.back_kb)
    await state.set_state(EditForm.age)

@user_router.message(EditForm.age)
async def edit_age(message: Message, state: FSMContext):
    if message.content_type != ContentType.TEXT:
        await message.answer('<b>Неправильный формат</b>',
                                reply_markup=kb.back_kb)
        return
    if not message.text.isdigit() or int(message.text) < 1 or int(message.text) > 150:
        await message.answer('<b>Ошибка в возрасте, введите еще раз</b>',
                                eply_markup=kb.back_kb)
    else:
        await add_age(user_id=message.from_user.id, age=int(message.text))
        await message.answer(f'<b>Возраст изменен на {message.text}</b>',
                            reply_markup=kb.start_kb)
        await commit_form(user_id=message.from_user.id)
        await state.clear()
'''
HELP
'''
@user_router.message(Command('help'))
async def help(message: Message):
    await message.answer(f'<b>Помощ от нейроести: </b><i>{choice(OPTIONS)}</i>\n\nЕсли не подошло используй /help еще раз')

'''
CHATTING
'''
@user_router.message(Dialogue.found)
async def companion_found(message: Message, state: FSMContext):
    companion_id = await get_companion_id(user_id=message.from_user.id)
    filter_gender = await get_filters(user_id=message.from_user.id)
    if filter_gender is None:
        filter_gender = 'не указан'
    else:
        filter_gender = 'мужской' if filter_gender.get('gender') == 'man' else 'женский'
    answer_after_stop_text = f'<b>Для работы с ботом используй кнопки или команды:\n\n• /start - Запуск\n• /form - Анкета\n• /search - Поиск \n• /info - Правила \n• /stop - Закончить диалог \n• /donate - Поддержать\n\nНе знаешь, о чём поговорить? Используй команду /help а встроенная нейросеть поможет!\n\nФильтр поиска: {filter_gender}</b>'

    
    if message.text == '/stop':
        await message.answer('<b>Диалог завершен, можете оценить компаньона</b>',
                                reply_markup=kb.rating(to_user_id=companion_id))
        await message.answer(answer_after_stop_text,
                                reply_markup=kb.start_kb)
        try:
            await bot.send_message(chat_id=companion_id, text='<b>Собеседник завершил диалог, можете оценить компаньона</b>',
                                    reply_markup=kb.rating(to_user_id=message.from_user.id))
            await bot.send_message(chat_id=companion_id, text=answer_after_stop_text,
                                    reply_markup=kb.start_kb)
        except: pass
        await set_state_exit(user_id=message.from_user.id)
        await set_state_exit(user_id=companion_id)
        
        await state.clear()
        storage_key = StorageKey(bot_id=bot.id, user_id=companion_id, chat_id=companion_id)
        await dp.storage.set_state(key=storage_key, state=None)
        return
    
    try:
        if message.content_type == ContentType.TEXT:
            await bot.send_message(chat_id=companion_id, text=message.text, parse_mode=None)
        elif message.content_type == ContentType.PHOTO:
            await bot.send_photo(chat_id=companion_id, photo=message.photo[-1].file_id, caption=message.caption)
        elif message.content_type == ContentType.VIDEO:
            await bot.send_video(chat_id=companion_id, video=message.video.file_id, caption=message.caption)
        elif message.content_type == ContentType.AUDIO:
            await bot.send_audio(chat_id=companion_id, audio=message.audio.file_id, caption=message.caption)
        elif message.content_type == ContentType.VIDEO_NOTE:
            await bot.send_video_note(chat_id=companion_id, video_note=message.video_note.file_id)
        elif message.content_type == ContentType.STICKER:
            await bot.send_sticker(chat_id=companion_id, sticker=message.sticker.file_id)
        elif message.content_type == ContentType.ANIMATION:
            await bot.send_animation(chat_id=companion_id, animation=message.animation.file_id, caption=message.caption)
    except: pass
'''
RAITING
'''
@user_router.callback_query(F.data.startswith('like_user_'))
async def like_user_func(callback: CallbackQuery):
    companion_id = int(callback.data.split('_')[-1])
    is_liked = await like_user(from_user_id=callback.message.chat.id, to_user_id=companion_id)
    if is_liked:
        await callback.answer('Лайк поставлен!')
    else:
        await callback.answer('Вы уже ставили лайк этому пользователю!')

@user_router.callback_query(F.data.startswith('dislike_user_'))
async def dislike_user_func(callback: CallbackQuery):
    companion_id = int(callback.data.split('_')[-1])
    is_disliked = await dislike_user(from_user_id=callback.message.chat.id, to_user_id=companion_id)
    if is_disliked:
        await callback.answer('Дизайк поставлен!')
    else:
        await callback.answer('Вы уже ставили дизлайк этому пользователю!')
'''
FILTERS
'''
@user_router.callback_query(F.data == 'filters')
async def filters(callback: CallbackQuery):
    await callback.answer()
    data = await get_filters(user_id=callback.message.chat.id)
    if data:
        filter_gender = 'мужской' if data.get('gender') == 'man' else 'женский'
        await callback.message.edit_text(f'<b>Изменить фильтр поиска можете, нажав кнопку ниже\n\nФильтр: {filter_gender}</b>',
                                        reply_markup=kb.filters_kb)
    else:
        await callback.message.edit_text('<b>Изменить фильтр поиска можете, нажав кнопку ниже\n\nФильтр: не указано</b>',
                                        reply_markup=kb.filters_kb)

@user_router.callback_query(F.data.startswith('filter_'))
async def filter_gender_func(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    current_state = await state.get_state()
    if current_state == 'Dialogue:search' or current_state == 'Dialogue:found':
        await callback.message.answer('<b>Нельзя изменить фильтр во время поиска собеседника или диалога</b>')
        return
    filter_gender = callback.data[7:]
    if filter_gender == 'reset':
        await reset_filter_gender(user_id=callback.message.chat.id)
        await callback.message.edit_text(f'<b>Фильтр поиска успешно сброшен!\n\nПол: не указано</b>',
                                        reply_markup=kb.start_kb)
        return
    await add_filter_gender(user_id=callback.message.chat.id, filter_gender=filter_gender)
    filter_gender = 'мужской' if filter_gender == 'man' else 'женский'
    await callback.message.edit_text(f'<b>Фильтр поиска успешно изменен!\n\nПол: {filter_gender}</b>',
                                        reply_markup=kb.start_kb)
'''
INFO ABOUT BOT
'''
@user_router.message(Command('info'))
async def info(message: Message):
    await message.answer('<b>Запрещено\n\n1) Рассылать спам-сообщения и зазывать в другие каналы/чаты\n2) Отправлять ссылки на сторонние ресурсы, если они не были одобрены администрацией бота\n3) Оскорблять и унижать других пользователей\n4) Пытаться обмануть или получить информацию конфиденциального характера у других пользователей\n5) Использовать бота для рекламы своих товаров или услуг\nАдминистрация проекта оставляет за собой право заблокировать пользователя, нарушившего какое либо из правил\n\nСпасибо за понимание</b>')
'''
OTHER
'''
@user_router.message(Command('stop'))
async def stop(message: Message):
    await message.answer('<b>У вас нет активного диалога</b>')

@user_router.message(Command('donate'))
async def donate(message: Message):
    await message.answer_photo('https://ibb.co/Mxqy18Ds', caption=f'<b>Поддежать проект можно через CloudTips сканируя QR код выше или нажав <a href="{DONATE_URL}">Поддержать</a></b>',
                                reply_markup=kb.back_new_message_kb)
@user_router.message()
async def other(message: Message):
    await message.answer('<b>Упс, я не знаю такую команду</b>')