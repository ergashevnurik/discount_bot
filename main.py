import logging
import os
from random import *

from qrcode import *
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import *
from config import *
from service import register_subscriber, select_user, select_all_users, broadcast, select_purchases
from strings import *
from states import *
from keyboard import *

@dp.message_handler(commands=["start"])
async def on_start(msg: types.Message):
    await BotState.contact.set()
    await bot.send_message(msg.from_user.id, greeting_text, reply_markup=send_contact)
    logging.basicConfig(level=logging.INFO)


@dp.message_handler(content_types=types.ContentType.CONTACT, state=BotState.contact)
async def on_contact(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['contact'] = msg.contact.phone_number

    await BotState.next()
    await msg.reply(whatIsYourFirstName)


@dp.message_handler(state=BotState.firstName)
async def on_contact(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['first'] = msg.text

    await BotState.next()
    await msg.reply(whatIsYourLastName)


@dp.message_handler(state=BotState.lastName)
async def on_contact(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['last'] = msg.text

    await BotState.next()
    await msg.reply(whenIsYourBirthday)


@dp.message_handler(state=BotState.birthday)
async def on_contact(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['birthday'] = msg.text

    await BotState.next()
    await msg.reply(chooseGender, reply_markup=gender_btn)


@dp.message_handler(lambda message: message.text not in [male, female, other], state=BotState.gender)
async def process_gender_invalid(message: types.Message):
    return await message.reply(badGenderChosed)


@dp.message_handler(state=BotState.gender)
async def process_gender(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['gender'] = message.text

        # Remove keyboard
        markup = ReplyKeyboardRemove()

        # And send message
        await bot.send_message(
            message.chat.id,
            md.text(
                md.text(hi, f", {md.bold(data['last'])} {md.bold(data['first'])}"),
                md.text(birthday, md.code(data['birthday'])),
                md.text(phoneNumber, md.code(data['contact'])),
                md.text(gender, data['gender']),
                sep='\n',
            ),
            reply_markup=markup,
            parse_mode=ParseMode.MARKDOWN,
        )

        user = register_subscriber(message, data['contact'], data['first'], data['last'], data['birthday'], data['gender'])

        if user:
            await message.answer(signedInSuccessfully)
        else:
            await message.answer(alreadySignedIn)

        await bot.send_message(message.from_user.id, chooseMenu, reply_markup=menu)
    # Finish conversation
    await state.finish()


@dp.message_handler(Text(equals=card, ignore_case=True))
async def show_card(msg: types.Message):
    user = select_user(msg.from_user.id)
    data = user.id
    img = make(data)
    file_name, path = await save_to_path(img, user.first, user.last, user.id)
    with open(os.path.join(path, file_name), 'rb') as file:
        await bot.send_photo(msg.chat.id, file, caption=f'{user.first} {user.last} {user.id}')


@dp.message_handler(Text(equals=orders, ignore_case=True))
async def show_purchases(msg: types.Message):
    await bot.send_message(msg.from_user.id, select_purchases(msg.from_user.id))


async def save_to_path(yt, first_name, last_name, id):
    path = './images'
    if not os.path.exists(path):
        os.makedirs(path)
    file_name = f'{first_name}_{last_name}_{id}' + '.png'
    if not os.path.isfile(path):
        yt.save(f'{path}/{file_name}')
    logging.info(f'Started processing {file_name}')
    return file_name, path


@dp.message_handler(Text(equals=profile, ignore_case=True))
async def show_profile(message: types.Message):
    user = select_user(message.from_user.id)

    await message.answer(f"{profile}\n"
                         f"{lastName}: {user.last}\n{firstName}: {user.first}\n"
                         f"{username}: @{user.username}\n"
                         f"{admin}: {f'{yes}' if user.admin else f'{no}'}")


@dp.message_handler(commands='all_users')
async def get_all_users(message: types.Message):
    user = select_user(message.from_user.id)
    if user.admin:
        users = select_all_users()
        await message.reply(f'{usersList}\n{users}')
    else:
        await message.reply(permission)


@dp.message_handler(Text(startswith='broadcast', ignore_case=True))
async def broadcast_message(message: types.Message):
    await message.reply(broadcast(message.text))

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp)

