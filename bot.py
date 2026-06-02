import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# ---------- НАСТРОЙКИ ----------
BOT_TOKEN = '8835701146:AAEbcx3j76Udnek14zMBwd7QFUfuveBnX4I'
CHANNEL_ID = -1004274610789

# Структура соцсетей и услуг (полная копия Mini App)
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
    service_detail = State()
    await_link = State()
    await_type = State()
    await_quantity = State()
    await_description = State()
    budget = State()
    business = State()

# ---------- КЛАВИАТУРЫ ----------
def socials_keyboard():
    buttons = []
    for key, val in SOCIALS.items():
        buttons.append([InlineKeyboardButton(text=val['name'], callback_data=f'social_{key}')])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def services_keyboard(selected: set, social_key: str):
    services = SOCIALS[social_key]['services']
    buttons = []
    for s in services:
        prefix = '✅ ' if s in selected else ''
        buttons.append([InlineKeyboardButton(text=f'{prefix}{s}', callback_data=f'toggle_{s}')])
    buttons.append([InlineKeyboardButton(text='Готово', callback_data='services_done')])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def boost_types_keyboard():
    buttons = []
    for t in BOOST_TYPES:
        buttons.append([InlineKeyboardButton(text=t, callback_data=f'boost_{t}')])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def budget_keyboard():
    opts = ['5 000 – 20 000 ₽', '20 000 – 50 000 ₽', '50 000 – 100 000 ₽', 'больше 100 000 ₽']
    buttons = [[InlineKeyboardButton(text=opt, callback_data=f'budget_{opt}')] for opt in opts]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# ---------- БОТ ----------
