import pprint

from Infraestructura.models import Chat, Message, SenderEnum, ChatStatus
from LogicaNegocio import langchain_executor

# Crear una nueva instancia de Chat e imprimir el estado inicial
chat = Chat()
print(chat.status)

while True:
    user_query = input("User: ")
    ai_response = langchain_executor.invoke(query=user_query, chat_history=chat)

    # Verificar si el StandardAgent ha completado su tarea
    if chat.status == ChatStatus.status1 and 'Vale, regalame un momento 123' in ai_response:
        chat.status = ChatStatus.status2  # Cambiar al estado para SecondAgent

    # Imprimir el estado actual del chat
    print(chat.status)

    # Crear y añadir los mensajes del usuario y de la IA al historial de chat
    human_message = Message(sender=SenderEnum.HumanMessage, message=user_query)
    ai_message = Message(sender=SenderEnum.AIMessage, message=ai_response)
    chat.messages.extend([human_message, ai_message])

    # Imprimir la respuesta de la IA
    pprint.pprint(ai_response)
