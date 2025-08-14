from openai import OpenAI

def main():
    # Connect to the LLAMPHouse server
    client = OpenAI(api_key="dummy", base_url="http://127.0.0.1:8000") # authentication is not enabled on the server, but the api_key is still required
    
    # Create new thread
    empty_thread = client.beta.threads.create()
    print(f"Created thread: {empty_thread.id}")

    # Add message to thread
    client.beta.threads.messages.create(empty_thread.id, role="user", content="This is my first message")
    client.beta.threads.messages.create(empty_thread.id, role="user", content="How are you")

    # Create new run in specific thread & assistant
    new_run =client.beta.threads.runs.create_and_poll(assistant_id="my-assistant", thread_id=empty_thread.id, temperature=1)
    print(f"Run finished: {new_run}")

if __name__ == "__main__":
    main()
