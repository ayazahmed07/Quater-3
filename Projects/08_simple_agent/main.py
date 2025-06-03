import os
from dotenv import load_dotenv
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    print("OPENAI_API_KEY is not set, skipping trace export")
else:
    print("API Key loaded successfully!")

provider = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=provider,
)

agent = Agent(
    name="Greting Agent",
    instructions="You are every thing, just answer every questions and skip nothing..",
    model=model
)

user_question = input("Please enter your question")

result = Runner.run_sync(agent, user_question)

print(result.final_output)