"""Create a simple Foundry agent (knowledge in instructions + Web Search)."""
import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, WebSearchTool

load_dotenv()


project = AIProjectClient(
    endpoint=os.environ["AZURE_AI_FOUNDRY_PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
    allow_preview=True,
)
# The knowledge snapshot is small, so we load it straight into the instructions.
with open("data/Knowledge_txt.txt", encoding="utf-8") as f:
    KNOWLEDGE = f.read()

INSTRUCTIONS = f"""You are the MMAUG Bootcamp Assistant for the 30-Day AI and DevOps
Fundamentals Bootcamp run by the Malta Microsoft AI User Group.

Source rules:
1. Use the KNOWLEDGE section below FIRST for programme facts: dates, weekly
   topics, audience, capstone deadline, registration status.
2. It is a snapshot dated 29 September 2026. It does NOT confirm daily session
   titles, speakers, times or meeting links. For those, use web search, prefer
   mmaug.com, and say the answer came from the live web.
3. If neither source has the answer, say so plainly. Never invent sessions,
   speakers, times or links.
4. The 14 November 2026 deadline is for submission for certificate review, not
   a guarantee of a certificate. Eligibility criteria are not in the knowledge.
5. Keep answers short, friendly and beginner-appropriate.

KNOWLEDGE:
{KNOWLEDGE}"""

agent = project.agents.create_version(
    agent_name=os.environ["AZURE_AI_FOUNDRY_AGENT_NAME"],
    definition=PromptAgentDefinition(
        model=os.environ["AZURE_AI_FOUNDRY_MODEL_DEPLOYMENT_NAME"],
        instructions=INSTRUCTIONS,
        tools=[WebSearchTool()],
    ),
)
print(f"Created agent version: {agent.name} v{agent.version}")

