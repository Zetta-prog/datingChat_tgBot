from aiogram.types import Message, CallbackQuery, ContentType
from aiogram.filters import Command
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv

import os

from database.crud import amount_of_users, get_all_users_id
from components.keyboards.admin_kb import kb_admin, kb_cancel
from components.states.admin_states import Admin
from core.init_bot import bot


admin_router = Router()

load_dotenv()

@admin_router.message(Command('admin'))
async def admin(message: Message):
    if message.from_user.id == int(os.getenv('ADMIN_ID')):
        amount = await amount_of_users()
        
        await message.answer(f'Количество пользователей: {amount}\n\n',
                                reply_markup=kb_admin)

@admin_router.callback_query(F.data == 'mailing')
async def write_mail(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    await callback.message.answer('Введите конент разсылки',
                                    reply_markup=kb_cancel)
    await state.set_state(Admin.mail_text)

@admin_router.message(Admin.mail_text)
async def send_mails(message: Message, state: FSMContext):
    users_id = await get_all_users_id()
    succes_users = 0
    if message.content_type == ContentType.TEXT:
        await state.clear()
        for user_id in users_id:
            try:
                await bot.send_message(user_id, message.text)
                succes_users += 1
            except:
                pass
    elif message.content_type == ContentType.PHOTO:
        await state.clear()
        for user_id in users_id:
            try:
                await bot.send_photo(user_id, photo=message.photo[-1].file_id, caption=message.caption)
                succes_users += 1
            except:
                pass
    elif message.content_type == ContentType.VIDEO:
        await state.clear()
        for user_id in users_id:
            try:
                await bot.send_video(user_id, video=message.video.file_id, caption=message.caption)
                succes_users += 1
            except:
                pass
    elif message.content_type == ContentType.STICKER:
        await state.clear()
        for user_id in users_id:
            try:
                await bot.send_sticker(user_id, sticker=message.sticker.file_id)
                succes_users += 1
            except:
                pass
    elif message.content_type == ContentType.ANIMATION:
        await state.clear()
        for user_id in users_id:
            try:
                await bot.send_animation(user_id, animation=message.animation.file_id, caption=message.caption)
                succes_users += 1
            except:
                pass
    elif message.content_type == ContentType.VIDEO_NOTE:
        await state.clear()
        for user_id in users_id:
            try:
                await bot.send_video_note(user_id, video_note=message.video_note.file_id)
                succes_users += 1
            except:
                pass
    else:
        await message.answer('Неправильный формат, попробуй еще раз',
                                    reply_markup=kb_cancel)
        return
    await message.answer(f'Разсылка окончена, отправлено {succes_users} пользователям')
    

@admin_router.callback_query(F.data == 'cancel')
async def cancel(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    amount = await amount_of_users()
    await callback.message.answer(f'Количество пользователей: {amount}\n\n',
                                    reply_markup=kb_admin)