async def main():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    @dp.message(Command('start'))
    async def cmd_start(message: types.Message, state: FSMContext):
        await state.clear()
        await message.answer('👋 Давай рассчитаем цену под тебя!\n\nВыберите соцсеть или платформу:',
                             reply_markup=socials_keyboard())
        await state.set_state(Form.social)

    # --- Выбор соцсети ---
    @dp.callback_query(F.data.startswith('social_'), Form.social)
    async def process_social(callback: types.CallbackQuery, state: FSMContext):
        social_key = callback.data.split('_')[1]
        await state.update_data(social=social_key, selected_services=[])
        await callback.message.edit_text(
            f'Выбрана платформа: <b>{SOCIALS[social_key]["name"]}</b>\nТеперь выберите услуги (можно несколько):',
            reply_markup=services_keyboard(set(), social_key)
        )
        await state.set_state(Form.services)
        await callback.answer()

    # --- Выбор услуг (переключение) ---
    @dp.callback_query(F.data.startswith('toggle_'), Form.services)
    async def toggle_service(callback: types.CallbackQuery, state: FSMContext):
        service_name = callback.data.replace('toggle_', '')
        data = await state.get_data()
        selected = set(data.get('selected_services', []))
        if service_name in selected:
            selected.remove(service_name)
        else:
            selected.add(service_name)
        await state.update_data(selected_services=list(selected))
        social_key = data['social']
        await callback.message.edit_reply_markup(
            reply_markup=services_keyboard(selected, social_key)
        )
        await callback.answer()

    # --- Завершение выбора услуг ---
    @dp.callback_query(F.data == 'services_done', Form.services)
    async def services_done(callback: types.CallbackQuery, state: FSMContext):
        data = await state.get_data()
        selected = data.get('selected_services', [])
        if not selected:
            await callback.answer('Выберите хотя бы одну услугу!', show_alert=True)
            return
        await state.update_data(service_index=0, details={})
        await process_next_service(callback.message, state)
        await state.set_state(Form.service_detail)
        await callback.answer()

    async def process_next_service(message: types.Message, state: FSMContext):
        data = await state.get_data()
        index = data['service_index']
        services = data['selected_services']
        social = SOCIALS[data['social']]
        if index >= len(services):
            await message.answer('Выберите подходящий бюджет:', reply_markup=budget_keyboard())
            await state.set_state(Form.budget)
            return
        service = services[index]
        await state.update_data(current_service=service)
        if service in social['quantitative']:
            await message.answer(f'Уточните: <b>{service}</b>\nВведите ссылку (или описание):')
            await state.set_state(Form.await_link)
        else:
            await message.answer(f'Опишите подробнее: <b>{service}</b>')
            await state.set_state(Form.await_description)

    # --- Сбор деталей количественной услуги ---
    @dp.message(Form.await_link)
    async def process_link(message: types.Message, state: FSMContext):
        link = message.text.strip()
        await state.update_data(temp_link=link)
        await message.answer('Выберите тип:', reply_markup=boost_types_keyboard())
        await state.set_state(Form.await_type)

    @dp.callback_query(F.data.startswith('boost_'), Form.await_type)
    async def process_type(callback: types.CallbackQuery, state: FSMContext):
        boost_type = callback.data.replace('boost_', '')
        await state.update_data(temp_type=boost_type)
        await callback.message.edit_text('Введите количество:')
        await state.set_state(Form.await_quantity)
        await callback.answer()

    @dp.message(Form.await_quantity)
    async def process_quantity(message: types.Message, state: FSMContext):
        try:
            qty = int(message.text.strip())
        except ValueError:
            await message.answer('Пожалуйста, введите число.')
            return
        data = await state.get_data()
        link = data['temp_link']
        boost_type = data['temp_type']
        service = data['current_service']
        details = data.get('details', {})
        if service not in details:
            details[service] = []
        details[service].append({'link': link, 'type': boost_type, 'quantity': qty})
        await state.update_data(details=details, service_index=data['service_index'] + 1)
        await process_next_service(message, state)

    # --- Сбор описания обычной услуги ---
    @dp.message(Form.await_description)
    async def process_description(message: types.Message, state: FSMContext):
        desc = message.text.strip()
        data = await state.get_data()
        service = data['current_service']
        details = data.get('details', {})
        details[service] = desc
        await state.update_data(details=details, service_index=data['service_index'] + 1)
        await process_next_service(message, state)

    # --- Бюджет ---
    @dp.callback_query(F.data.startswith('budget_'), Form.budget)
    async def process_budget(callback: types.CallbackQuery, state: FSMContext):
        budget = callback.data.replace('budget_', '')
        await state.update_data(budget=budget)
        await callback.message.edit_text('Введите вашу сферу деятельности (например, "мебель"):')
        await state.set_state(Form.business)
        await callback.answer()

    # --- Сфера деятельности ---
    @dp.message(Form.business)
    async def process_business(message: types.Message, state: FSMContext):
        business = message.text.strip()
        data = await state.get_data()
        text = format_order(data, business, message.from_user)
        await bot.send_message(CHANNEL_ID, text)
        await message.answer('✅ Спасибо! Ваша заявка отправлена. Мы свяжемся с вами в ближайшее время.')
        await state.clear()

    def format_order(data: dict, business: str, user: types.User) -> str:
        social = SOCIALS[data['social']]['name']
        services = ', '.join(data['selected_services'])
        details = data.get('details', {})
        budget = data.get('budget', 'не указан')

        text = f'📩 <b>Новая заявка</b>\n'
        text += f'👤 От: {user.full_name} (@{user.username})\n' if user.username else f'👤 От: {user.full_name}\n'
        text += f'Платформа: {social}\n'
        text += f'Услуги: {services}\n'
        for srv, det in details.items():
            if isinstance(det, list):
                text += f'  — <b>{srv}</b>:\n'
                for d in det:
                    text += f'    🔗 {d["link"]} | {d["type"]} x {d["quantity"]}\n'
            else:
                text += f'  — <b>{srv}</b>: {det}\n'
        text += f'Бюджет: {budget}\n'
        text += f'Сфера: {business}\n'
        return text

    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
