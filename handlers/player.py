import asyncio
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.fsm.context import FSMContext
from states import PlayerCreation

router = Router(name="player")

async def increase_ability(ability, callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    curr_ability = data[ability]
    curr_ability_points = data["p"]
    if curr_ability <= 14 and curr_ability_points >= 1:
        curr_ability += 1
        curr_ability_points -= 1
    elif curr_ability <= 16 and curr_ability_points >= 2:
        curr_ability += 1
        curr_ability_points -= 2
    elif curr_ability_points >= 3:
        curr_ability += 1
        curr_ability_points -= 3
    else:
        await callback.answer(text="Недостаточно свободных очков для повышения способности.",show_alert=True)
        return curr_ability_points
    await state.update_data({"p": curr_ability_points, ability: curr_ability})
    return curr_ability_points

async def decrease_ability(ability, callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    curr_ability = data[ability]
    curr_ability_points = data["p"]
    if curr_ability > 16:
        curr_ability -= 1
        curr_ability_points += 3
    elif curr_ability > 14:
        curr_ability -= 1
        curr_ability_points += 2
    elif curr_ability > 5:
        curr_ability -= 1
        curr_ability_points += 1
    else:
        await callback.answer(text="Способность не может иметь значение ниже 4.", show_alert=True)
        return curr_ability_points
    await state.update_data({"p": curr_ability_points, ability: curr_ability})
    return curr_ability_points
    

async def get_keyboard(type, state: FSMContext):
    state_data = await state.get_data()
    buttons = {
        "phase02": [
            [
                InlineKeyboardButton(text=f"Сила: {state_data["s"]} (мод.: {(state_data["s"] - 10) / 2 // 1}", callback_data="none"),
            ],
            [
                InlineKeyboardButton(text="+", callback_data="ability_s+"),
                InlineKeyboardButton(text="-", callback_data="ability_s-"),
            ],
            [
                InlineKeyboardButton(text=f"Ловкость: {state_data["d"]} (мод.: {(state_data["d"] - 10) / 2 // 1})", callback_data="none"),
            ],
            [
                InlineKeyboardButton(text="+", callback_data="ability_d+"),
                InlineKeyboardButton(text="-", callback_data="ability_d-"),
            ],
            [
                InlineKeyboardButton(text=f"Телосложение: {state_data["c"]} (мод.: {(state_data["c"] - 10) / 2 // 1})", callback_data="none"),
            ],
            [
                InlineKeyboardButton(text="+", callback_data="ability_c+"),
                InlineKeyboardButton(text="-", callback_data="ability_c-"),
            ],
            [
                InlineKeyboardButton(text=f"Интеллект: {state_data["i"]} (мод.: {(state_data["i"] - 10) / 2 // 1})", callback_data="none"),
            ],
            [
                InlineKeyboardButton(text="+", callback_data="ability_i+"),
                InlineKeyboardButton(text="-", callback_data="ability_i-"),
            ],
            [
                InlineKeyboardButton(text=f"Мудрость: {state_data["w"]} (мод.: {(state_data["w"] - 10) / 2 // 1})", callback_data="none"),
            ],
            [
                InlineKeyboardButton(text="+", callback_data="ability_w+"),
                InlineKeyboardButton(text="-", callback_data="ability_w-"),
            ],
            [
                InlineKeyboardButton(text="Подтвердить", callback_data="commit_phase02"),
                InlineKeyboardButton(text="Отмена", callback_data="cancel"),
            ]
        ]
    }
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons[type])
    return keyboard



async def reset_player_creation(message: Message, state: FSMContext):
    '''Отмена процедуры создания персонажа'''
    current_state = await state.get_state()
    await asyncio.sleep(10)
    state_type = await state.get_state()
    if state_type == PlayerCreation.phase_01:
        await state.clear()
        await message.delete()
        await message.answer("Создание героя отменено: превышено время ожидания ответа.")

@router.message(Command("create_player"))
async def choose_player_name(message: Message, state: FSMContext):
    phase_01_msg = await message.answer(
        "В ответ на это сообщение, введите имя героя для игры в Chats&Dragons"
    )
    await state.set_state(PlayerCreation.phase_01)
    await state.update_data({"phase_01_msg_id": phase_01_msg.message_id})
    timeout = asyncio.create_task(reset_player_creation(message=phase_01_msg, state=state))
    await timeout

@router.message(
    PlayerCreation.phase_01,
    F.reply_to_message
)
async def characters_menu(message: Message, state: FSMContext):
        await state.set_state(PlayerCreation.phase_02)
        state.get_data
        await state.update_data({"s": 6, "d": 6, "c": 6, "i": 6, "w": 6, "p": 30})
        reply_markup = await get_keyboard("phase02", state)
        await message.answer(
            text=f"Настройка способностей героя\nДоступно очков распределения способностей: 30",
            reply_markup=reply_markup
        )

@router.callback_query(F.data.startswith("ability_"))
async def modify_ability(callback: CallbackQuery, state: FSMContext):
    action = callback.data.split("_")[1]
    match action[1]:
        case "+":
            curr_ability_points = await increase_ability(action[0], callback, state)
            await callback.message.edit_text(text=f"Настройка способностей героя\nДоступно очков распределения способностей: {curr_ability_points}")
            reply_markup = await get_keyboard("phase02", state)
            await callback.message.edit_reply_markup(reply_markup=reply_markup)
        case "-":
            curr_ability_points = await decrease_ability(action[0], callback, state)
            await callback.message.edit_text(text=f"Настройка способностей героя\nДоступно очков распределения способностей: {curr_ability_points}")
            reply_markup = await get_keyboard("phase02", state)
            await callback.message.edit_reply_markup(reply_markup=reply_markup)

