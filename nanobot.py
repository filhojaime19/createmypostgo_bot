from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext, ConversationHandler, MessageHandler, filters, CallbackQueryHandler

# Definir estados para o ConversationHandler
CHOOSING, SETTING_DESCRIPTION, SETTING_LINK = range(3)

# Token do bot fornecido pelo BotFather
TOKEN = '7988315530:AAGL8irV-cwc6NvZtgimJtFUq61k3WgDZwk'

# Dicionário para armazenar dados do usuário temporariamente
user_data = {}

# Iniciar o bot com um menu interativo
async def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [
            InlineKeyboardButton("Vídeo 🎥", callback_data='video'),
            InlineKeyboardButton("Foto 📸", callback_data='photo'),
        ],
        [
            InlineKeyboardButton("Áudio 🎙️", callback_data='audio'),
            InlineKeyboardButton("Texto 📝", callback_data='text'),
        ],
        [
            InlineKeyboardButton("Cancelar ❌", callback_data='cancel'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("O que você deseja criar?", reply_markup=reply_markup)
    return CHOOSING

# Função para processar as escolhas do menu
async def choose_option(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

    user_data[query.from_user.id] = {'type': query.data}
    if query.data == 'cancel':
        await query.edit_message_text("Operação cancelada.")
        return ConversationHandler.END
    else:
        await query.edit_message_text(f"Você escolheu: {query.data.capitalize()}. Agora, envie a descrição:")
        return SETTING_DESCRIPTION

# Função para receber a descrição
async def set_description(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    user_data[user_id]['description'] = update.message.text

    await update.message.reply_text("Descrição recebida! Agora, envie o link:")
    return SETTING_LINK

# Função para receber o link
async def set_link(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    user_data[user_id]['link'] = update.message.text

    # Mostra o resumo do post
    data = user_data[user_id]
    keyboard = [
        [
            InlineKeyboardButton("Concluir ✅", callback_data='finish'),
            InlineKeyboardButton("Editar ✏️", callback_data='edit'),
        ],
        [
            InlineKeyboardButton("Cancelar ❌", callback_data='cancel'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"Resumo do post:\n\nTipo: {data['type']}\nDescrição: {data['description']}\nLink: {data['link']}\n\nEscolha uma opção abaixo:",
        reply_markup=reply_markup
    )
    return CHOOSING

# Função para concluir ou editar
async def finalize_or_edit(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

    if query.data == 'finish':
        user_id = query.from_user.id
        data = user_data.get(user_id, {})
        if not data:
            await query.edit_message_text("Erro: Dados não encontrados.")
        else:
            await query.edit_message_text(
                f"Postagem concluída com sucesso!\n\nTipo: {data['type']}\nDescrição: {data['description']}\nLink: {data['link']}"
            )
        return ConversationHandler.END
    elif query.data == 'edit':
        await query.edit_message_text("Envie a nova descrição:")
        return SETTING_DESCRIPTION
    elif query.data == 'cancel':
        await query.edit_message_text("Operação cancelada.")
        return ConversationHandler.END

# Configuração principal do bot
def main() -> None:
    # Criar a aplicação do bot
    application = Application.builder().token(TOKEN).build()

    # Configurar o ConversationHandler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [
                CallbackQueryHandler(choose_option),
                MessageHandler(filters.TEXT & ~filters.COMMAND, set_description)
            ],
            SETTING_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_description)],
            SETTING_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_link)],
        },
        fallbacks=[CommandHandler("start", start)]
    )

    # Adicionar o handler ao bot
    application.add_handler(conv_handler)

    # Iniciar o bot
    application.run_polling()

if __name__ == '__main__':
    main()