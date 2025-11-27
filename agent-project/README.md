**A Fast Way to Get Started with Agent Development Kit on Google Cloud**
July 3, 2025 • Wietse Venema

The Agent Development Kit (ADK) by Google is an open-source framework for creating AI agents. I'll show you how to get started with it using Gemini on Google Cloud and run the local web interface for development.

You can also use Gemini without Google Cloud. To learn more, go to ai.google.dev. In this guide, however, I'll focus on using Google Cloud.

**Prerequisites**
Before you begin, you'll need a Google Cloud project with billing enabled.

This guide requires the following tools:

- uv: An extremely fast Python package and project manager.
- gcloud CLI: The command-line interface for Google Cloud. Make sure you have authenticated (gcloud auth login) and set a default project (gcloud config set project [YOUR_PROJECT_ID]).

**Enable the AI Platform API**

Before you can use Gemini, you need to enable the AI Platform API for your project.

```
gcloud services enable aiplatform.googleapis.com
```

**Create an Agent**
First, create a new directory for your project and initialize it with uv.

```
mkdir agent-project
cd agent-project
uv init
```

Next, add the google-adk package to your project.

```
uv add google-adk
```

Now, create a new agent named agent.

```
uv run adk create agent
```

The adk create command walks you through a few setup questions. You'll be asked to:

- **Choose a model:** Select gemini-2.5-flash. You can always change this later in the generated agent.py file.
- **Choose a backend:** Select Vertex AI to access the model through Google Cloud.
- **Confirm your Google Cloud project:** If you have gcloud configured, it suggests your default project and the global region.

The command then creates a new directory agent with a few files, including agent.py with this agent implementation:

```
from google.adk.agents.llm_agent import Agent

root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge',
)
```

Finally, start the ADK web UI.

```
uv run adk web
```

This starts a local web server and opens the ADK web UI in your browser. You can now chat with your agent and explore the ADK's features.

**Modifying Your Agent's Configuration**

You can change your agent's configuration after it has been created:

**Model:** The model is defined in agent/agent.py. You can edit the model parameter in the Agent constructor to use a different Gemini model.
**Google Cloud Project and Region:** The connection to Vertex AI is configured in the agent/.env file. Here you can change the GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_LOCATION.

**Using the Global Endpoint**
Using the global region provides a single, highly available endpoint. This means that instead of being tied to a specific geographic location, your requests are dynamically routed to the most available resources to ensure uptime. You don't control which region handles the request; the system optimizes for availability. You can read more about this in the Vertex AI documentation.

**Wrap Up**
You've now created a basic agent with the Google ADK, configured it to use Gemini on Google Cloud, and launched the web UI. You also know how to modify the agent's configuration by editing the agent.py and .env files.

As a next step, you can start adding tools to your agent to give it more capabilities. I wrote another post to show you how to add Python functions as custom tools to your ADK agent.


**Adding a URL Fetcher**

I'll show you how to create a Python function that can fetch the content of a URL and add it to your agent's toolbox.

Install the httpx library. From your agent-project directory, run the following command:

```
uv add httpx
```

Open the agent/agent.py file.
Add the import httpx line at the top of the file.

Create the fetch_url function. This function takes a string url as input and returns the text content of the response.

```
def fetch_url(url: str) -> str:
    """Fetches the content of a URL."""
    with httpx.Client(follow_redirects=True) as client:
        response = client.get(url)
        response.raise_for_status()
        return response.text
```

Add the function to your Agent's tools list.

```
root_agent = Agent(
  # ...
  tools=[fetch_url]  # <-- Add tool
)      
```

Your agent.py should now look like this:

```
from google.adk.agents import Agent
import httpx

def fetch_url(url: str) -> str:
    """Fetches the content of a URL."""
    with httpx.Client(follow_redirects=True) as client:
        response = client.get(url)
        response.raise_for_status()
        return response.text

root_agent = Agent(
    model='gemini-2.0-flash-001',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge',
    tools=[fetch_url]
)
```

**Testing Your Tool**

Test your tool using the ADK web UI.

From your agent-project directory, (re)start the web UI:

```
uv run adk web
```

The restart is required because it doesn't reload changed files automatically
In the chat interface, ask the agent to summarize the content of a URL. For example: What's on wietsevenema.eu?

The agent calls your fetch_url function, receives the HTML content, and then summarizes it to answer your question. The web UI's conversation panel displays the function call and the final summarized response.

**Why Tools Matter**

Large Language Models (LLMs) used in isolation have some key limitations. Their knowledge is frozen at the time they were trained, and they cannot interact directly with the outside world. A key development that enables a more dynamic approach is tool calling.

**How Tools Work**

With each prompt, the application provides the LLM with a list of available tools and their descriptions.

The LLM uses these descriptions to decide which tool (if any) can help fulfill the prompt.

Instead of running the tool itself, the LLM generates a structured output that specifies which tool it wants to use and what information to pass to it.

The application code receives this output, executes the actual tool, and then calls the LLM a second time, providing the tool's result as part of the new prompt.
The LLM then uses the tool's output to generate its final response to you.

**The Importance of a Good Description**
The docstring you write for your function (in this example, """Fetches the content of a URL.""") is the primary way the LLM understands what the tool does. It's crucial that the description is clear, concise, and accurate.

**Why It's Important**

- Discovery: The LLM uses the description to determine if the tool is relevant to the user's request. A vague description might cause the model to overlook your tool when it's needed, or use it incorrectly.

- Parameter Mapping: The description, along with the function's parameter names and types, helps the model understand what arguments to pass. For your fetch_url function, the model knows it needs to provide a string for the url parameter because ADK tells it about it.

**Common Failure Modes**

- Vague or Ambiguous Descriptions: If the description is unclear, the model might not know when to use the tool. For instance, "Returns items in display order" doesn't specify what items are returned and what display order exactly means.

- Mismatch between Description and Functionality: If the description says the tool does one thing but the code does another, the model will be confused and likely produce incorrect or unexpected results.

- Confusing Parameter Names: If you use non-descriptive variable names, the model may struggle to provide the correct inputs, leading to errors.

**Summary**

You've learned how to add a tool to your ADK agent. By providing a Python function with a clear description, you can build agents that can fetch data, interact with APIs, and perform a wide range of tasks.