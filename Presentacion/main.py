import pprint
from LogicaNegocio import langchain_executor
from Infraestructura.models import Chat, Message, SenderEnum
import json
chat = Chat()
print(chat.status)

while True:
    user_query = input("User: ")
    if user_query.startswith('{') and user_query.endswith('}'):
        try:
            # Try to parse the user's input into a dictionary
            user_query = json.loads(user_query)
        except json.JSONDecodeError:
            print("La entrada no es un string JSON válido. Por favor, intenta de nuevo.")
            continue
    ai_response = langchain_executor.invoke(query=user_query, chat_history=chat)
    print(chat.status)
    human_message = Message(sender=SenderEnum.HumanMessage, message=user_query)
    ai_message = Message(sender=SenderEnum.AIMessage, message=ai_response)
    chat.messages.extend([human_message, ai_message])
    pprint.pprint(ai_response)