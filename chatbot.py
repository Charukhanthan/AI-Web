import os
import json
import requests
from bs4 import BeautifulSoup
import language_tool_python
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline, Conversation

# Set up model cache directory
cache_dir = os.path.join(os.path.dirname(__file__), 'model_cache')
os.makedirs(cache_dir, exist_ok=True)
os.environ['TRANSFORMERS_CACHE'] = cache_dir

# Load BlenderBot model
try:
    tokenizer = AutoTokenizer.from_pretrained("facebook/blenderbot-400M-distill")
    model = AutoModelForSeq2SeqLM.from_pretrained("facebook/blenderbot-400M-distill")
    chatbot = pipeline("conversational", model=model, tokenizer=tokenizer)
    print("BlenderBot model loaded successfully.")
except Exception as e:
    print(f"Failed to load BlenderBot model: {e}")
    chatbot = None

# Initialize LanguageTool for grammar correction
try:
    tool = language_tool_python.LanguageTool('en-US')
except Exception as e:
    print(f"Failed to start LanguageTool server: {e}")
    tool = None

# Load training data
TRAINING_FILE = os.path.join(os.path.dirname(__file__), "training_data.json")
if os.path.exists(TRAINING_FILE):
    with open(TRAINING_FILE, "r") as file:
        trained_responses = json.load(file)
else:
    trained_responses = {}

def save_training_data():
    """ Save responses to the training JSON file """
    with open(TRAINING_FILE, "w") as file:
        json.dump(trained_responses, file, indent=4)

def local_chatbot(user_input):
    """ Check locally trained responses first """
    return trained_responses.get(user_input.lower(), None)

def correct_language(text):
    """ Correct grammatical errors in input text """
    if tool:
        matches = tool.check(text)
        return language_tool_python.utils.correct(text, matches)
    return text  # Return original text if LanguageTool isn't available

def web_search(query):
    """ Perform a simple web search and return the first result """
    try:
        search_url = f"https://www.google.com/search?q={query}"
        response = requests.get(search_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        result = soup.find('div', class_='BNeawe vvjwJb AP7Wnd')
        if result:
            snippet = soup.find('div', class_='BNeawe s3v9rd AP7Wnd').get_text()
            return f"Result: {result.get_text()}\nSnippet: {snippet}"
        else:
            return "No relevant results found."
    except Exception as e:
        return f"Search failed: {e}"

def chatbot_response(user_input):
    """ Main chatbot logic """
    user_input = user_input.strip().lower()

    # Check locally trained responses
    response = local_chatbot(user_input)
    if response:
        return response

    # Grammar correction
    if "correct my grammar" in user_input or "help with spelling" in user_input:
        return f"Corrected: {correct_language(user_input)}"

    # Web search
    if "search" in user_input:
        query = user_input.replace("search", "").strip()
        return web_search(query)

    # AI model response
    if chatbot:
        try:
            conversation = Conversation(user_input)
            response = chatbot(conversation)
            return response.generated_responses[-1]
        except Exception as e:
            return f"Chatbot error: {e}"

    return "I'm not sure how to respond. Try rephrasing your question."

# WebSocket server integration
async def handle_message(message):
    """ Process messages from WebSocket clients """
    response = chatbot_response(message)
    return json.dumps({"response": response})