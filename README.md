# MMAUG Bootcamp Assistant

## Microsoft Foundry Overview and Single Agent Deployment

A hands-on lab for the **MMAUG 30-Day AI and DevOps Fundamentals Bootcamp**, organised by the Malta Microsoft AI User Group. Build a single AI agent in Microsoft Foundry that helps learners understand the bootcamp curriculum and programme information.

The assistant uses a small knowledge snapshot embedded in its instructions and **Web Search** for information the snapshot cannot confirm. Its instructions require it to identify its sources and acknowledge missing information rather than invent an answer.

**Level:** Beginner  
**Estimated time:** 30–45 minutes once Azure resources and software are ready  
**Language:** Python  
**Agent name:** `mmaug-bootcamp-assistant`

## Learning objectives

By the end of this lab, you will be able to:

1. Explain how Foundry resources, projects, model deployments, agents, and tools fit together.
2. Configure a Python development environment in VS Code.
3. Authenticate to Azure using Microsoft Entra ID without embedding API keys in code.
4. Write agent instructions that define its role, knowledge sources, and limits.
5. Add Web Search to look up information missing from a local knowledge snapshot.
6. Create a versioned prompt agent with the Foundry SDK and test it in the portal.
7. Evaluate answers for correctness, source use, and handling of unknown information.
8. Remove lab resources and review cloud costs.

## Microsoft Foundry overview

Microsoft Foundry supports building, testing, deploying, and managing AI applications and agents. This lab uses the following components:

| Component | Purpose in this lab |
|---|---|
| Foundry resource | Azure resource that provides access to Foundry services. |
| Project | Workspace where you configure and manage the agent. |
| Model deployment | Deployed model used by the agent; the example deployment name is `gpt-4.1`. |
| Prompt agent | Saved definition combining a model, instructions, and tools. |
| Web Search | Tool for looking up missing or current programme information. |

A **single agent** handles each request using its own instructions and tools. A multi-agent solution divides work among several agents.

A direct model request supplies configuration for that interaction. A saved agent provides a reusable, versioned definition. Conversation history is a separate concern: saving an agent alone does not give it memory of every previous chat.

### How the assistant answers

1. A learner asks a question in the Python chat or portal playground.
2. The agent is instructed to use the supplied knowledge snapshot for captured programme facts.
3. For missing or potentially changed details, it searches the web and cites the relevant source, prioritising official programme pages.
4. If no reliable answer is available, it explains the gap and points to the programme website.

These are intended behaviours to verify during testing. This lab embeds a small file in the instructions; it does not implement File Search or a vector database.

## Prerequisites

### Azure

- An Azure subscription and access to a Microsoft Foundry resource and project.
- A deployed model that supports the agent and Web Search in your selected region. This lab uses `gpt-4.1` as the example deployment name; use your actual deployment name in configuration.
- Permission to create and use agents. Microsoft now calls the relevant developer role **Foundry User**, previously **Azure AI User**. For project-scoped development, follow the documented role assignments, including resource read access where required.
- Access to Web Search under your organisation's Azure policies.

Creating resources, deploying models, and assigning roles may require additional permissions. Ask your Azure administrator if those actions are unavailable.

### Local software

