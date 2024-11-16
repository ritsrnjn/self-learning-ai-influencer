from engagement_agent import EngagementAgent
from dotenv import load_dotenv
import os

def test_engagement_agent():
    # Load environment variables
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')

    # Sample engagement instructions
    engagement_instructions = """
    You are an engaging community manager for a memecoin project. Your role is to:
    - Create friendly, casual replies to community comments
    - Stay on-brand with meme culture and humor
    - Keep responses relevant to both the visual content and comment context
    - Maintain a positive, engaging tone
    - Keep replies concise and natural-sounding
    """

    # Initialize the agent
    agent = EngagementAgent(api_key=api_key, engagement_instructions=engagement_instructions)

    # Test the get_reply function
    try:
        reply = agent.get_reply(
            post_id="post1",
            comment_id="comment1"
        )
        print("\nGenerated Reply:", reply)
    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    test_engagement_agent()
