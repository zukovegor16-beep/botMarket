import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommand, BotCommandScopeDefault
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiohttp import web

# ---------- НАСТРОЙКИ ----------
BOT_TOKEN = '8835701146:AAEbcx3j76Udnek14zMBwd7QFUfuveBnX4I'
GROUP_ID = -1004274610789

SOCIALS = {
    'vk': {
        'name': 'ВКонтакте',
        'services': [
            'Настройка таргетированной рекламы', 'Продвижение сообщества',
            'Продвижение + ведение сообщества', 'Разработка мини-приложения ВК',
            'Разработка чат-бота ВК', 'Рассылка сообщений (холодным)',
            'Рассылка сообщений (подписчикам)', 'Накрутка (все типы)',
            'Продажа аккаунтов/сообществ', 'Иная услуга'
        ],
        'quantitative': ['Накрутка (все типы)', 'Продажа аккаунтов/сообществ',
                         'Рассылка сообщений (холодным)', 'Рассылка сообщений (подписчикам)']
    },
    'tiktok': {
        'name': 'TikTok',
        'services': ['Реклама TikTok Ads', 'Продвижение аккаунта', 'Создание креативов',
                     'Накрутка (все типы)', 'Продажа аккаунтов', 'Иная услуга'],
        'quantitative': ['Накрутка (все типы)', 'Продажа аккаунтов']
    },
    'instagram': {
        'name': 'Instagram',
        'services': ['Таргетированная реклама', 'Ведение аккаунта', 'Креативы',
                     'Накрутка (все типы)', 'Продажа аккаунтов', 'Иная услуга'],
        'quantitative': ['Накрутка (все типы)', 'Продажа аккаунтов']
    },
    'telegram': {
        'name': 'Telegram',
        'services': ['Реклама в Telegram', 'Продвижение канала/чата', 'Разработка Mini App',
                     'Разработка бота', 'Рассылка сообщений', 'Накрутка (подписчики/просмотры)',
                     'Продажа каналов/аккаунтов', 'Иная услуга'],
        'quantitative': ['Рассылка сообщений', 'Накрутка (подписчики/просмотры)',
                         'Продажа каналов/аккаунтов']
    },
    'twitter': {
        'name': 'Twitter (X)',
        'services': ['Продвижение аккаунта', 'Накрутка (все типы)', 'Продажа аккаунтов', 'Иная услуга'],
        'quantitative': ['Накрутка (все типы)', 'Продажа аккаунтов']
    },
    'facebook': {
        'name': 'Facebook',
        'services': ['Реклама Facebook Ads', 'Ведение страницы', 'Накрутка (все типы)',
                     'Продажа аккаунтов', 'Иная услуга'],
        'quantitative': ['Накрутка (все типы)', 'Продажа аккаунтов']
    },
    'yandex_direct': {
        'name': 'Яндекс.Директ',
        'services': ['Настройка и ведение', 'Аудит', 'Создание объявлений',
                     'Подключение аналитики', 'Иная услуга'],
        'quantitative': []
    },
    'google_ads': {
        'name': 'Google Ads',
        'services': ['Контекстная реклама', 'Google Shopping', 'Аудит', 'Создание объявлений',
                     'Аналитика', 'Иная услуга'],
        'quantitative': []
    },
    'wildberries': {
        'name': 'Wildberries',
        'services': ['SEO-оптимизация карточек', 'Внутренняя реклама', 'Аналитика',
                     'Контент для карточек', 'Иная услуга'],
        'quantitative': []
    },
    'ozon': {
        'name': 'OZON',
        'services': ['SEO-оптимизация', 'Продвижение', 'Аналитика', 'Контент', 'Иная услуга'],
        'quantitative': []
    },
    'avito': {
        'name': 'Avito',
        'services': ['Продвижение объявлений', 'SEO-оптимизация', 'Массовый постинг',
                     'Аналитика', 'Иная услуга'],
        'quantitative': ['Массовый постинг']
    },
    'other': {
        'name': 'Другие услуги',
        'services': [
            'Разработка сайта', 'Преобразование в Mini App', 'Разработка Mini App',
            'Разработка бота с ИИ', 'Мобильное приложение', 'Внедрение CRM',
            'SEO-оптимизация сайта', 'SEO карточек', 'Рассылка Email',
            'Рассылка ВК/Telegram', 'Сквозная аналитика', 'Логотип/брендбук',
            'Баннеры', 'Рилс/видео', 'Комплексный брендинг',
            'Накрутка (любые соцсети)', 'Продажа аккаунтов/каналов', 'Иная услуга'
        ],
        'quantitative': ['Рассылка Email', 'Рассылка ВК/Telegram', 'Накрутка (любые соцсети)',
                         'Продажа аккаунтов/каналов']
    }
}

BOOST_TYPES = [
    '👥 Подписчики', '👀 Просмотры короткие', '⏳ Просмотры долгие', '❤️ Лайки',
    '🔄 Репосты', '💬 Комментарии', '👍 Положительные реакции', '👎 Отрицательные реакции'
]

