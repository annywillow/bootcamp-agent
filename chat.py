import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

load_dotenv()

project = AIProjectClient(
    endpoint=os.environ["AZURE_AI_FOUNDRY_PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
    allow_preview=True,
)

openai_client = project.get_openai_client(
    agent_name=os.environ["AZURE_AI_FOUNDRY_AGENT_NAME"]
)

conversation = openai_client.conversations.create()

print("Bootcamp assistant ready.")

while True:
    question = input("\nAsk the bootcamp assistant (or 'quit'): ")

    if question.lower() in {"quit", "exit"}:
        break

    response = openai_client.responses.create(
        conversation=conversation.id,
        input=question,
    )

    print(f"\nAssistant: {response.output_text}")