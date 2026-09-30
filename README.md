# MMAUG Bootcamp Assistant

## Microsoft Foundry Overview and Single Agent Deployment

A hands-on lab for the **MMAUG 30-Day AI and DevOps Fundamentals Bootcamp**, organised by the Malta Microsoft AI User Group. Build a single prompt agent in Microsoft Foundry, configure its behaviour, and chat with it from Python or the portal.

The assistant uses a small bootcamp knowledge snapshot embedded in its instructions and **Web Search** for details the snapshot cannot confirm. Its source rules tell it to acknowledge missing information rather than invent sessions, speakers, times or links.

**Level:** Beginner  
**Estimated time:** 30–45 minutes once software and Azure resources are ready  
**Language:** Python  
**Example agent name:** `mmaug-bootcamp-agent`  
**Example model deployment:** `gpt-4.1` with **Global Standard** deployment

## Learning objectives

By the end of this lab, you will be able to:

1. Explain the roles of a Foundry resource, project, model deployment, prompt agent and tool.
2. Set up a Python virtual environment in VS Code.
3. Authenticate to Azure using Microsoft Entra ID and `DefaultAzureCredential`.
4. Define agent instructions using a small programme knowledge snapshot.
5. Configure Web Search for missing or current information.
6. Create an agent version with `agent.py` and inspect it in Foundry.
7. Use `chat.py` to ask questions and follow-ups in one conversation.
8. Evaluate source use, accuracy and handling of unknown information.
9. Clean up lab resources and understand which actions incur charges.

## How the lab works

| Component | Purpose |
| --- | --- |
| Foundry resource | Azure resource providing access to Foundry services. |
| Project | Workspace containing the agent and its configuration. |
| Model deployment | Deployed model used to generate responses. |
| Prompt agent | Saved, versioned definition containing the model, instructions and tools. |
| Web Search | Looks up information on the public web when the model calls the tool. |
| Conversation | Holds the context used for follow-up questions. |

There are **two separate Python scripts**:

- **`agent.py`** reads `data/Knowledge_txt.txt`, adds the text to the instructions, configures `WebSearchTool()`, creates an agent version and prints its name and version. It then exits.
- **`chat.py`** connects to the existing named agent, creates a conversation, and runs an interactive question-and-answer loop. It does not create another agent version.

The knowledge file is embedded in the agent's saved instructions. It is not uploaded to File Search, and this lab does not create a vector database. `chat.py` therefore does not need to read the knowledge file again.

The instructions prioritise the snapshot for programme facts and request web search for details such as daily session titles, speakers, times and links. These are intended behaviours to check during testing: enabling a tool does not force the agent to use it for every question.

## Prerequisites

### Azure access

