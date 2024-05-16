import telebot
from LogicaNegocio.langchain_executor import invoke
from Infraestructura.models import Chat, Message, SenderEnum

import whisper

# Conexion con bot de telegram
TOKEN = "6825035162:AAF_h9GZXW-29xkiYiVqbhCdpPlpO8T5O6U"
bot = telebot.TeleBot(TOKEN)

# Crear una instancia de chat con el estado inicial
chat = Chat()


# Se procesan los audios para pasarlo a texto
def transcribe_audio(audio_file_path):
    try:
        model = whisper.load_model("base")
        result = model.transcribe(audio_file_path)
        return result["text"]
    except Exception as e:
        print(f"Error al transcribir el audio: {e}")
        return ""


@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(message, "Hola, soy un bot de telegram, en que puedo ayudarte?")


@bot.message_handler(content_types=["voice"])
def handle_voice_message(message):
    file_info = bot.get_file(message.voice.file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    # Guardar en un formato adecuado para la transcripción
    with open("voice_message.ogg", "wb") as new_file:
        new_file.write(downloaded_file)

    user_input = transcribe_audio("voice_message.ogg")
    process_and_respond(message, user_input)

    # Update chat history with the transcribed audio message
    human_message = Message(sender=SenderEnum.HumanMessage, message=user_input)
    chat.messages.append(human_message)


@bot.message_handler(func=lambda message: message.content_type == "text")
def handle_text_message(message):
    user_input = message.text
    process_and_respond(message, user_input)


def process_and_respond(message, user_input):
    ai_response = invoke(chat_history=chat, query=user_input)
    bot.reply_to(message, ai_response)

    human_message = Message(sender=SenderEnum.HumanMessage, message=user_input)
    ai_message = Message(sender=SenderEnum.AIMessage, message=ai_response)
    chat.messages.extend([human_message, ai_message])


if __name__ == "__main__":
    bot.polling(non_stop=True)
