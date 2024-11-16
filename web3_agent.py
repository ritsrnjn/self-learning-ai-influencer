from openai import OpenAI, AssistantEventHandler
from typing_extensions import override
from dotenv import load_dotenv
from chatbot import initialize_agent
from langchain_core.messages import HumanMessage
import os
import time
from storage import save_update

class EventHandler(AssistantEventHandler):
    @override
    def on_text_created(self, text) -> None:
        print(f"\nassistant > ", end="", flush=True)

    @override
    def on_text_delta(self, delta, snapshot):
        print(delta.value, end="", flush=True)

class Web3Assistant:
    def __init__(self):
        load_dotenv()
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.chatbot_address = "0x3A1a13863f009902B13AEd3AC09bd06a74c754b7"
        self.assistant = self._create_assistant()
        self.thread = self._create_thread()
        self.agent_executor, self.config = initialize_agent()

    def _create_assistant(self, create_new=False):
        """Create or retrieve Web3 assistant"""
        assistant_id = os.getenv('WEB3_ASSISTANT_ID')

        if create_new or not assistant_id:
            assistant = self.client.beta.assistants.create(
                name="Web3 Transaction Assistant",
                instructions="""You are a Web3 assistant that helps craft messages for blockchain ai agent.
                You understand how to format messages for token deployments, airdrops, and faucet requests.
                When the chatbot indicates insufficient funds, you know to request ETH from the faucet.
                You work with Base Sepolia network.""",
                model="gpt-4",
            )

            with open('.env', 'a') as f:
                f.write(f'\nWEB3_ASSISTANT_ID={assistant.id}')
            return assistant
        else:
            try:
                return self.client.beta.assistants.retrieve(assistant_id)
            except Exception:
                return self._create_assistant(create_new=True)

    def _create_thread(self):
        return self.client.beta.threads.create()

    def execute_transaction(self, message):
        """Execute transaction through chatbot and handle responses"""
        print(f"\nExecuting transaction: {message}")
        response = None

        for chunk in self.agent_executor.stream(
            {"messages": [HumanMessage(content=message)]},
            self.config
        ):
            if "agent" in chunk:
                response = chunk["agent"]["messages"][0].content
                print(response)

                # Check for insufficient funds
                if "insufficient funds" in response.lower():
                    print("Detected insufficient funds. Requesting from faucet...")
                    self.request_faucet()
                    # Retry original transaction
                    return self.execute_transaction(message)

            elif "tools" in chunk:
                print(chunk["tools"]["messages"][0].content)

        return response  # Return the final response

    def request_faucet(self):
        """Request ETH from faucet"""
        print("\n💧 Requesting ETH from faucet...")
        faucet_message = f"request eth from faucet for address {self.chatbot_address}"
        self.execute_transaction(faucet_message)
        print("⏳ Waiting for faucet transaction to complete...")
        time.sleep(15)

    def create_memecoin(self, name, symbol, supply):
        """Create a new memecoin"""
        prompt = f"""deploy a memecoin with:
        Name: {name}
        Symbol: {symbol}
        Supply: {supply}
        Network: Base Sepolia"""

        print("\n🤖 Assistant > memecoin deployment...")
        print(f"User > {prompt}")

        message = self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=prompt
        )

        run = self.client.beta.threads.runs.create(
            thread_id=self.thread.id,
            assistant_id=self.assistant.id
        )

        print("⏳ Waiting for assistant response...")
        while True:
            run_status = self.client.beta.threads.runs.retrieve(
                thread_id=self.thread.id,
                run_id=run.id
            )
            if run_status.status == 'completed':
                break
            elif run_status.status == 'failed':
                raise Exception("Assistant run failed")
            time.sleep(1)

        messages = self.client.beta.threads.messages.list(
            thread_id=self.thread.id
        )
        deploy_message = messages.data[0].content[0].text.value
        print(f"🤖 Assistant > {deploy_message}\n")

        print("📝 Executing transaction through chatbot...")
        response = self.execute_transaction(deploy_message)

        # Extract transaction link from response using string manipulation
        # if "https://sepolia.basescan.org" in response:
        #     tx_link = response.split("Transaction link:")[1].strip()
        #     save_update("TOKEN DEPLOYMENT COMPLETED",
        #                f"Token {name} ({symbol}) deployed successfully. "
        #                f"Transaction: {tx_link}")

    def airdrop_tokens(self, addresses, amount):
        """Airdrop tokens to multiple addresses"""
        for idx, address in enumerate(addresses, 1):
            print(f"\n🔄 Processing transfer {idx}/{len(addresses)}")
            prompt = f"send {amount} ETH to {address}"

            print(f"User > {prompt}")

            message = self.client.beta.threads.messages.create(
                thread_id=self.thread.id,
                role="user",
                content=prompt
            )

            run = self.client.beta.threads.runs.create(
                thread_id=self.thread.id,
                assistant_id=self.assistant.id
            )

            print("⏳ Waiting for assistant response...")
            while True:
                run_status = self.client.beta.threads.runs.retrieve(
                    thread_id=self.thread.id,
                    run_id=run.id
                )
                if run_status.status == 'completed':
                    break
                elif run_status.status == 'failed':
                    raise Exception("Assistant run failed")
                time.sleep(1)

            messages = self.client.beta.threads.messages.list(
                thread_id=self.thread.id
            )
            transfer_message = messages.data[0].content[0].text.value
            print(f"🤖 Assistant > {transfer_message}\n")

            print("📝 Executing transaction through chatbot...")
            response = self.execute_transaction(transfer_message)

            # Extract transaction link from response
            if "https://sepolia.basescan.org" in response:
                # try:
                #     tx_link = response.split("https://sepolia.basescan.org")[1].strip()
                #     save_update("TOKEN TRANSFER COMPLETED",
                #                 f"Transferred {amount} ETH to {address}. "
                #                 f"Transaction: {tx_link}")
                # except Exception as e:
                    save_update("TOKEN TRANSFER DETAILS", response)

            if idx < len(addresses):
                print(f"⏳ Waiting 10 seconds before next transfer...")
                time.sleep(10)

