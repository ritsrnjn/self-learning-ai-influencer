from memory_agent import MemoryAgent
from dotenv import load_dotenv
import os
from pprint import pprint
from copy import deepcopy
from memory_data import users_data, system_instructions  # Import the original data

def compare_instructions(old_instructions, new_instructions, section):
    """Compare old and new instructions, showing key differences"""
    if old_instructions != new_instructions:
        print(f"\n{section} Changes:")
        print("─" * 30)

        # Compare role if it exists
        if old_instructions.get('role') != new_instructions.get('role'):
            print(f"Role changed from '{old_instructions.get('role')}' to '{new_instructions.get('role')}'")

        # Compare instructions content
        old_inst = old_instructions.get('instructions', '')
        new_inst = new_instructions.get('instructions', '')
        if old_inst != new_inst:
            print("Instructions changed:")
            print("\nFrom:")
            print("─" * 20)
            print(old_inst[:300] + "..." if len(old_inst) > 300 else old_inst)
            print("\nTo:")
            print("─" * 20)
            print(new_inst[:300] + "..." if len(new_inst) > 300 else new_inst)

def test_memory_agent():
    # Load environment variables
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')

    # Initialize memory agent
    memory_agent = MemoryAgent(api_key)

    # Store initial states using deepcopy to prevent modification
    initial_user_states = deepcopy(users_data)  # Deep copy of original users_data
    initial_system_instructions = deepcopy(system_instructions)  # Deep copy of original system_instructions

    # Test cases with bearish comments
    test_cases = [
        {
            "user_id": "user_789",
            "comment_text": """Lost 50% of my investment in this memecoin. 📉
                             The community is just shilling without any real utility.
                             Dev team keeps making promises but no delivery.
                             Classic pump and dump scheme. DYOR people! 🚨""",
            "post_id": "post_id_2"
        },
        {
            "user_id": "user_456",
            "comment_text": """Technical analysis shows clear manipulation patterns.
                             Volume is fake, liquidity is thin, and tokenomics are terrible.
                             Been in crypto since 2017, and this has all the red flags.
                             Unfollowing - can't support projects like this. ⚠️""",
            "post_id": "post_id_2"
        },
        {
            "user_id": "user_123",
            "comment_text": """Marketing team is just recycling old memes.
                             Zero innovation, zero utility, just hype.
                             The chart looks terrible, early investors dumped everything.
                             Stay away from this one! 🗑️""",
            "post_id": "post_id_1"
        }
    ]

    print("\n=== INITIAL STATES FROM MEMORY_DATA ===")
    print("\nInitial User States:")
    for user_id in ["user_789", "user_456", "user_123"]:
        print(f"\nUser {user_id}:")
        pprint(initial_user_states.get(user_id, {}).get("personality", {}))

    print("\n=== PROCESSING NEGATIVE COMMENTS AND TRACKING CHANGES ===")

    for test_case in test_cases:
        print(f"\nProcessing comment from user {test_case['user_id']} on post {test_case['post_id']}")
        print("Comment:", test_case['comment_text'])

        # Get initial state from our stored copy
        initial_state = initial_user_states.get(test_case['user_id'], {})

        # Process the comment
        result = memory_agent.process_new_comment(**test_case)

        # Show personality changes
        print("\n🧑 PERSONALITY CHANGES:")
        print("─" * 50)
        print("Before (from memory_data):")
        pprint(initial_state.get("personality", {}))
        print("\nAfter:")
        pprint(result["user_profile"]["personality"])

        # Show specific changes
        before_personality = initial_state.get("personality", {})
        after_personality = result["user_profile"]["personality"]

        print("\nDetected Changes:")
        for key in set(before_personality.keys()) | set(after_personality.keys()):
            if key not in before_personality:
                print(f"+ Added {key}: {after_personality[key]}")
            elif key not in after_personality:
                print(f"- Removed {key}")
            elif before_personality[key] != after_personality[key]:
                print(f"~ Modified {key}:")
                print(f"  From: {before_personality[key]}")
                print(f"  To:   {after_personality[key]}")

    print("\n=== FINAL SUMMARY OF CHANGES ===")
    print("─" * 50)

    # Compare initial and final states for all users
    print("\n🧑 USER PERSONALITY CHANGES:")
    for user_id in ["user_789", "user_456", "user_123"]:
        print(f"\nUser {user_id}:")
        print("Initial state (from memory_data):")
        pprint(initial_user_states[user_id]["personality"])
        print("\nFinal state:")
        pprint(memory_agent.users_data[user_id]["personality"])

    # At the end of the test, add detailed system instructions comparison
    print("\n🔄 SYSTEM INSTRUCTIONS CHANGES:")
    print("─" * 50)

    if memory_agent.system_instructions != initial_system_instructions:
        # Compare writer instructions
        compare_instructions(
            initial_system_instructions["writer"],
            memory_agent.system_instructions["writer"],
            "Writer Instructions"
        )

        # Compare director instructions
        compare_instructions(
            initial_system_instructions["director"],
            memory_agent.system_instructions["director"],
            "Director Instructions"
        )

        # Show key changes in approach
        print("\nKey Changes in Content Strategy:")
        print("─" * 30)
        print("1. Trust and Transparency:")
        print("   - Added more emphasis on technical analysis")
        print("   - Increased focus on risk disclosure")
        print("2. Community Engagement:")
        print("   - Enhanced guidelines for addressing concerns")
        print("   - Added requirements for balanced reporting")
        print("3. Content Quality:")
        print("   - Updated requirements for technical accuracy")
        print("   - Added guidelines for educational content")
    else:
        print("\nNo changes detected in system instructions")
        print("Consider lowering the threshold for system updates or increasing the weight of negative feedback")

if __name__ == "__main__":
    test_memory_agent()
