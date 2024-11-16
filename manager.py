
import os
import time

from dotenv import load_dotenv
from content_agent import ContentAgent
from engagement_agent import EngagementAgent
from agent_instructions import WRITER_INSTRUCTIONS, ENGAGEMENT_INSTRUCTIONS
from data import posts_data, comments_data
from instagram import create_new_post, reply_to_comment
from web3_agent import Web3Assistant
from storage import save_update

import queue
import json
from datetime import datetime


updates_queue = queue.Queue()

def add_update(action_type, details):
    """Add a new update to the queue"""
    update = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'action_type': action_type,
        'details': details
    }
    updates_queue.put(update)

def event_stream():
    """Generator function for SSE"""
    while True:
        try:
            # Get update from queue (non-blocking)
            update = updates_queue.get_nowait()
            yield f"data: {json.dumps(update)}\n\n"
        except queue.Empty:
            # If queue is empty, yield an empty string to keep connection alive
            yield ": heartbeat\n\n"


def create_content_to_post():
    # Load environment variables
    load_dotenv()

    # Initialize the agent
    agent = ContentAgent(
        api_key=os.getenv('OPENAI_API_KEY'),
        writer_instructions=WRITER_INSTRUCTIONS
    )

    # Generate content
    token_doc_file = "./BASED BRETT.pdf"  # Replace with actual path
    prompt = "Brett coin's latest price movement"

    save_update("INITIATING CONTENT CREATION", "Creating content about " + prompt)

    new_post = agent.generate_content(prompt, token_doc_file)

    data = {
        "headline": new_post["headline"],
        "generated_image_url": new_post["generated_image_url"]
    }

    save_update("CONTENT CREATED", f"New post generated with caption: {new_post['headline']}")

    # convert current timestamp to string to use as postId
    post_id = "post" + str(int(time.time()))
    posts_data[post_id] = {
        "headline": new_post["headline"],
        "image_url": new_post["generated_image_url"]
    }

    print(f"New post generated: {new_post}")
    return data


def reply_to_comments(data):
    # Load environment variables
    load_dotenv()

    engagement_agent = EngagementAgent(
        api_key=os.getenv('OPENAI_API_KEY'),
        engagement_instructions=ENGAGEMENT_INSTRUCTIONS
    )

    comment = data['comment']
    headline = data['headline']
    image_url = data['image_url']

    save_update("REPLYING TO COMMENT", f"Replying to comment: {comment}")

    reply_of_comment = engagement_agent.get_reply(headline, comment, image_url)

    save_update("REPLY GENERATED", f"Reply generated: {reply_of_comment}")
    return reply_of_comment




def agent_created(name, symbol, supply):
    save_update("INITIATING WEB3 AGENT CREATION", "Creating agent which will handle web3 trasactions")

    assistant = Web3Assistant()

    # Example usage
    assistant.create_memecoin(name, symbol, supply)

    save_update("MEMECOIN CREATED", "Meme coin created with name: " + name + " and symbol: " + symbol)


    # addresses = [
    #     "0xA50D250Ba7FDf522008dF7300F3B9230bDbbfffa",
    #     "0xC4a1F85DeEe4407DF9d88F697a7B496950dc18F6"
    # ]
    # save_update("AIRDROP TOKENS INITIATED", "Airdropping tokens to addresses from the following list: " + str(addresses))

    # assistant.airdrop_tokens(addresses, "0.0001")

    # save_update("AIRDROP TOKENS COMPLETED", "Airdropping tokens completed")

def transfer_tokens(data):

    address = data['address']
    amount = data['amount']
    addresses = [address]

    save_update("TRANSFER TOKENS INITIATED", "Transferring tokens to address: " + address)
    assistant = Web3Assistant()
    assistant.create_memecoin("Brett", "BRETT", 34343)

    assistant.airdrop_tokens(addresses, str(amount))
    # add_update("TRANSFER TOKENS COMPLETED", "Transfer completed")
    save_update("TRANSFER TOKENS COMPLETED", "Transfer completed")








