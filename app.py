from router import route_and_respond  # type: ignore

def main():
    print("=== LLM-Powered Prompt Router ===")
    print("Type 'exit' to quit.\n")
    
    while True:
        user_input = input("Enter your message: ")
        if user_input.lower() in ['exit', 'quit']:
            break
            
        print("\n[Routing and generating response...]")
        try:
            response = route_and_respond(user_input)
            print(f"\nAI Response:\n{response}\n")
            print("-" * 30)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
