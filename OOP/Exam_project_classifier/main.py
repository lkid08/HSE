import logging
from telegram import (
    Update, 
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder, 
    ContextTypes, 
    CommandHandler, 
    filters, 
    MessageHandler, 
    CallbackQueryHandler, 
    ConversationHandler
)

from classifier import *


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.getLogger('httpx').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)



return_kb = [[InlineKeyboardButton('Вернуться в меню', callback_data='menu')]]
return_markup=InlineKeyboardMarkup(return_kb)

classifier = Classifier()


# states
NAME, MENU, CHOOSING, TEXT, CLF_CONFIG = range(5)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Добро пожаловать в бот-классификатор!\n"
        "Введите свое имя:\n"
    )

    return NAME


async def change_name(update: Update, context:ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
            text='Введите свое имя:'
            )
    
    return NAME


async def name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info("Имя пользователя %s: %s", user.first_name, update.message.text)
    
    text = update.message.text
    context.user_data['tg_id'] = user.first_name
    context.user_data['name'] = text


    confirmation_kb = [
        [InlineKeyboardButton('Подтверждаю', callback_data='menu')],
        [InlineKeyboardButton('Назад', callback_data='change_name')]
        ]

    await update.message.reply_text(
        text=f'Ваше имя: {context.user_data["name"]}?\n',
        reply_markup=InlineKeyboardMarkup(confirmation_kb)
    )
    
    return MENU


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("Пользователь %s прервал регистрацию.", user.first_name)
    await update.message.reply_text(
        "Регистрация прервана."
    )

    return ConversationHandler.END
    

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    connection_subscription_kb = [
        ['Классифицировать текст', 'Мои тексты', 'Настроить классификатор'],
        ['Помощь']
        ]
    reply_markup=ReplyKeyboardMarkup(connection_subscription_kb, one_time_keyboard=True)

    await query.message.edit_text(
            text=f'Добро пожаловать в меню бота-классификатора!\n'
            'Выберите одну из опций ниже\n\n'
            'Для помощи нажмите "Помощь"',
            reply_markup=reply_markup
            )
    
    return CHOOSING
    

# TODO: handle classification
async def classify(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    
    await update.message.edit_text(
        text='Классификация нового текста\n\n'
        'Введите текст:'
    )

    return TEXT


async def clf_config(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    clf_config_kb = [
        [InlineKeyboardButton('Добавить класс', callback_data='add'), InlineKeyboardButton('Убрать класс', callback_data='remove')],
        [InlineKeyboardButton('Вернуться в меню', callback_data='menu')]
    ]
    clf_config_markup = InlineKeyboardMarkup(clf_config_kb)
    
    await update.message.edit_text(
        text='На данный момент, классификатор распознает следующие классы:\n\n'
        f'{classifier.get_candidate_labels}',
        reply_markup=clf_config_markup

    )

    return CLF_CONFIG


async def add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    
    await update.message.edit_text(
        text='Чтобы добавить новый класс,\n\n'
        'Введите его ниже:'
    )

    return CLF_CONFIG


async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    
    await update.message.edit_text(
        text='Классификация нового текста\n\n'
        'Введите текст:'
    )

    return CLF_CONFIG


async def process(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    text = update.message.text

    wait_msg = await update.message.reply_text(
        text='Текст классифицируется\n\n'
        'Пожалуйста, подождите...'
    )

    extracted_class = classifier.classify_text(text)
    
#     # get result 
#     # display result


    await wait_msg.edit_text(
        text='Результат классификации:\n\n'
        f'{extracted_class}',
        reply_markup=return_markup
    )

    return MENU


# TODO: handle previous classification results
async def my_texts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    # ping article storage class 
    
    # if NOTEXTS:
    #     await update.message.reply_text(
    #         text='Ваши тексты:\n'
    #         'Сейчас у вас нет классифицированных текстов.',
    #         reply_markup=[ReplyKeyboardRemove(), return_kb]
    #     )
    # else:
    #     await update.message.reply_text(
    #         text='Ваши тексты:\n'
    #         f'{TEXTS}',
    #         reply_markup=[ReplyKeyboardRemove(), return_kb]
    #     )

    await update.message.reply_text(
        text='Мои тексты:\n\n'
        'На данный момент, у Вас нет текстов.\n'
        'Для начала, классифицируйте какой-нибудь текст.',
        reply_markup=return_markup
    )

    return MENU


# TODO: handle help function
async def help_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    await update.message.reply_text(
        text='Бот-классификатор сделан для классификации статей\n'
        'Чтобы классифицировать текст, нажмите\n\n'
        '---(Классифицировать текст)---\n\n'
        'И отправьте нужный текст в сообщении\n\n\n'
        'Если у Вас уже есть классифицированные тексты, нажмите\n\n'
        '---(Мои тексты)---\n\n',
        reply_markup=return_markup
    )

    return MENU


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text='Я не понимаю эту команду...\n'
        'Если Вам нужна помощь, нажмите "Помощь"'
        )


if __name__ == '__main__':
    application = ApplicationBuilder().token('6871722083:AAHAfWghwL4huE0DA3ih_UxuH_8YSZ5DbQo').build()
    
    start_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name)],

            MENU: [
                CallbackQueryHandler(menu, pattern="menu"),
                CallbackQueryHandler(change_name, pattern="change_name")
                ],

            CHOOSING: [
                MessageHandler(filters.Regex("^Классифицировать текст$"), classify),
                MessageHandler(filters.Regex("^Мои тексты$"), my_texts),
                MessageHandler(filters.Regex("^Настроить классификатор$"), clf_config),
                MessageHandler(filters.Regex("^Помощь$"), help_list)
            ],

            CLF_CONFIG: [
                CallbackQueryHandler(add, pattern="add"),
                CallbackQueryHandler(remove, pattern="remove"),
                CallbackQueryHandler(menu, pattern="menu")

            ]

            TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, process)]

        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    application.add_handler(start_handler)

    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    application.add_handler(unknown_handler)

    application.run_polling()