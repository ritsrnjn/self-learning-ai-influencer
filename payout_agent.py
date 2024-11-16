from cdp_agentkit_core import Agent
from cdp_agentkit_core.actions.transfer import transfer, TransferInput

class PayoutAgent(Agent):
    def __init__(self, config=None):
        super().__init__(config)
        self.transfer = transfer

    async def process(self, input_data):
        """
        Process the input and execute payout via TestTransfer

        Args:
            input_data: Dictionary containing payout details
                Expected format:
                {
                    "recipient": str,
                    "amount": float,
                    "currency": str
                }

        Returns:
            dict: Result of the payout operation
        """
        try:
            # Validate input
            if not all(key in input_data for key in ["recipient", "amount", "currency"]):
                raise ValueError("Missing required fields: recipient, amount, currency")

            # Execute transfer
            transfer_result = await self.transfer(
                recipient=input_data["recipient"],
                amount=input_data["amount"],
                currency=input_data["currency"]
            )

            return {
                "status": "success",
                "transaction_id": transfer_result.get("transaction_id"),
                "details": transfer_result
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    async def cleanup(self):
        """Cleanup any resources if needed"""
        await self.transfer_client.close()
