from openai import OpenAI, AssistantEventHandler
from typing_extensions import override
from dotenv import load_dotenv
import os
import json
from memory_data import posts_data, comments_data, users_data, system_instructions
from copy import deepcopy

class EventHandler(AssistantEventHandler):
    @override
    def on_text_created(self, text) -> None:
        print(f"\nassistant > ", end="", flush=True)

    @override
    def on_text_delta(self, delta, snapshot):
        print(delta.value, end="", flush=True)

class MemoryAgent:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.memory_assistant = self._create_memory_assistant()
        self.thread = self._create_thread()
        self.users_data = deepcopy(users_data)
        self.posts_data = deepcopy(posts_data)
        self.system_instructions = deepcopy(system_instructions)

    def _create_memory_assistant(self, create_new=False):
        """Create or retrieve memory assistant"""
        memory_id = os.getenv('MEMORY_ASSISTANT_ID')

        if create_new or not memory_id:
            memory = self.client.beta.assistants.create(
                name="Memory and Personality Analyzer",
                instructions="""You are an expert at analyzing user behavior and content performance.
                Your tasks are:
                1. Analyze user comments to update their personality profile
                2. Analyze post performance to optimize content creation guidelines""",
                model="gpt-4"
            )

            with open('.env', 'a') as f:
                f.write(f'\nMEMORY_ASSISTANT_ID={memory.id}')
            load_dotenv()
            return memory
        else:
            try:
                return self.client.beta.assistants.retrieve(memory_id)
            except Exception:
                return self._create_memory_assistant(create_new=True)

    def _create_thread(self):
        """Create a new thread for conversation"""
        return self.client.beta.threads.create()

    def update_user_personality(self, user_id: str, comment_text: str, post_id: str) -> dict:
        """Update user personality based on new comment"""
        current_profile = self.users_data.get(user_id, {
            "personality": {
                "sentiment": "neutral",
                "common_topics": [],
                "engagement_level": "low"
            }
        })

        prompt = f"""
        Analyze this new comment and update the user's personality profile.

        Current Profile: {json.dumps(current_profile)}
        New Comment: {comment_text}
        Post Context: {json.dumps(self.posts_data.get(post_id))}

        IMPORTANT: Respond ONLY with a JSON object in this exact format, no additional text:
        {{
            "personality": {{
                "sentiment": "<positive/negative/neutral>",
                "common_topics": ["topic1", "topic2"],
                "engagement_level": "<high/medium/low>"
            }}
        }}
        """

        self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=prompt
        )

        with self.client.beta.threads.runs.stream(
            thread_id=self.thread.id,
            assistant_id=self.memory_assistant.id,
            event_handler=EventHandler(),
        ) as stream:
            stream.until_done()

        messages = self.client.beta.threads.messages.list(thread_id=self.thread.id)
        response_text = messages.data[0].content[0].text.value

        try:
            # Clean up the response text to handle potential markdown formatting
            cleaned_response = response_text.strip()
            if '```json' in cleaned_response:
                cleaned_response = cleaned_response.replace('```json', '').replace('```', '')
            updated_profile = json.loads(cleaned_response.strip())

            # Ensure the response has the correct structure
            if "personality" not in updated_profile:
                updated_profile = {
                    "personality": {
                        "sentiment": "neutral",
                        "common_topics": [],
                        "engagement_level": "low"
                    }
                }
        except Exception as e:
            print(f"Error parsing response: {e}")
            print(f"Raw response: {response_text}")
            # Provide a default profile if parsing fails
            updated_profile = {
                "personality": {
                    "sentiment": "neutral",
                    "common_topics": [],
                    "engagement_level": "low"
                }
            }

        # Update the users_data
        if user_id not in self.users_data:
            self.users_data[user_id] = {
                "engagement": {
                    "commented_posts": [],
                    "comments": []
                },
                "personality": updated_profile["personality"]
            }
        else:
            self.users_data[user_id]["personality"] = updated_profile["personality"]

        if post_id not in self.users_data[user_id]["engagement"]["commented_posts"]:
            self.users_data[user_id]["engagement"]["commented_posts"].append(post_id)

        return updated_profile

    def optimize_content_guidelines(self) -> dict:
        """Analyze post performance and update system instructions"""
        # Analyze which posts performed well and why
        high_performing_posts = []
        low_performing_posts = []

        for post_id, post_data in self.posts_data.items():
            metrics = post_data.get("metrics", {})
            # Very low thresholds for testing
            if (metrics.get("views", 0) > 10 or
                metrics.get("likes", 0) > 2 or
                metrics.get("comments", 0) > 1 or
                metrics.get("shares", 0) > 1):
                high_performing_posts.append(post_data)
            else:
                low_performing_posts.append(post_data)

        prompt = f"""
        Analyze these posts and their performance metrics to update content creation guidelines.

        High Performing Posts: {json.dumps(high_performing_posts)}
        Low Performing Posts: {json.dumps(low_performing_posts)}
        Current Instructions: {json.dumps(self.system_instructions)}

        Based on the performance analysis:
        1. What content styles/formats worked best?
        2. What headlines generated most engagement?
        3. What media types (images/videos) performed better?
        4. What topics resonated with the audience?

        IMPORTANT: Return ONLY a JSON object with updated instructions based on what worked:
        {{
            "director": {{
                "role": "content_analyzer",
                "instructions": "Detailed instructions based on high-performing content patterns"
            }},
            "writer": {{
                "role": "content_creator",
                "instructions": "Specific guidelines based on successful posts"
            }}
        }}
        """

        self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=prompt
        )

        with self.client.beta.threads.runs.stream(
            thread_id=self.thread.id,
            assistant_id=self.memory_assistant.id,
            event_handler=EventHandler(),
        ) as stream:
            stream.until_done()

        messages = self.client.beta.threads.messages.list(thread_id=self.thread.id)
        response_text = messages.data[0].content[0].text.value

        try:
            # Clean up the response text
            cleaned_response = response_text.strip()
            if '```json' in cleaned_response:
                cleaned_response = cleaned_response.split('```json')[1].split('```')[0].strip()
            elif '```' in cleaned_response:
                cleaned_response = cleaned_response.split('```')[1].strip()

            # Parse and validate the JSON
            updated_instructions = json.loads(cleaned_response)

            if not all(key in updated_instructions for key in ['director', 'writer']):
                raise ValueError("Missing required keys in response")

            # Only update if the instructions are different
            if updated_instructions != self.system_instructions:
                print("\nSystem instructions updated based on post performance analysis:")
                print(f"Analyzed {len(high_performing_posts)} high-performing posts")
                print(f"Analyzed {len(low_performing_posts)} low-performing posts")
                self.system_instructions = updated_instructions

            return updated_instructions
        except Exception as e:
            print(f"Error parsing optimization response: {e}")
            print(f"Raw response: {response_text}")
            return self.system_instructions

    def process_new_comment(self, user_id: str, comment_text: str, post_id: str):
        """Process a new comment: update user personality and optimize content if needed"""
        # Update user personality
        updated_profile = self.update_user_personality(user_id, comment_text, post_id)

        # Very low thresholds for testing
        post_metrics = self.posts_data.get(post_id, {}).get("metrics", {})
        should_optimize = (
            post_metrics.get("views", 0) > 10 or
            post_metrics.get("likes", 0) > 2 or
            post_metrics.get("comments", 0) > 1 or
            post_metrics.get("shares", 0) > 1
        )

        if should_optimize:
            updated_instructions = self.optimize_content_guidelines()
            return {
                "user_profile": updated_profile,
                "system_instructions": updated_instructions
            }

        return {
            "user_profile": updated_profile
        }