- An Azure subscription and access to a Microsoft Foundry resource and project.
- A deployed model supported by the prompt-agent and Web Search features in your chosen region. This lab uses GPT-4.1.
- Permission to create and run agents, such as the **Foundry User** role on the project, with any required resource access. Some interfaces still show the previous name, **Azure AI User**. See [Foundry role assignments](https://learn.microsoft.com/en-us/azure/foundry/concepts/rbac-foundry).
- Web Search permitted by your organisation's policies.

Creating resources, model deployments or role assignments can require additional permissions. Use a dedicated lab project where possible.

### Local software

- [Python 3.10 or later](https://www.python.org/downloads/) — the working Windows environment for this lab used Python 3.13.9.
- [VS Code](https://code.visualstudio.com/) with the Python extension. The Python Environments extension helps select and activate the virtual environment.
- [Git](https://git-scm.com/downloads).
- [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli).

Check your installations in a terminal:

```powershell
python --version
git --version
az version
```

On macOS/Linux, use `python3` if `python` is unavailable.

**Costs:** Asking the assistant questions consumes model tokens, and Web Search calls can incur separate charges. Review the [cleanup and costs](#cleanup-and-costs) section before starting.

## Files and learner templates

| File | Purpose |
| --- | --- |
| [agent.py](agent.py) | Creates or updates the saved agent by creating a version. |
| [chat.py](chat.py) | Chats with the existing agent using a conversation. |
| [data/Knowledge_txt.txt](data/Knowledge_txt.txt) | Small programme knowledge snapshot dated 29 September 2026. |
| [README.md](README.md) | Lab instructions and learning objectives. |
| [.gitignore](.gitignore) | Excludes local environment settings, the virtual environment and generated files. |
| `requirements.txt` | Dependency file; a starting template is provided in step 4 if absent. |
| `.env.example` | Configuration template; create it using step 6 if absent. |
| `.env` | Your local configuration, created from the template and excluded from Git. |

Keep `agent.py` and `chat.py` as separate files. Run all lab commands from the repository root so the relative knowledge-file path resolves correctly.

## Step-by-step lab

### 1. Prepare Foundry

1. Sign in to the [Foundry portal](https://ai.azure.com/).
2. Select your subscription, Foundry resource and project.
3. Open the model deployment area. Deploy GPT-4.1 or confirm an existing suitable deployment is available.
4. For this example, use **Global Standard** and record the exact **deployment name**. It may differ from the model's product name.
5. Copy the **project endpoint** from the project's overview or welcome page.
6. Confirm your project access and Web Search availability.

The endpoint should have this format:

```text
https://YOUR-RESOURCE.services.ai.azure.com/api/projects/YOUR-PROJECT
```

This lab uses the versioned prompt-agent approach with **Azure AI Projects 2.x**. Do not mix it with classic 1.x agent examples. Portal labels can vary between experiences.

### 2. Clone and open the repository

```powershell
git clone https://github.com/annywillow/bootcamp-agent.git
cd bootcamp-agent
code .
```

If using a fork, substitute its URL. If the folder is already on your computer, open it in VS Code instead of cloning again.

### 3. Create and activate `myenv`

**Windows PowerShell:**

```powershell
python -m venv myenv
.\myenv\Scripts\Activate.ps1
```

Skip creation if `myenv` already exists. After activation, the prompt usually starts with `(myenv)`.

If PowerShell blocks activation on your personal computer, this user-scoped setting persists across sessions:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
.\myenv\Scripts\Activate.ps1
```

Organisation policies can override this setting. If activation remains blocked, use the virtual environment's Python directly:

```powershell
.\myenv\Scripts\python.exe -m pip --version
```

For subsequent commands, replace `python` with `.\myenv\Scripts\python.exe` until activation works.

**macOS/Linux:**

```bash
python3 -m venv myenv
source myenv/bin/activate
```

**Configure VS Code:**

1. Press **Ctrl+Shift+P** and select **Python: Select Interpreter**.
2. Choose `myenv`. If missing, enter the path to `myenv/Scripts/python.exe` on Windows or `myenv/bin/python` on macOS/Linux.
3. Close the old terminal and open a new one. With automatic activation enabled, VS Code activates the selected environment.
4. Check the interpreter:

```powershell
python -c "import sys; print(sys.executable)"
```

On Windows, the result should end in `myenv\Scripts\python.exe`. If it points to Anaconda or another installation, switch environments before installing packages or running scripts. You can also use **Environment Managers → myenv → Open in Terminal**.

### 4. Install dependencies

If `requirements.txt` is absent, create it with this starting template:

```text
azure-ai-projects>=2.3.0,<3.0.0
azure-identity
python-dotenv
```

With `myenv` active, run:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

`azure-ai-projects` supplies the project SDK and its OpenAI client dependency. `azure-identity` supplies authentication. The package for `from dotenv import load_dotenv` is **`python-dotenv`**; do not try to install a package named `python`.

The template follows the SDK generation used by the lab. Use pinned versions from a validated lab release when available, and retest the scripts after upgrading dependencies.

### 5. Sign in to Azure

```powershell
az login
```

Complete the browser/account sign-in and any multi-factor authentication, then select the subscription that contains your project. To select it explicitly:

```powershell
az account set --subscription "YOUR-SUBSCRIPTION-ID"
```

If sign-in fails for the wrong tenant or requires a fresh interactive login:

```powershell
az login --tenant "YOUR-TENANT-ID" --use-device-code
```

Follow the displayed browser instructions and complete MFA. `DefaultAzureCredential` can use this Azure CLI sign-in, but your identity must still have project permissions.

### 6. Configure `.env`

If `.env.example` is absent, create it with these placeholders:

```dotenv
AZURE_AI_FOUNDRY_PROJECT_ENDPOINT=https://YOUR-RESOURCE.services.ai.azure.com/api/projects/YOUR-PROJECT
AZURE_AI_FOUNDRY_MODEL_DEPLOYMENT_NAME=YOUR-DEPLOYMENT-NAME
AZURE_AI_FOUNDRY_AGENT_NAME=mmaug-bootcamp-agent
```

Copy the template locally:

**Windows PowerShell:**

```powershell
Copy-Item .env.example .env
```

**macOS/Linux:**

```bash
cp .env.example .env
```

Replace the endpoint and deployment placeholders in `.env`, then save it. For a deployment actually named `gpt-4.1`, set:

```dotenv
AZURE_AI_FOUNDRY_MODEL_DEPLOYMENT_NAME=gpt-4.1
```

| Variable | Used by |
| --- | --- |
| `AZURE_AI_FOUNDRY_PROJECT_ENDPOINT` | Both scripts to connect to the project. |
| `AZURE_AI_FOUNDRY_MODEL_DEPLOYMENT_NAME` | `agent.py` to configure the agent's model deployment. |
| `AZURE_AI_FOUNDRY_AGENT_NAME` | Both scripts to identify the same agent. |

Agent names must start and end with an alphanumeric character, may contain hyphens in the middle, and must not exceed 63 characters. Use `mmaug-bootcamp-agent`, without spaces or underscores.

Both scripts call `load_dotenv()`. VS Code terminal injection through `python.terminal.useEnvFile` is not required for these scripts. The keys must match the code exactly; the older names `PROJECT_ENDPOINT`, `MODEL_DEPLOYMENT` and `AGENT_NAME` will not satisfy it.

Keep your existing `.gitignore`, ensuring these entries are present:

```gitignore
.env
myenv/
.venv/
__pycache__/
*.pyc
```

Commit `.env.example` with placeholders. Keep your actual `.env` local.

### 7. Review the knowledge and instructions

Open `data/Knowledge_txt.txt`. Check its source URL, capture date and programme facts.

Then review `agent.py`:

- `AIProjectClient` connects to the project.
- `DefaultAzureCredential` provides authentication.
- `KNOWLEDGE` contains the file's text.
- `INSTRUCTIONS` defines the assistant's role, source rules and boundaries.
- `PromptAgentDefinition` combines the deployed model, instructions and `WebSearchTool()`.
- `project.agents.create_version(...)` saves an agent version.

The current source rules prioritise the snapshot, require web search for daily details, prohibit invented answers, and distinguish the certificate-review deadline from a guarantee of certification.

The supplied clients include `allow_preview=True`. Retain it for the named-agent `get_openai_client(agent_name=...)` route used in `chat.py`.

### 8. Create the agent

```powershell
python agent.py
```

Expected output resembles:

```text
Created agent version: mmaug-bootcamp-agent v1
```

The version number can differ. The script finishes and returns to the shell; this is expected. It does not ask for a question.

Run `agent.py` when initially creating the agent or after changing the knowledge file, instructions, tools or configured model. Rerunning it creates an agent version; ordinary chat does not require it. Changing the local knowledge file or model setting alone does not update the saved agent until you rerun this script.

### 9. Start the chat

```powershell
python chat.py
```

You should see:

```text
Bootcamp assistant ready.

Ask the bootcamp assistant (or 'quit'):
```

Enter a question at that prompt, for example:

```text
What will I learn in Week 2?
```

Ask a follow-up in the same session:

```text
Explain the first topic in simpler terms.
```

The chat creates one conversation before the loop and sends its ID with every question:

```python
conversation = openai_client.conversations.create()

response = openai_client.responses.create(
    conversation=conversation.id,
    input=question,
)
```

This provides context for follow-ups during that run. Restarting `chat.py` creates a new conversation. The script does not save an ID for resuming an earlier chat.

Type `quit` or `exit` to leave the loop. Enter it without surrounding spaces; the supplied code uses `question.lower()` without `.strip()`. After returning to the `PS ...>` shell prompt, run `python chat.py` again before asking more questions. A question entered directly at the shell prompt is treated as a command.

### 10. Inspect the agent in Foundry

1. Open the same Foundry project and select **Agents**.
2. Select the name configured in `.env` and inspect the version created by `agent.py`.
3. Check the model deployment, saved instructions and Web Search tool.
4. Test questions in the playground.
5. Inspect available tool-call details and citations for web questions. A response saying it searched is not sufficient evidence that a search occurred.

The current terminal client prints `response.output_text`; it does not separately print structured tool-call or citation metadata. Use the portal's available diagnostics when checking those details.

## Test questions and success criteria

Compare answers with your actual knowledge file and any cited official sources. Do not grade an answer against a guessed programme schedule.

| Question | What to check |
| --- | --- |
| What will I learn in Week 1? | Matches the topics recorded in the snapshot. |
| What will I learn in Week 3? | Covers the snapshot's Week 3 topics without inventing sessions. |
| Explain the first topic more simply. | Uses the previous answer's context within the same chat session. |
| How much time should I spend each day? | Reports the estimate in the knowledge file or acknowledges that it is missing. |
| Does submitting the capstone guarantee a certificate? | Explains that submission is for review; does not invent eligibility rules. |
| Search the web for the speaker on 12 October 2026 and cite the official source. | Uses a search where available; provides verifiable evidence or acknowledges that it cannot confirm the speaker. |
| What is the private WhatsApp group link? | Does not invent an invitation or claim access to private information. |

**Refinement exercise:** Change one instruction, such as the preferred answer length. Rerun `agent.py`, then restart `chat.py` and compare responses to the same questions. Record the agent version and any factual or source-use failures.

## Troubleshooting

| Problem | Fix |
| --- | --- |
| `ModuleNotFoundError: No module named 'azure'` | Check `sys.executable`, activate `myenv`, and install dependencies with that Python. |
| `KeyError: 'AZURE_AI_FOUNDRY_PROJECT_ENDPOINT'` | Save `.env` in the project folder with the exact keys from step 6 and populated values. |
| VS Code says terminal environment injection is disabled | The scripts already use `load_dotenv()`. Check the file and variable names instead of assuming this warning caused a failure. |
| PowerShell says scripts are disabled | Follow step 3 or use `myenv\Scripts\python.exe` directly. |
| Anaconda appears in the traceback | The wrong Python is running. Select `myenv`, open a fresh activated terminal and verify its executable. |
| `Decompressor.decompress()` rejects `output_buffer_limit` | This lab encountered a dependency mismatch in Anaconda. Run from `myenv` first; if it persists there, update the SDK and its compression dependencies in that environment and check their compatibility. |
| Agent-name validation error | Use a name such as `mmaug-bootcamp-agent` with no spaces or underscores and no more than 63 characters. |
| `404 DeploymentNotFound` | Match the model deployment name exactly in `.env`, verify it belongs to the project's backing resource, then rerun `agent.py` and restart `chat.py`. |
| Agent not found during chat | Run `agent.py` first and ensure both scripts use the same endpoint and agent name. |
| Authentication or MFA fails | Repeat interactive Azure sign-in for the correct tenant as in step 5. |
| `401` or `403` | Check the signed-in identity and project permissions; allow time for role changes to take effect. |
| Knowledge file not found | Run `agent.py` from the repository root and check `data/Knowledge_txt.txt`, including letter case. |
| Web Search unavailable or unused | Check tool configuration, model/region support and project policy; inspect the actual tool call. |
| Chat exits immediately without a prompt | Save `chat.py` and confirm it contains the supplied interactive loop. |
| PowerShell says `what` is not recognised | Start `python chat.py` and enter questions at the assistant's prompt. |

## Cleanup and costs

### Stop the chat

Type `quit` or `exit`, or press `Ctrl+C`. This stops the local process. It does not delete the agent, model deployment, Azure resources or stored conversation.

### Keep the agent for another demonstration

The prompt-agent definition itself has no additional creation or running fee. For the base GPT-4.1 **Global Standard** deployment used here, model billing is based on input and output tokens; leaving it idle does not create an idle model-deployment charge. Web Search calls incur separate usage charges.

This does not mean the whole resource group is cost-free. Provisioned model capacity is billed while deployed, and separately provisioned services such as search or storage can have their own costs. Check [Agent Service pricing](https://azure.microsoft.com/en-us/pricing/details/foundry-agent-service/), [Azure OpenAI pricing](https://azure.microsoft.com/en-us/pricing/details/azure-openai/) and [deployment types](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/deployment-types).

### Delete the agent when finished

For this lab, manual cleanup is sufficient:

1. Open the correct project in Foundry.
2. Open **Agents** and select `mmaug-bootcamp-agent`, or your configured name.
3. Delete the intended lab agent and verify its removal.

SDK cleanup is an optional alternative. If you create `cleanup.py`, use the same environment-variable names as the working scripts. The deletion call is:

```python
project.agents.delete(
    agent_name=os.environ["AZURE_AI_FOUNDRY_AGENT_NAME"]
)
```

Here, `project` must be an authenticated `AIProjectClient` configured with `AZURE_AI_FOUNDRY_PROJECT_ENDPOINT`, as in the other scripts. You only need one deletion method. Deleting the agent does not delete its model deployment or perform full Azure-resource cleanup.

### Remove dedicated cloud resources

- Delete model deployments created only for this lab if you no longer need them.
- Check for lab-only connected resources and remove those too.
- If the whole resource group is dedicated to this lab, inspect its contents and delete it in the [Azure portal](https://portal.azure.com/). Do not delete a shared group.
- Review **Azure Cost Management + Billing** afterwards. Previously incurred charges remain, and usage reporting can be delayed.

For a dedicated lab group, the CLI alternative is:

```powershell
az group delete --name "YOUR-LAB-RESOURCE-GROUP"
```

Confirm the group name before accepting the CLI's deletion prompt. Resource-group deletion removes all resources inside it.

### Clean up locally

If the environment is active:

```powershell
deactivate
```

Delete `myenv` and the local `.env` only if you no longer need them. Local deletion does not remove cloud resources.

## Publish updates to GitHub

Save the files, open VS Code Source Control, review changes, stage the intended files, commit them, and select **Push** or **Sync Changes** for the configured repository.

Include the scripts, public knowledge file, README, `.gitignore`, and the learner templates. Exclude `.env` and `myenv/`. `.gitignore` does not untrack a file that was already committed; check the files and history on GitHub if local configuration was previously added.

## Limitations and next steps

- The snapshot is dated **29 September 2026**. It does not confirm daily speakers, times, meeting links or full certificate eligibility rules.
- Web Search can return incomplete or outdated information. Preferring `mmaug.com` in instructions is not a technical domain restriction.
- Source instructions guide behaviour but do not guarantee correctness.
- The console client has no custom retry handling and does not resume saved conversations after restarting.
- This lab creates a prompt agent and a local client; it does not publish a public chat website.
- For a larger document collection, explore File Search and evaluate retrieval quality.
- Use public programme information only. MMAUG is a community group; this demo is not an official Microsoft product.

For current programme information, visit [mmaug.com/bootcamp](https://mmaug.com/bootcamp).

## Resources

- [MMAUG Bootcamp](https://mmaug.com/bootcamp)
- [Microsoft Foundry documentation](https://learn.microsoft.com/en-us/azure/foundry/)
- [Create a prompt agent and use conversation history](https://learn.microsoft.com/en-us/azure/foundry/agents/quickstarts/prompt-agent)
- [AIProjectClient and named-agent clients](https://learn.microsoft.com/en-us/python/api/azure-ai-projects/azure.ai.projects.aiprojectclient?view=azure-python)
- [Web Search tool](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/web-search)
- [Foundry permissions](https://learn.microsoft.com/en-us/azure/foundry/concepts/rbac-foundry)
- [Python environments in VS Code](https://code.visualstudio.com/docs/python/environments)
- [Azure CLI interactive sign-in](https://learn.microsoft.com/en-us/cli/azure/authenticate-azure-cli-interactively)
- [PowerShell execution policies](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_execution_policies)
- [Agent Service pricing](https://azure.microsoft.com/en-us/pricing/details/foundry-agent-service/)
- [Azure OpenAI pricing](https://azure.microsoft.com/en-us/pricing/details/azure-openai/)

## Licence

MIT — see the repository's [LICENSE](LICENSE).
