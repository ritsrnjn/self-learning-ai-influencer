from chat_agent import ChatAgent

def main():
    # Initialize chat agent
    try:
        chat_agent = ChatAgent()
    except ValueError as e:
        print(f"Error: {e}")
        return

    print("Brett Memecoin Chat Bot (type 'quit' to exit)")
    print("-" * 50)

    while True:
        # Get user input
        user_message = input("\nYou > ").strip()

        # Check for exit command
        if user_message.lower() in ['quit', 'exit', 'bye']:
            print("\nGoodbye! 👋")
            break

        if user_message:
            try:
                # Get response from chat agent
                response = chat_agent.chat(user_message)
                print(f"\nBrett Bot > {response}")
            except Exception as e:
                print(f"\nError: {str(e)}")

if __name__ == "__main__":
    main()
