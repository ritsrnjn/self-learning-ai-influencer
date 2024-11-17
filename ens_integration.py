from dataclasses import dataclass
from typing import Optional
import json

@dataclass
class ENSProfile:
    """Represents an ENS profile for an AI agent"""
    name: str
    address: str
    avatar_url: Optional[str] = None
    description: Optional[str] = None
    social_links: dict = None

class AIAgentENS:
    def __init__(self, agent_name: str):
        self.agent_name = f"{agent_name}.eth"
        self.profile = self._create_ens_profile()

    def _create_ens_profile(self) -> ENSProfile:
        """Creates a mock ENS profile for the AI agent"""
        return ENSProfile(
            name=self.agent_name,
            address="0xAI" + "0" * 38,  # Mock Ethereum address
            avatar_url="ipfs://QmAIagent123456789",
            description="AI Assistant powered by Advanced Language Models",
            social_links={
                "twitter": "ai_assistant",
                "github": "ai-assistant",
                "discord": "ai_assistant#1234"
            }
        )

    def display_profile(self) -> None:
        """Displays the ENS profile information"""
        print(f"\n=== {self.agent_name} Profile ===")
        print(f"Address: {self.profile.address}")
        print(f"Avatar: {self.profile.avatar_url}")
        print(f"Description: {self.profile.description}")
        print("\nSocial Links:")
        for platform, handle in self.profile.social_links.items():
            print(f"- {platform}: {handle}")

    def to_json(self) -> str:
        """Converts the ENS profile to JSON format"""
        return json.dumps({
            "name": self.profile.name,
            "address": self.profile.address,
            "avatar": self.profile.avatar_url,
            "description": self.profile.description,
            "social": self.profile.social_links
        }, indent=2)

# Example usage
if __name__ == "__main__":
    # Create an ENS profile for an AI agent
    ai_agent = AIAgentENS("claude")

    # Display the profile
    ai_agent.display_profile()

    # Get JSON representation
    print("\nJSON Format:")
    print(ai_agent.to_json())
