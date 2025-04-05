from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ContentType
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey

import components.keyboards.kb as kb
from database.crud import (
    check_user, add_user, add_gender, add_name, add_age, 
    commit_form, set_state_exit, get_companion_id, get_filters,
    add_filter_gender, reset_filter_gender, like_user,
    dislike_user
)
from components.states.user_states import Form, Dialogue, EditForm
from components.search_companion import search, search_with_filters
from core.init_bot import bot, dp

user_router = Router()


@user_router.message(CommandStart())
async def start(message: Message):
    answer_text = '<b>Привет этот бот создан для общения!</b>'
    await message.answer(answer_text,
                            reply_markup=kb.start_kb)
    await add_user(user_id=message.from_user.id)

@user_router.callback_query(F.data == 'start_dialogue')
async def start_dialogue(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    current_state = await state.get_state()
    if current_state == 'Dialogue:search' or current_state == 'Dialogue:found':
        await callback.message.answer('Нельзя начать поиск в данный момент')
        return
    user = await check_user(user_id=callback.message.chat.id)
    if user and user.ready == True:
        await state.set_state(Dialogue.search)
        await callback.message.answer('Ищу собеседника',
                                        reply_markup=kb.finish_search)
        filters = await get_filters(user_id=callback.message.chat.id)
        if filters:
            companion = await search_with_filters(user_id=callback.message.chat.id)
            if companion:
                await callback.message.answer('Пользователь найден')
                await state.set_state(Dialogue.found)
        else:
            companion = await search(user_id=callback.message.chat.id)
            if companion:
                await callback.message.answer('Пользователь найден')
                await state.set_state(Dialogue.found)
    else:
        await callback.message.answer('Для начала надо создать анкету, выберите свой пол',
                                        reply_markup=kb.gender_kb)

@user_router.message(Command('search'))
async def search_func(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == 'Dialogue:search' or current_state == 'Dialogue:found':
        await message.answer('Нельзя начать поиск в данный момент')
        return
    user = await check_user(user_id=message.from_user.id)
    if user and user.ready == True:
        await state.set_state(Dialogue.search)
        await message.answer('Ищу собеседника',
                                        reply_markup=kb.finish_search)
        filters = await get_filters(user_id=message.from_user.id)
        if filters:
            companion = await search_with_filters(user_id=message.from_user.id)
            if companion:
                await message.answer('Пользователь найден')
                await state.set_state(Dialogue.found)
        else:
            companion = await search(user_id=message.from_user.id)
            if companion:
                await message.answer('Пользователь найден')
                await state.set_state(Dialogue.found)
    else:
        await message.answer('Для начала надо создать анкету, выберите свой пол',
                                        reply_markup=kb.gender_kb)

@user_router.callback_query(F.data == 'finish_search')
async def finish_search(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    current_state = await state.get_state()
    if current_state != 'Dialogue:search':
        await callback.message.answer('Поиск не начат')
        return
    await callback.message.answer('Поиск отменен',
                                    reply_markup=kb.start_kb)
    await set_state_exit(user_id=callback.message.chat.id)
    await state.clear()

@user_router.callback_query(F.data == 'back')
async def back(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await callback.message.edit_text('<b>Привет этот бот создан для общения!</b>',
                                    reply_markup=kb.start_kb)

'''
ADD FORM
'''
@user_router.callback_query(F.data == 'add_form')
async def add_form(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    current_state = await state.get_state()
    if current_state == 'Dialogue:search' or current_state == 'Dialogue:found':
        await callback.message.answer('Нельзя изменить анкету во время поиска собеседника или диалога')
        return
    data = await check_user(user_id=callback.message.chat.id)
    if not data.name or not data.age or not data.gender:
        await callback.message.answer('Для начала надо создать анкету, выберите свой пол',
                                        reply_markup=kb.gender_kb)
    else:
        await callback.message.answer('Анкета уже создана')

@user_router.callback_query(F.data.startswith('gender_'))
async def gender(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    current_state = await state.get_state()
    if current_state == 'Dialogue:search' or current_state == 'Dialogue:found':
        await callback.message.answer('Нельзя изменить анкету во время поиска собеседника или диалога')
        return
    gender = callback.data[7:]
    await add_gender(user_id=callback.message.chat.id, gender=gender)
    await callback.message.answer('<b>Отлично, Напишите свое имя</b>', 
                                    reply_markup=kb.back_kb)
    await state.set_state(Form.name)

@user_router.message(Form.name)
async def name(message: Message, state: FSMContext):
    if message.content_type != ContentType.TEXT:
        await message.answer('Неправильный формат',
                                reply_markup=kb.back_kb)
        return
    if len(message.text) > 30 or '/' in message.text or ':' in message.text or '.' in message.text or '@' in message.text : 
        await message.answer('Ошибка в имени, попробуйте еще раз',
                                reply_markup=kb.back_kb)
    else:
        await add_name(user_id=message.from_user.id, name=message.text)
        await message.answer('Отлично, напишите свой возраст',
                                reply_markup=kb.back_kb)
        await state.set_state(Form.age)

@user_router.message(Form.age)
async def age(message: Message, state: FSMContext):
    if message.content_type != ContentType.TEXT:
        await message.answer('Неправильный формат',
                                reply_markup=kb.back_kb)
        return
    if not message.text.isdigit() or int(message.text) < 1 or int(message.text) > 150:
        await message.answer('Ошибка в возрасте, попробуйте еще раз',
                                reply_markup=kb.back_kb)
    else:
        await add_age(user_id=message.from_user.id, age=int(message.text))
        await message.answer('Отлично анкета готова',
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
        gender = 'Мужской' if user.gender == 'man' else 'Женский'
        name = user.name.replace('<', '&lt;').replace('>', '&gt;')
        await callback.message.edit_text(f'Ваша анкета:\n\nПол: {gender}\nИмя: {name}\nВозраст: {user.age}\n\nЕсли хотите что нибудь изменить выберите ниже',
                                        reply_markup=kb.edit_kb)
    else:
        await callback.message.edit_text('Ваша анкета еще не создана', 
                                        reply_markup=kb.add_form)

@user_router.message(Command('form'))
async def form_func(message: Message):
    user = await check_user(user_id=message.from_user.id) 
    if user.name and user.age and user.gender:
        gender = 'Мужской' if user.gender == 'man' else 'Женский'
        name = user.name.replace('<', '&lt;').replace('>', '&gt;')
        await message.edit_text(f'Ваша анкета:\n\nПол: {gender}\nИмя: {name}\nВозраст: {user.age}\n\nЕсли хотите что нибудь изменить выберите ниже',
                                        reply_markup=kb.edit_kb)
    else:
        await message.edit_text('Ваша анкета еще не создана', 
                                        reply_markup=kb.add_form)

@user_router.callback_query(F.data == 'edit_gender')
async def choose_gender(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    current_state = await state.get_state()
    if current_state == 'Dialogue:search' or current_state == 'Dialogue:found':
        await callback.message.answer('Нельзя изменить анкету во время поиска собеседника или диалога')
        return
    await callback.message.answer('Выберите свой пол',
                                    reply_markup=kb.edit_gender)

@user_router.callback_query(F.data.startswith('edit_gender_'))
async def edit_gender(callback: CallbackQuery,state: FSMContext):
    await callback.answer()
    
    current_state = await state.get_state()
    if current_state == 'Dialogue:search' or current_state == 'Dialogue:found':
        await callback.message.answer('Нельзя изменить анкету во время поиска собеседника или диалога')
        return
    gender = callback.data[12:]
    await add_gender(user_id=callback.message.chat.id, gender=gender)
    
    gender = 'Мужской' if gender == 'man' else 'Женский'
    await callback.message.answer(f'Пол успешно изменен на {gender}',
                                    reply_markup=kb.start_kb)

@user_router.callback_query(F.data == 'edit_name')
async def write_name(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    current_state = await state.get_state()
    if current_state == 'Dialogue:search' or current_state == 'Dialogue:found':
        await callback.message.answer('Нельзя изменить анкету во время поиска собеседника или диалога')
        return
    await callback.message.answer('Напишите имя',
                                    reply_markup=kb.back_kb)
    await state.set_state(EditForm.name)

@user_router.message(EditForm.name)
async def edit_name(message: Message, state: FSMContext):
    if message.content_type != ContentType.TEXT:
        await message.answer('Неправильный формат',
                                reply_markup=kb.back_kb)
        return
    if len(message.text) > 30 or '/' in message.text or ':' in message.text or '.' in message.text or '@' in message.text : 
        await message.answer('Ошибка в имени, попробуйте еще раз',
                                reply_markup=kb.back_kb)
    else:
        await add_name(user_id=message.from_user.id, name=message.text)
        await message.answer(f'Имя изменено на {message.text}',
                                reply_markup=kb.start_kb)
        await state.clear()

@user_router.callback_query(F.data == 'edit_age')
async def write_age(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    current_state = await state.get_state()
    if current_state == 'Dialogue:search' or current_state == 'Dialogue:found':
        await callback.message.answer('Нельзя изменить анкету во время поиска собеседника или диалога')
        return
    await callback.message.answer('Напишите возраст',
                                    reply_markup=kb.back_kb)
    await state.set_state(EditForm.age)

@user_router.message(EditForm.age)
async def edit_age(message: Message, state: FSMContext):
    if message.content_type != ContentType.TEXT:
        await message.answer('Неправильный формат',
                                reply_markup=kb.back_kb)
        return
    if not message.text.isdigit() or int(message.text) < 1 or int(message.text) > 150:
        await message.answer('Ошибка в возрасте, попробуйте еще раз',
                                eply_markup=kb.back_kb)
    else:
        await add_age(user_id=message.from_user.id, age=int(message.text))
        await message.answer(f'Возраст изменен на {message.text}',
                            reply_markup=kb.start_kb)
        await commit_form(user_id=message.from_user.id)
        await state.clear()
'''
CHATTING
'''
@user_router.message(Dialogue.found)
async def companion_found(message: Message, state: FSMContext):
    companion_id = await get_companion_id(user_id=message.from_user.id)
    
    if message.text == '/stop':
        await message.answer('Диалог завершен',
                                reply_markup=kb.rating(to_user_id=companion_id))
        await message.answer('Привет этот бот создан для общения',
                                reply_markup=kb.start_kb)
        await bot.send_message(chat_id=companion_id, text='Собеседник завершил диалог',
                                reply_markup=kb.rating(to_user_id=message.from_user.id))
        await bot.send_message(chat_id=companion_id, text='Привет этот бот создан для общения',
                                reply_markup=kb.start_kb)
        await set_state_exit(user_id=message.from_user.id)
        await set_state_exit(user_id=companion_id)
        
        await state.clear()
        storage_key = StorageKey(bot_id=bot.id, user_id=companion_id, chat_id=companion_id)
        await dp.storage.set_state(key=storage_key, state=None)
        return
    
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
        filter_gender = 'Мужской' if data.get('gender') == 'man' else 'Женский'
        await callback.message.answer(f'Фильтры\n\nПол: {filter_gender}\nможете сменить ниже',
                                        reply_markup=kb.filters_kb)
    else:
        await callback.message.answer('Фильтры\n\nПол: Не указано\nможете выбрать ниже',
                                        reply_markup=kb.filters_kb)

@user_router.callback_query(F.data.startswith('filter_'))
async def filter_gender_func(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    current_state = await state.get_state()
    if current_state == 'Dialogue:search' or current_state == 'Dialogue:found':
        await callback.message.answer('Нельзя изменить фильтр во время поиска собеседника или диалога')
        return
    filter_gender = callback.data[7:]
    if filter_gender == 'reset':
        await reset_filter_gender(user_id=callback.message.chat.id)
        await callback.message.edit_text(f'Фильтр сброшен!\n\nПол: Не указано',
                                        reply_markup=kb.start_kb)
        return
    await add_filter_gender(user_id=callback.message.chat.id, filter_gender=filter_gender)
    filter_gender = 'Мужской' if filter_gender == 'man' else 'Женский'
    await callback.message.edit_text(f'Фильтр изменен!\n\nПол: {filter_gender}',
                                        reply_markup=kb.start_kb)
'''
INFO ABOUT BOT
'''
@user_router.message(Command('info'))
async def info(message: Message):
    await message.answer('Правила')
'''
OTHER
'''
@user_router.message()
async def other(message: Message):
    await message.answer('Я не знаю такую команду')