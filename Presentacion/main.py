import telebot
from LogicaNegocio.langchain_executor import invoke
from Infraestructura.models import Chat, Message, SenderEnum

# Conexion con bot de telegram
TOKEN = "6825035162:AAF_h9GZXW-29xkiYiVqbhCdpPlpO8T5O6U"
bot = telebot.TeleBot(TOKEN)

# Crear una instancia de chat con el estado inicial
chat = Chat()


@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(message, "Hola, soy un bot de telegram, en que puedo ayudarte?")


@bot.message_handler(commands=["help"])
def send_help(message):
    bot.reply_to(message, "puedes interactuar conmigo usando comandos. POR AHORA")


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    # Invocar la función con el input del usuario y la instancia de chat
    ai_response = invoke(chat_history=chat, query=message.text)

    # Enviar la respuesta del agente al usuario
    bot.reply_to(message, ai_response)

    # Añadir los mensajes al historial de chat
    human_message = Message(sender=SenderEnum.HumanMessage, message=message.text)
    ai_message = Message(sender=SenderEnum.AIMessage, message=ai_response)
    chat.messages.extend([human_message, ai_message])


if __name__ == "__main__":
    bot.polling(non_stop=True)
