import os
from openai import OpenAI
from dotenv import load_dotenv

# Set your OpenAI API key
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
assistant_id = "asst_EZg5wB8vHSkEhJGEt5nM7Ya3"

client = OpenAI()

#load  an assistant
client.beta.assistants.retrieve(assistant_id=assistant_id)

thread = client.beta.threads.create()

client.beta.assistants.update(assistant_id=assistant_id,instructions="YOU LOVE ONLY two DOGS!!!!!")
thread_id = "thread_cpoafPTRH20Nk2JK1eJrOOwZ"
thread = client.beta.threads.retrieve(thread_id=thread_id)

all_messages = []
limit = 100  # Maximum allowed limit per request 
after = None

while True:
    response = client.beta.threads.messages.list(thread_id=thread_id, limit=limit, after=after)
    messages = response.data
    if not messages:
        break
    all_messages.extend(messages)
    after = messages[-1].id  # Set the 'after' cursor to the ID of the last message

for message in all_messages:
    # Extract the text content from the message
    message_content = message.content
    if isinstance(message_content, list):
        text_parts = [block.text.value for block in message_content if hasattr(block, 'text')]
        text = ' '.join(text_parts)
        print(f"{message.role}: {text}")

# save to a list of dictionary
extracted_messages = []
for message in all_messages:
    # Initialize a dictionary for each message
    message_dict = {
        'role': message.role,
        'text': ''
    }

    message_content = message.content
    if isinstance(message_content, list):
        text_parts = [block.text.value for block in message_content if hasattr(block, 'text')]
        text = ' '.join(text_parts)
        message_dict['text'] = text
    
    extracted_messages.append(message_dict)

# Now `extracted_messages` is a list of dictionaries containing the role and text of each message.