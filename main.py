import logging
import os
from random import *

from aiogram.utils import executor
from qrcode import *
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import *

import config
from config import *
from is_admin import IsAdmin
from service import register_subscriber, select_user, select_all_users, broadcast, select_purchases, select_loyalty, \
    return_all_users, register_card_details, return_card_details, return_card_number, register_language
from strings import *
from states import *
from keyboard import *


@dp.message_handler(commands=["start"])
async def on_start(msg: types.Message):
    await BotState.language.set()
    await bot.send_message(msg.from_user.id, config._("🇷🇺Выберите язык\n🇺🇿Tilni tanlang"), reply_markup=choose_language)
    logging.basicConfig(level=logging.INFO)


@dp.message_handler(state=BotState.language)
async def on_language(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if msg.text == uz:
            data['language'] = 'uz'
        elif msg.text == ru:
            data['language'] = 'ru'

    await BotState.next()
    await bot.send_message(msg.from_user.id, config._("""✋ Добро пожаловать в Telegram Bot Rasulov GI 🚪
            Пройдите регистрацию и следите за 🛒 своими покупками и 👑 программой лояльности прямо внутри бота.
            Нажмите кнопку "Отправить контакт 👤" для регистрации 👇"""), reply_markup=send_contact)


@dp.message_handler(content_types=types.ContentType.CONTACT, state=BotState.contact)
async def on_contact(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['contact'] = msg.contact.phone_number

        markup = ReplyKeyboardRemove()

        # Finish conversation
    await BotState.next()
    await msg.reply(config._("📃 Пожалуйста, пройдите проверку, заполните поле"), reply_markup=markup)
    await bot.send_document(msg.from_user.id, open('анкета.docx', 'rb'))
    await msg.reply_document(config._("📩 Пожалуйста, заполните бланк и отправьте его обратно, сделав фото"))


# @dp.message_handler(state=BotState.firstName)
# async def on_contact(msg: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         data['first'] = msg.text
#
#     await BotState.next()
#     await msg.reply(whatIsYourLastName)
#
#
# @dp.message_handler(state=BotState.lastName)
# async def on_contact(msg: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         data['last'] = msg.text
#
#     await BotState.next()
#     await msg.reply(whenIsYourBirthday)
#
#
# @dp.message_handler(state=BotState.birthday)
# async def on_contact(msg: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         data['birthday'] = msg.text
#
#     await BotState.next()
#     await msg.reply(chooseGender, reply_markup=gender_btn)
#
#
# @dp.message_handler(lambda message: message.text not in [male, female, other], state=BotState.gender)
# async def process_gender_invalid(message: types.Message):
#     return await message.reply(badGenderChosed)
#
#
# @dp.message_handler(state=BotState.gender)
# async def process_gender(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         data['gender'] = message.text
#
#         # Remove keyboard
#         markup = ReplyKeyboardRemove()
#
#     # Finish conversation
#     await BotState.next()
#     await message.reply(fillTheBlank, reply_markup=markup)
#     await bot.send_document(message.from_user.id, open('анкета.docx', 'rb'))
#     await message.reply_document(sendBack)


@dp.message_handler(content_types=['photo'], state=BotState.verification)
async def process_blank(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['blank'] = message.photo

        filename = f"{message.from_user.id}.jpg"
        await message.photo[-1].download(filename)

        with open(os.path.join(filename), 'rb') as file:
            await bot.send_photo(
                message.chat.id, file,
                caption=md.text(
                    md.text(config._("🟧 Привет! Рад встрече"), f'{message.from_user.last_name} {message.from_user.first_name}'),
                    md.text(config._("🔶 Номер телефона"), md.code(data['contact'])),
                    md.text(config._("🟩 Твой выбор"), md.code(data['language'])),
                    # md.text(hi, f", {md.bold(data['last'])} {md.bold(data['first'])}"),
                    # md.text(birthday, md.code(data['birthday'])),
                    # md.text(phoneNumber, md.code(data['contact'])),
                    # md.text(gender, data['gender']),
                    sep='\n',
                ),
                parse_mode=ParseMode.MARKDOWN,
            )

        with open(os.path.join(filename), 'rb') as file:
            cid = message.chat.id
            user = select_user(str(message.from_user.id))
            if not user and cid not in config.ADMINS:
                verify_btn = InlineKeyboardMarkup().add(InlineKeyboardButton(config._("🟩 Да, подтверждаю"),callback_data=message.from_user.id), InlineKeyboardButton(config._("🟥 Нет, неподтверждаю"),callback_data=message.from_user.id))
                await bot.send_photo(config.ADMINS[0], file, caption=config._("🟩Подтвердите нового пользователя:\nИмя пользователя: {username}\nКонтакт: {contact}\nИмя: {firstName}\nФамилия: {lastName}").format(username=message.from_user.username,contact=data['contact'],firstName=message.from_user.first_name,lastName=message.from_user.last_name), reply_markup=verify_btn)


        # user = register_subscriber(message, data['contact'], data['first'], data['last'], data['birthday'],data['gender'], filename)
        user = register_subscriber(message, data['contact'], message.from_user.first_name, message.from_user.last_name, filename, data['language'])

        if user:
            await message.answer(config._("✅ Вы успешно вошли в систему!"))
        else:
            await message.answer(config._("☑ Вы уже вошли в систему!"))

        await filterUser(message)

    await state.finish()


async def filterUser(message):
    user = select_user(str(message.from_user.id))
    if user.admin:
        await bot.send_message(message.from_user.id, config._("👆 Пожалуйста, выберите вариант из меню"), reply_markup=admin_menu)
    else:
        await bot.send_message(message.from_user.id, config._("👆 Пожалуйста, выберите вариант из меню"), reply_markup=menu)


@dp.message_handler(Text(equals=card, ignore_case=True))
async def show_card(msg: types.Message):
    user = select_user(str(msg.from_user.id))
    data = user.id
    img = make(data)
    file_name, path = await save_to_path(img, user.first, user.last, user.id)
    with open(os.path.join(path, file_name), 'rb') as file:
        await bot.send_photo(msg.chat.id, file, caption=f'{user.first} {user.last} {user.id}')


@dp.message_handler(Text(equals=orders, ignore_case=True))
async def show_purchases(msg: types.Message):
    await bot.send_message(msg.from_user.id, select_purchases(str(msg.from_user.id)))


@dp.message_handler(Text(equals=connect_card, ignore_case=True))
async def show_connect_card(msg: types.Message, state: FSMContext):
    card_details = return_card_details(str(msg.from_user.id))

    if card_details:
        await msg.answer(config._("🟧 Ваша карта зарегистрирована как:\n🔸 {holder}\n🔸 {expired}\n🔸 {name}").format(holder=card_details.holder,expired=card_details.issued, name=card_details.name))
        await state.finish()
    else:
        await ConnectCardState.cardNumber.set()
        await bot.send_message(msg.from_user.id, config._("✍ Пожалуйста, пришлите данные карты Номер карты, который состоит из 16 цифр."))


@dp.message_handler(state=ConnectCardState.cardNumber)
async def process_card_number(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['holder'] = msg.text

    await ConnectCardState.next()
    await msg.reply(config._("📆 Пожалуйста, пришлите дату истечения срока действия"))


@dp.message_handler(state=ConnectCardState.cardDate)
async def process_issue_date(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['issued'] = msg.text

    await ConnectCardState.next()
    await msg.reply(config._("📜 Пожалуйста, пришлите имя карты"))


@dp.message_handler(state=ConnectCardState.cardName)
async def process_card_name(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['card_name'] = msg.text

        # And send message
        await bot.send_message(
            msg.chat.id,
            md.text(
                md.text(config._("🟧 Ваша карта добавлена")),
                md.text(config._("🔸 Номер карты"), md.code(data['holder'])),
                md.text(config._("🔸 Дата истечения срока действия"), md.code(data['issued'])),
                md.text(config._("🔸 Владелец карты"), data['card_name']),
                sep='\n',
            ),
            reply_markup=menu,
            parse_mode=ParseMode.MARKDOWN,
        )

        card_details = register_card_details(msg, data['holder'], data['issued'], data['card_name'])

        if card_details:
            await msg.answer(config._('🟩 Подключено успешно'))
        else:
            await msg.answer(config._('➕ Уже подключено'))

        await filterUser(msg)

    await state.finish()


async def save_to_path(yt, first_name, last_name, id):
    path = './images'
    if not os.path.exists(path):
        os.makedirs(path)
    file_name = f'{first_name}_{last_name}_{id}' + '.png'
    if not os.path.isfile(path):
        yt.save(f'{path}/{file_name}')
    logging.info(f'Started processing {file_name}')
    return file_name, path


@dp.message_handler(Text(equals=loyalty, ignore_case=True))
async def show_loyalty(msg: types.Message):
    await bot.send_message(msg.from_user.id, select_loyalty(str(msg.from_user.id)))


@dp.message_handler(Text(equals=profile, ignore_case=True))
async def show_profile(message: types.Message):
    user = select_user(str(message.from_user.id))

    with open(os.path.join(f'{message.from_user.id}.jpg'), 'rb') as file:
        await bot.send_photo(
            message.chat.id, file,
            caption=md.text(
                md.text(f'{profile}\n', f"{lastName}: {user.last}\n{firstName}: {user.first}"),
                md.text(f'{verified}:', md.code(f"{f'{yes}' if user.verified else f'{no}'}")),
                sep='\n',
            ),
            parse_mode=ParseMode.MARKDOWN,
        )


@dp.message_handler(Text(equals=all_users, ignore_case=True))
async def get_all_users(message: types.Message):
    user = select_user(str(message.from_user.id))
    if user.admin:
        users = select_all_users()
        await message.reply(f'{usersList}\n{users}')
    else:
        await message.reply(config._("🔶 У вас нет разрешения"))


@dp.message_handler(Text(startswith='broadcast', ignore_case=True))
async def broadcast_message(message: types.Message):
    users = return_all_users()
    for user in users:
        await bot.send_message(user.id, broadcast(message.text, user.last, user.first, user.gender))

@dp.message_handler(commands=['lang'])
async def cmd_lang(message: types.Message, locale):
    await message.reply(config._('Your current language: <i>{language}</i>').format(language=locale))

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp)