# ---------- FSM ----------
class Form(StatesGroup):
    social = State()
    services = State()
    await_link = State()
    await_type = State()
    await_quantity = State()
    await_description = State()
    budget = State()
    business = State()

# ---------- КЛАВИАТУРЫ ----------
def socials_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=val['name'], callback_data=f'social_{key}')] for key, val in SOCIALS.items()
    ])

def services_keyboard(selected, social_key):
    services = SOCIALS[social_key]['services']
    buttons = []
    for s in services:
        prefix = '✅ ' if s in selected else ''
        buttons.append([InlineKeyboardButton(text=f'{prefix}{s}', callback_data=f'toggle_{s}')])
    buttons.append([InlineKeyboardButton(text='Готово', callback_data='services_done')])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def boost_types_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t, callback_data=f'boost_{t}')] for t in BOOST_TYPES
    ])

def budget_keyboard():
    opts = ['5 000 – 20 000 ₽', '20 000 – 50 000 ₽', '50 000 – 100 000 ₽', 'больше 100 000 ₽']
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=opt, callback_data=f'budget_{opt}')] for opt in opts
    ])

# ---------- БОТ ----------
async def main():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    await bot.set_my_commands([
        BotCommand(command="start", description="Жми 👈 для просмотра услуг")
    ], scope=BotCommandScopeDefault())

    await bot.delete_webhook(drop_pending_updates=True)
    await asyncio.sleep(1)

    @dp.message(Command('start'))
    async def cmd_start(message: types.Message, state: FSMContext):
        await state.clear()
        await message.answer(
            '👋 Давай рассчитаем цену под тебя!\n\nВыберите соцсеть или платформу:',
            reply_markup=socials_keyboard()
        )
        await state.set_state(Form.social)

    # Платформы, для которых удаляем старое сообщение и отправляем новое
    DELETE_AND_RESEND = {'vk', 'telegram', 'yandex_direct', 'google_ads'}

    @dp.callback_query(F.data.startswith('social_'))
    async def process_social(callback: types.CallbackQuery, state: FSMContext):
        social_key = callback.data.split('_')[1]
        await state.update_data(social=social_key, selected_services=[], details={}, service_index=0)

        if social_key in DELETE_AND_RESEND:
            # Удаляем (с защитой) и отправляем новое сообщение
            try:
                await callback.message.delete()
            except Exception:
                pass
            await bot.send_message(
                chat_id=callback.message.chat.id,
                text=f'Выбрана платформа: <b>{SOCIALS[social_key]["name"]}</b>\nТеперь выберите услуги (можно несколько):',
                reply_markup=services_keyboard(set(), social_key)
            )
        else:
            # Для остальных — редактируем текущее сообщение
            await callback.message.edit_text(
                f'Выбрана платформа: <b>{SOCIALS[social_key]["name"]}</b>\nТеперь выберите услуги (можно несколько):',
                reply_markup=services_keyboard(set(), social_key)
            )
        await state.set_state(Form.services)

    @dp.callback_query(F.data.startswith('toggle_'))
    async def toggle_service(callback: types.CallbackQuery, state: FSMContext):
        data = await state.get_data()
        service_name = callback.data.replace('toggle_', '')
        selected = set(data.get('selected_services', []))
        if service_name in selected:
            selected.remove(service_name)
        else:
            selected.add(service_name)
        await state.update_data(selected_services=list(selected))
        social_key = data.get('social')
        await callback.message.edit_reply_markup(reply_markup=services_keyboard(selected, social_key))

    @dp.callback_query(F.data == 'services_done')
    async def services_done(callback: types.CallbackQuery, state: FSMContext):
        data = await state.get_data()
        selected = data.get('selected_services', [])
        if not selected:
            await callback.answer('Выберите хотя бы одну услугу!', show_alert=True)
            return

        social = SOCIALS[data['social']]
        quantitative = [s for s in selected if s in social['quantitative']]
        cost = [s for s in selected if s not in social['quantitative']]
        await state.update_data(has_cost=bool(cost), has_quantitative=bool(quantitative),
                                quantitative=quantitative, cost=cost, details={})

        social_key = data['social']
        if social_key in DELETE_AND_RESEND:
            try:
                await callback.message.delete()
            except Exception:
                pass
            await bot.send_message(
                chat_id=callback.message.chat.id,
                text='Вы выбрали услуги. Сейчас зададим уточняющие вопросы.'
            )
        else:
            await callback.message.edit_text('Вы выбрали услуги. Сейчас зададим уточняющие вопросы.')

        await process_next_service(callback.message.chat.id, bot, state)

    async def process_next_service(chat_id: int, bot: Bot, state: FSMContext):
        data = await state.get_data()
        quantitative = data.get('quantitative', [])
        cost = data.get('cost', [])
        index = data.get('service_index', 0)

        if index < len(quantitative):
            service = quantitative[index]
            await state.update_data(current_service=service, current_type='quantitative')
            await bot.send_message(chat_id, f'Уточните: <b>{service}</b>\nВведите ссылку (или описание):')
            await state.set_state(Form.await_link)
            return

        cost_index = index - len(quantitative)
        if cost_index < len(cost):
            service = cost[cost_index]
            await state.update_data(current_service=service, current_type='cost')
            await bot.send_message(chat_id, f'Опишите подробнее: <b>{service}</b>')
            await state.set_state(Form.await_description)
            return

        if data.get('has_cost'):
            await bot.send_message(chat_id, 'Выберите подходящий бюджет:', reply_markup=budget_keyboard())
            await state.set_state(Form.budget)
        else:
            await bot.send_message(chat_id, 'Введите вашу сферу деятельности (например, "мебель"):')
            await state.set_state(Form.business)

    @dp.message(Form.await_link)
    async def process_link(message: types.Message, state: FSMContext):
        await state.update_data(temp_link=message.text.strip())
        await message.answer('Выберите тип:', reply_markup=boost_types_keyboard())
        await state.set_state(Form.await_type)

    @dp.callback_query(F.data.startswith('boost_'))
    async def process_type(callback: types.CallbackQuery, state: FSMContext):
        await state.update_data(temp_type=callback.data.replace('boost_', ''))
        await callback.message.edit_text('Введите количество:')
        await state.set_state(Form.await_quantity)

    @dp.message(Form.await_quantity)
    async def process_quantity(message: types.Message, state: FSMContext):
        try:
            qty = int(message.text.strip())
        except ValueError:
            await message.answer('Пожалуйста, введите число.')
            return
        data = await state.get_data()
        details = data.get('details', {})
        service = data['current_service']
        details.setdefault(service, []).append({
            'link': data['temp_link'],
            'type': data['temp_type'],
            'quantity': qty
        })
        new_index = data['service_index'] + 1
        await state.update_data(details=details, service_index=new_index)
        await process_next_service(message.chat.id, bot, state)

    @dp.message(Form.await_description)
    async def process_description(message: types.Message, state: FSMContext):
        data = await state.get_data()
        details = data.get('details', {})
        details[data['current_service']] = message.text.strip()
        new_index = data['service_index'] + 1
        await state.update_data(details=details, service_index=new_index)
        await process_next_service(message.chat.id, bot, state)

    @dp.callback_query(F.data.startswith('budget_'))
    async def process_budget(callback: types.CallbackQuery, state: FSMContext):
        await state.update_data(budget=callback.data.replace('budget_', ''))
        await callback.message.edit_text('Введите вашу сферу деятельности (например, "мебель"):')
        await state.set_state(Form.business)

    @dp.message(F.text)
    async def handle_text(message: types.Message, state: FSMContext):
        current_state = await state.get_state()
        if current_state == Form.business:
            data = await state.get_data()
            if not data:
                await message.answer('Произошла ошибка. Нажмите /start')
                return
            text = format_order(data, message.text.strip(), message.from_user)
            await bot.send_message(GROUP_ID, text)
            await message.answer(
                '✅ Спасибо! Ваша заявка отправлена.\nМы уже составляем предложение ⚡️\nХотите рассчитать ещё? Нажмите кнопку ниже.',
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔄 Новый расчёт", callback_data="restart")]
                ])
            )
            await state.clear()
        elif current_state is None:
            await message.answer('Нажмите /start, чтобы начать.')
        else:
            await message.answer('Следуйте инструкциям. Для нового расчёта нажмите /start')

    @dp.callback_query(F.data == "restart")
    async def restart(callback: types.CallbackQuery, state: FSMContext):
        await state.clear()
        await callback.message.edit_text(
            '👋 Давай рассчитаем цену под тебя!\n\nВыберите соцсеть или платформу:',
            reply_markup=socials_keyboard()
        )
        await state.set_state(Form.social)

    def format_order(data: dict, business: str, user: types.User) -> str:
        social = SOCIALS[data['social']]['name']
        all_selected = data.get('quantitative', []) + data.get('cost', [])
        services = ', '.join(all_selected)
        details = data.get('details', {})
        budget = data.get('budget', 'не указан')
        text = f'📩 <b>Новая заявка</b>\n'
        text += f'👤 От: {user.full_name} (@{user.username})\n' if user.username else f'👤 От: {user.full_name}\n'
        text += f'Платформа: {social}\nУслуги: {services}\n'
        for srv, det in details.items():
            if isinstance(det, list):
                text += f'  — <b>{srv}</b>:\n'
                for d in det:
                    text += f'    🔗 {d["link"]} | {d["type"]} x {d["quantity"]}\n'
            else:
                text += f'  — <b>{srv}</b>: {det}\n'
        if data.get('has_cost'):
            text += f'Бюджет: {budget}\n'
        text += f'Сфера: {business}\n'
        return text

    # --- Веб-сервер ---
    app = web.Application()
    async def health(request):
        return web.Response(text="OK")
    app.router.add_get('/', health)
    app.router.add_get('/ping', health)

    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
