from openai import OpenAI, AssistantEventHandler
from typing_extensions import override
from dotenv import load_dotenv
import os
import json
from generate_image import generate_image
from data import posts_data, comments_data

class EventHandler(AssistantEventHandler):
    @override
    def on_text_created(self, text) -> None:
        print(f"\nassistant > ", end="", flush=True)

    @override
    def on_text_delta(self, delta, snapshot):
        print(delta.value, end="", flush=True)

class ContentAgent:
    def __init__(self, api_key: str, writer_instructions: str):
        self.client = OpenAI(api_key=api_key)
        self.writer_instructions = writer_instructions
        self.writer = self._create_writer_assistant()
        self.thread = self._create_thread()

    def _create_writer_assistant(self, create_new=False):
        """Create or retrieve writer assistant"""
        writer_id = os.getenv('WRITER_ASSISTANT_ID')

        if create_new or not writer_id:
            writer = self.client.beta.assistants.create(
                name="Memecoin content creator",
                instructions=self.writer_instructions,
                model="gpt-4o",
                tools=[
                    {"type": "file_search"},
                    {"type": "function", "function": {
                        "name": "generate_image",
                        "description": "Calls a function at fal with an image prompt to generate the image",
                        "parameters": {
                            "type": "object",
                            "required": ["image_prompt", "resolution", "format"],
                            "properties": {
                                "image_prompt": {"type": "string", "description": "The prompt that describes the image to be generated"},
                                "resolution": {"type": "string", "description": "The resolution of the generated image, e.g., '1920x1080'"},
                                "format": {"type": "string", "description": "The format of the generated image, e.g., 'png' or 'jpg'"}
                            }
                        }
                    }}
                ]
            )

            with open('.env', 'a') as f:
                f.write(f'\nWRITER_ASSISTANT_ID={writer.id}')
            load_dotenv()
            return writer
        else:
            try:
                return self.client.beta.assistants.retrieve(writer_id)
            except Exception:
                return self._create_writer_assistant(create_new=True)

    def _create_thread(self):
        """Create a new thread for conversation"""
        return self.client.beta.threads.create()

    def generate_content(self, prompt: str, token_doc_file: str) -> dict:
        """Generate content with the writer assistant"""
        message_file = self.client.files.create(
            file=open(token_doc_file, "rb"),
            purpose="assistants"
        )

        formatted_prompt = f"""
        Please create content about {prompt}

        Remember to provide your response in JSON format with both a headline and image_prompt as specified in your instructions.
        The image prompt must:
        - Start with 'Brett_memecoin'
        - Include a clear description of Brett's expression and surroundings
        - Keep text minimal (not more than 4 words)

        Use the provided token documentation to ensure accuracy.
        """

        self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=formatted_prompt,
            attachments=[{"file_id": message_file.id, "tools": [{"type": "file_search"}]}]
        )

        with self.client.beta.threads.runs.stream(
            thread_id=self.thread.id,
            assistant_id=self.writer.id,
            event_handler=EventHandler(),
        ) as stream:
            stream.until_done()

        messages = self.client.beta.threads.messages.list(thread_id=self.thread.id)
        content = messages.data[0].content[0].text.value

        content_json = {}
        try:
            cleaned_content = content.strip().replace('```json', '', 1).rsplit('```', 1)[0]
            content_json = json.loads(cleaned_content.strip())

            image_prompt = content_json.get('image_prompt')
            if image_prompt:
                image_url = generate_image(image_prompt.strip())
                content_json['generated_image_url'] = image_url
        except Exception as e:
            print(f"Error processing content: {str(e)}")

        return content_json
