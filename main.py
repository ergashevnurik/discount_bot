import logging

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import *
from config import *
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
        data['first_name'] = msg.text

    await BotState.next()
    await msg.reply(whatIsYourLastName)


@dp.message_handler(state=BotState.lastName)
async def on_contact(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['last_name'] = msg.text

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
        markup = types.ReplyKeyboardRemove()

        # And send message
        await bot.send_message(
            message.chat.id,
            md.text(
                md.text(hi, f", {md.bold(data['last_name'])} {md.bold(data['first_name'])}"),
                md.text(birthday, md.code(data['birthday'])),
                md.text(phoneNumber, md.code(data['contact'])),
                md.text(gender, data['gender']),
                sep='\n',
            ),
            reply_markup=markup,
            parse_mode=ParseMode.MARKDOWN,
        )

    # Finish conversation
    await state.finish()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp)

