from openai import OpenAI, AssistantEventHandler
from typing_extensions import override
from dotenv import load_dotenv
import os
import requests
from io import BytesIO
import base64
from data import posts_data, comments_data

class EventHandler(AssistantEventHandler):
    @override
    def on_text_created(self, text) -> None:
        print(f"\nassistant > ", end="", flush=True)

    @override
    def on_text_delta(self, delta, snapshot):
        print(delta.value, end="", flush=True)

class EngagementAgent:
    def __init__(self, api_key: str, engagement_instructions: str):
        self.client = OpenAI(api_key=api_key)
        self.engagement_instructions = engagement_instructions
        self.assistant = self._create_engagement_assistant()
        self.thread = self._create_thread()

    def _create_engagement_assistant(self, create_new=False):
        """Create or retrieve engagement assistant"""
        assistant_id = os.getenv('ENGAGEMENT_ASSISTANT_ID')

        if create_new or not assistant_id:
            assistant = self.client.beta.assistants.create(
                name="Memecoin engagement manager",
                instructions=self.engagement_instructions,
                model="gpt-4o",
            )

            with open('.env', 'a') as f:
                f.write(f'\nENGAGEMENT_ASSISTANT_ID={assistant.id}')
            load_dotenv()
            return assistant
        else:
            try:
                return self.client.beta.assistants.retrieve(assistant_id)
            except Exception:
                return self._create_engagement_assistant(create_new=True)

    def _create_thread(self):
        """Create a new thread for conversation"""
        return self.client.beta.threads.create()

    def get_reply(self, headline: str, comment: str, image_url: str) -> str:
        """Generate a reply for a comment based on the post and comment context"""
        # headline = posts_data[post_id]["headline"]
        # image_url = posts_data[post_id]["generated_image_url"]
        # comment = comments_data[comment_id]


        # Create message with direct image URL
        self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=[
                {
                    "type": "text",
                    "text": f"""
                    Please create a reply to this comment on our meme post.

                    Post Headline: {headline}
                    Comment: {comment}

                    The image from the post is attached. Please consider both the visual content and the comment context when crafting your reply.

                    Keep the reply casual, engaging, and in line with meme culture. Make it feel natural and conversational.
                    """
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image_url,  # Use the direct URL instead of base64
                        "detail": "low"
                    }
                }
            ]
        )

        # Get the response
        with self.client.beta.threads.runs.stream(
            thread_id=self.thread.id,
            assistant_id=self.assistant.id,
            event_handler=EventHandler(),
        ) as stream:
            stream.until_done()

        messages = self.client.beta.threads.messages.list(thread_id=self.thread.id)
        reply = messages.data[0].content[0].text.value

        return reply.strip()
