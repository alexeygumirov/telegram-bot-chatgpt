from dotenv import load_dotenv
import os


class Parametrize():
    GPT_DEFAULT_CHAT_MODEL = "gpt-3.5-turbo"
    MODEL_MAX_TOKENS = 4096
    MAX_HISTORY_SIZE = 50
    MAX_SEARCH_RESULTS = 10

    def __init__(self):
        self.openai_api_key = ""
        self.telegram_api_token = ""
        self.gpt_chat_model = "gpt-3.5-turbo"
        self.max_tokens = 500
        self.chat_history_size = 20
        self.num_search_results = 3
        self.allowed_chat_ids = []
        self.is_public = True

    def read_environment(self):

        # Load environment variables
        load_dotenv()
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.telegram_api_token = os.getenv("TELEGRAM_API_TOKEN")
        self.gpt_chat_model = os.getenv("GPT_CHAT_MODEL", self.GPT_DEFAULT_CHAT_MODEL)
        self.chat_history_size = min(int(os.getenv("CHAT_HISTORY_SIZE", 20)), self.MAX_HISTORY_SIZE)
        self.max_tokens = min(int(os.getenv("MAX_TOKENS", 500)), self.MODEL_MAX_TOKENS)
        self.num_search_results = min(int(os.getenv("NUM_SEARCH_RESULTS", 3)), self.MAX_SEARCH_RESULTS)
        if os.getenv("ALLOWED_CHAT_IDS"):
            self.allowed_chat_ids = [int(chat_id) for chat_id in os.getenv("ALLOWED_CHAT_IDS").split(",")]
            self.is_public = False


class ChatUtils():

    def __init__(self, history_size=20):
        self.history = {}
        self.history_size = history_size

    def add_chat_message(self, chat_id, message):
        """
        Add a message to the chat history of a specific chat.

        Parameters:
        chat_id (int): The ID of the chat.
        message (str): The message to be added.

        Returns:
        None
        """
        if chat_id not in self.history:
            self.history[chat_id] = []
        self.history[chat_id].append(message)
        if len(self.history[chat_id]) > self.history_size:
            self.history[chat_id].pop(0)

    def remove_last_chat_message(self, chat_id):
        """
        Remove the last message from the chat history of a specific chat.

        Parameters:
        chat_id (int): The ID of the chat.

        Returns:
        None
        """
        if chat_id not in self.history:
            return
        self.history[chat_id].pop()

    def clean_chat_history(self, chat_id):
        """
        Clean the chat history of a specific chat.

        Parameters:
        chat_id (int): The ID of the chat.

        Returns:
        None
        """
        self.history[chat_id] = []
