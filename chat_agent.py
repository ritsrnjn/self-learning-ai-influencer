from openai import OpenAI, AssistantEventHandler
from typing_extensions import override
from dotenv import load_dotenv
import os
from pathlib import Path

class EventHandler(AssistantEventHandler):
    @override
    def on_text_created(self, text) -> None:
        print(f"\nassistant > ", end="", flush=True)

    @override
    def on_text_delta(self, delta, snapshot):
        print(delta.value, end="", flush=True)

class ChatAgent:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        self.client = OpenAI(api_key=api_key)

        # Create vector store for the token documentation
        self.token_doc_path = Path(__file__).parent / "BASED BRETT.pdf"
        if not self.token_doc_path.exists():
            print(f"Warning: Token documentation not found at {self.token_doc_path}")
            self.vector_store = None
        else:
            # Create a vector store for the token documentation
            self.vector_store = self._create_vector_store()

        self.chat_instructions = """
        You are Brett's AI assistant, representing the Brett memecoin community. Your role is to:

        - Engage with users in a friendly, casual manner that reflects meme culture
        - Provide accurate information about Brett memecoin and its features
        - Use appropriate emojis and meme references when suitable
        - Keep responses concise and natural-sounding
        - Stay positive and enthusiastic about the project
        - Answer questions about tokenomics, community events, and general crypto topics
        - Use humor when appropriate while maintaining professionalism

        Key points about Brett to remember:
        - Community-focused memecoin
        - Limited supply tokenomics
        - Moon and blue theme aesthetic
        - Emphasis on holding and community building

        Always maintain the balance between being helpful and entertaining while representing the Brett brand.
        """

        # Create assistant with file search capability
        self.assistant = self._create_chat_assistant()
        self.thread = self._create_thread()

    def _create_vector_store(self):
        """Create a vector store for the token documentation"""
        try:
            # Upload the file to OpenAI
            file = self.client.files.create(
                file=open(self.token_doc_path, "rb"),
                purpose="assistants"
            )

            # Create a vector store
            vector_store = self.client.beta.vector_stores.create(
                name="Brett Token Documentation",
                file_ids=[file.id]
            )

            # Wait for processing to complete
            vector_store = self.client.beta.vector_stores.create_and_poll(
                name="Brett Token Documentation",
                file_ids=[file.id]
            )

            return vector_store
        except Exception as e:
            print(f"Error creating vector store: {str(e)}")
            return None

    def _create_chat_assistant(self, create_new=False):
        """Create or retrieve chat assistant"""
        chat_id = os.getenv('CHAT_ASSISTANT_ID')

        assistant_params = {
            "name": "Brett Memecoin Chat Assistant",
            "instructions": self.chat_instructions,
            "model": "gpt-4",
            "tools": [{"type": "file_search"}]
        }

        if create_new or not chat_id:
            assistant = self.client.beta.assistants.create(**assistant_params)

            with open('.env', 'a') as f:
                f.write(f'\nCHAT_ASSISTANT_ID={assistant.id}')
            load_dotenv()
            return assistant
        else:
            try:
                return self.client.beta.assistants.retrieve(chat_id)
            except Exception:
                return self._create_chat_assistant(create_new=True)

    def _create_thread(self):
        """Create a new thread for conversation"""
        return self.client.beta.threads.create()

    def chat(self, user_message: str) -> str:
        """Process user message and return response"""
        # If token documentation exists, attach it to the message
        attachments = []
        if self.token_doc_path and self.token_doc_path.exists():
            message_file = self.client.files.create(
                file=open(self.token_doc_path, "rb"),
                purpose="assistants"
            )
            attachments = [{"file_id": message_file.id, "tools": [{"type": "file_search"}]}]

        # Create message in thread
        self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=user_message,
            attachments=attachments
        )

        # Run the assistant
        with self.client.beta.threads.runs.stream(
            thread_id=self.thread.id,
            assistant_id=self.assistant.id,
            event_handler=EventHandler(),
        ) as stream:
            stream.until_done()

        # Get the latest message
        messages = self.client.beta.threads.messages.list(thread_id=self.thread.id)
        return messages.data[0].content[0].text.value