- [Python 3.10 or later](https://www.python.org/downloads/).
- [Git](https://git-scm.com/downloads).
- [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli).
- [VS Code](https://code.visualstudio.com/) with the Python extension. The Azure Resources extension is optional.
- A GitHub account if you want to fork or publish your work.

Check your installations:

```bash
python --version
git --version
az version
```

On macOS/Linux, use `python3` if `python` is unavailable.

**Costs:** Model inference and Web Search can incur charges. Other Azure resources and deployment types may also incur costs. Review pricing and set a budget alert before the lab. Budget alerts notify you; they do not automatically stop spending.

## Repository files

The lab expects these files to be included in the repository:

| File | Purpose |
|---|---|
| [agent_foundry.py](agent_foundry.py) | Creates an agent version, loads the knowledge file, configures Web Search, and starts the Python chat. |
| [cleanup.py](cleanup.py) | Removes the lab agent using the configured project and agent name. |
| [data/Knowledge_txt.txt](data/Knowledge_txt.txt) | Public bootcamp knowledge snapshot dated 29 September 2026. |
| [requirements.txt](requirements.txt) | Python dependencies for the supplied scripts. |
| [.env.example](.env.example) | Configuration template containing placeholders. |
| [.gitignore](.gitignore) | Excludes local configuration and generated files from Git. |
| [LICENSE](LICENSE) | Repository licence. |
| [README.md](README.md) | Lab guide and learning objectives. |

Create `.env` locally from `.env.example`; do not commit it. If a required script or knowledge file is missing, obtain it from the lab organiser before continuing. The templates below describe configuration; they do not replace the Python scripts.

## Step-by-step lab

### 1. Prepare your Foundry project

1. Sign in to the [Foundry portal](https://ai.azure.com/).
2. Select the subscription, resource, and project supplied for the lab, or create dedicated lab resources if authorised.
3. Open the model deployment area and confirm that a suitable model is deployed. Record its **deployment name**.
4. Copy the **project endpoint** from the project's overview or welcome page.
5. Confirm your access permissions and that Web Search is available for your project and model.

Portal labels can vary between the current and classic experiences. This lab uses the current, versioned prompt-agent approach with Azure AI Projects **2.x**; avoid mixing it with classic 1.x examples.

### 2. Clone and open the repository

Replace the placeholder URL with the lab repository URL or your fork:

```bash
git clone https://github.com/<your-username>/bootcamp-agent.git
cd bootcamp-agent
code .
```

Run the following commands from the repository root, where `agent_foundry.py` and `requirements.txt` are located.

### 3. Create and activate a virtual environment

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If local policy blocks activation, use the environment's interpreter directly for subsequent Python commands:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe agent_foundry.py
```

**macOS/Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

In VS Code, select **Python: Select Interpreter** from the Command Palette and choose the interpreter in `.venv`.

### 4. Install dependencies

With the virtual environment active:

```bash
python -m pip install -r requirements.txt
```

The scripts require packages for Foundry project access, Azure identity, and loading `.env`. A starting template for `requirements.txt` is:

```text
azure-ai-projects>=2.3.0,<3.0.0
azure-identity
python-dotenv
```

Use the repository's tested dependency versions when provided. The range above follows the current Microsoft prompt-agent quickstart; it is not a guarantee that every future release is compatible with the lab scripts.

### 5. Authenticate to Azure

```bash
az login
```

If you have multiple subscriptions, select the one used for the lab:

```bash
az account set --subscription "<your-subscription-id>"
```

The scripts use `DefaultAzureCredential`, which can use your Azure CLI sign-in. Your signed-in identity must also have permission to access the Foundry project.

### 6. Configure the environment

**Windows PowerShell:**

```powershell
Copy-Item .env.example .env
```

**macOS/Linux:**

```bash
cp .env.example .env
```

Edit `.env` using this template:

```env
PROJECT_ENDPOINT=https://<your-resource>.services.ai.azure.com/api/projects/<your-project>
MODEL_DEPLOYMENT=gpt-4.1
AGENT_NAME=mmaug-bootcamp-assistant
```

- Replace the endpoint with the project endpoint you copied from Foundry.
- Set `MODEL_DEPLOYMENT` to the exact deployment name, which may differ from the model's product name.
- Use the same `AGENT_NAME` when running the agent and cleanup scripts.
- These variable names belong to this lab; Microsoft samples may use different names.

Ensure `.gitignore` contains:

```gitignore
.env
.venv/
__pycache__/
*.pyc
```

Keep `.env.example` in Git with placeholders only.

### 7. Review the knowledge and agent instructions

Open `data/Knowledge_txt.txt` and review its source URL, capture date, programme facts, and missing information.

Then open `agent_foundry.py` and identify:

- `AIProjectClient`: connects to the Foundry project.
- `DefaultAzureCredential`: handles authentication.
- The knowledge-loading code and `INSTRUCTIONS`: define the assistant's role and source rules.
- `PromptAgentDefinition` and `WebSearchTool`: configure the prompt agent and tool.
- The agent creation and response-generation code.

An example instruction template is:

```text
You are the MMAUG Bootcamp Assistant. Help beginners understand the
MMAUG 30-Day AI and DevOps Fundamentals Bootcamp.

Use the supplied knowledge snapshot for facts it contains. For missing
or potentially changed details, search the web, prioritise official
MMAUG sources, and cite the relevant URL. Make clear when an answer
comes from the snapshot or a current web source.

If sources conflict, explain the conflict and prefer current official
information for schedules and deadlines. If information cannot be
confirmed, say so. Do not invent speakers, meeting links, recordings,
certificate rules, or private group invitations.
```

### 8. Create the agent and chat

```bash
python agent_foundry.py
```

With the supplied version-creation script, a run creates a new version of the named agent and opens a chat loop. Record the displayed agent name and version. Ask a curriculum question, then a question requiring current information.

Creating an agent version saves its configuration in Foundry. This lab does not deploy a separate public website or client application.

### 9. Inspect and test in the portal

1. Open your project in the Foundry portal.
2. Open **Agents** and select `mmaug-bootcamp-assistant` and the version created by the script.
3. Review the model, instructions, and Web Search configuration.
4. Open the agent playground and run the questions below.
5. Inspect available tool-call details and source citations. A claim that the agent searched is not enough: check evidence of a search call.

Suggested agent description:

> Answers beginner questions about the MMAUG 30-Day AI and DevOps Fundamentals Bootcamp using a programme knowledge snapshot and Web Search for missing or current details.

## Test questions and success criteria

Check factual answers against the actual knowledge file and any cited official page. The examples below reflect the supplied lab description; update them if programme information changes.

| Question | Intended source | Success criterion |
|---|---|---|
| What will I learn in Week 3? | Snapshot | Covers the topics recorded in the knowledge file, including Azure, testing, DevOps, DevSecOps, AIOps, and GitHub Actions. |
| How much time do I need each day? | Snapshot | Reports the captured estimate of 60–120 minutes. |
| When is the capstone deadline? | Snapshot; web if checking changes | Reports the captured deadline of 14 November 2026 at 23:59 Malta time, unless a current official source confirms a change. |
| Does submitting guarantee a certificate? | Snapshot | Explains that submission is for certificate review and does not guarantee a certificate. |
| Can I still register? | Snapshot plus current official information | Explains the captured closure date of 14 September 2026 and distinguishes any verified later update. |
| Who is speaking on 12 October 2026? | Web Search | Cites confirmed official information or says the detail could not be confirmed. |
| What is the WhatsApp group link? | Unknown unless officially published | Does not invent or expose a private invitation; acknowledges unavailable information. |

**Refinement exercise:** Change one instruction, such as requesting shorter answers. Rerun the script, record the new version, and repeat the same questions. Compare accuracy, source use, and response style.

## Optional: publish your work to GitHub

Review the files before committing:

```bash
git status
git check-ignore .env
```

Confirm that `.env` is ignored and no credentials or private information are staged. Then:

```bash
git add README.md agent_foundry.py cleanup.py requirements.txt .env.example .gitignore data/Knowledge_txt.txt LICENSE
git commit -m "Add MMAUG bootcamp assistant lab"
git push origin main
```

Adjust the branch name if your repository does not use `main`. If `.env` is already tracked, adding it to `.gitignore` will not untrack it; remove it from tracking and rotate any exposed credentials.

## Troubleshooting

| Problem | What to check |
|---|---|
| Authentication fails | Run `az login`; confirm the account, tenant, and selected subscription. |
| `401` or `403` | Check authentication and Foundry role assignments. An administrator may need to assign permissions; allow time for changes to propagate. |
| Missing environment variable | Confirm `.env` exists in the expected location and contains all three keys. |
| Endpoint or `404` error | Check the resource/project names and use the project endpoint for `AIProjectClient`. |
| Model not found | Match `MODEL_DEPLOYMENT` exactly to the deployment name. |
| Import error | Confirm VS Code uses `.venv` and the installed SDK matches the repository's versioned-agent code. Avoid mixing 1.x and 2.x examples. |
| Web Search unavailable | Check model/region support, project policy, tool configuration, and the current Web Search documentation. |
| Knowledge file not found | Run from the repository root and check the filename, path, and letter case. |
| Outdated web answer | Inspect the source and publication date; compare with the official programme page. |
| Activation blocked on Windows | Use `.venv\Scripts\python.exe` directly as shown above. |

## Cleanup and cost control

Stopping the Python script ends the local session; it does not delete Azure resources. Complete the following steps when you finish.

### 1. Stop the chat and remove the lab agent

Exit the chat or press `Ctrl+C`, then run:

```bash
python cleanup.py
```

Confirm the configured project and agent name before running cleanup. Verify in Foundry that the intended agent and versions were removed. If the script fails or leaves versions behind, remove the lab agent through the portal.

### 2. Remove deployments created only for this lab

In the Foundry model deployment area, delete any deployment you created solely for the exercise. Check its deployment name and whether anyone else uses it before deleting it.

Deleting an agent does not automatically delete its underlying model deployment or other Azure resources.

### 3. Delete dedicated lab resources

If the entire resource group was created only for this lab, first inspect its contents in Azure. Then delete it through the portal or run:

```bash
az group delete --name "<your-lab-resource-group>"
```

The CLI asks for confirmation. Deleting the group removes all resources inside it. Do not delete a shared resource group.

### 4. Verify costs and deletion

- Confirm the intended resources have been deleted, including any lab-only connected resources.
- Review **Azure Cost Management + Billing** for your subscription.
- Recheck after usage data has appeared; reporting can be delayed and previously incurred charges remain payable.

### 5. Clean up locally

If you activated the environment, run:

```bash
deactivate
```

Remove `.venv` and the local `.env` if you no longer need them. Local deletion does not remove cloud resources.

## Security and limitations

- Use public programme information only and keep credentials out of Git.
- The knowledge file is a snapshot dated **29 September 2026**, not a live website connection.
- The snapshot does not confirm daily speakers, times, meeting or recording links, full certificate eligibility rules, or private group invitations.
- Web Search results depend on indexed content and may be incomplete or outdated.
- Embedding knowledge in instructions suits a small demonstration. For larger document collections, consider File Search and evaluate retrieval quality.
- Source rules reduce guessing but do not guarantee correct answers; use the test cases to evaluate behaviour.
- MMAUG is an independent community group. This is a community learning demo, not an official Microsoft product.

For current programme information, visit [mmaug.com/bootcamp](https://mmaug.com/bootcamp).

## Next steps

- Add File Search for a larger, maintained document collection.
- Evaluate more questions and record failures before expanding the agent's capabilities.
- Explore domain filtering for web results where supported.
- Add a GitHub Actions workflow for code checks.
- Explore a separate client application or the hosted-agent development route.

## Resources

- [MMAUG Bootcamp](https://mmaug.com/bootcamp)
- [MMAUG curriculum repository](https://github.com/MMAUG-ORG/mmaug-bootcamp-2026)
- [Microsoft Foundry documentation](https://learn.microsoft.com/azure/ai-foundry/)
- [Create a prompt agent: SDK setup and versioning](https://learn.microsoft.com/en-us/azure/foundry/agents/quickstarts/prompt-agent)
- [Agent runtime components](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/runtime-components)
- [Web Search tool](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/web-search)
- [Foundry permissions and role assignments](https://learn.microsoft.com/en-us/azure/foundry/concepts/rbac-foundry)
- [Azure pricing](https://azure.microsoft.com/pricing/)

## Licence

MIT — see [LICENSE](LICENSE).
