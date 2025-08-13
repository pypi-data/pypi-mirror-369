from dotenv import load_dotenv
from crewai import Agent, Task, Crew
from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from langchain_community.tools import DuckDuckGoSearchResults
from unified_agent_interface.utils import patch_log

load_dotenv()


class MyCustomDuckDuckGoToolInput(BaseModel):
    """Input schema for MyCustomDuckDuckGoTool."""

    query: str = Field(..., description="URL to search for.")


# def step_callback(output: AgentAction | AgentFinish | ToolResult) -> None:
#     # Mirror to server logs and optionally ask for human input
#     try:
#         post_log(None, "DEBUG", f"step: {repr(output)}")
#     except Exception:
#         pass
#     text = str(getattr(output, "log", None) or output)
#     if "human" in text.lower() or "check with a human" in text.lower():
#         # Demonstrate prompting for human input mid-run (optional heuristic)
#         msg, _ = request_human_input(
#             None, prompt="Agent requested human input. Provide guidance:"
#         )
#         if msg:
#             post_log(None, "INFO", f"human_input: {msg}")


# def task_callback(output: TaskOutput) -> None:
#     # Log task completion and optionally require final human approval
#     summary = f"Task completed desc={output.description!r} by={output.agent}"
#     try:
#         post_log(None, "INFO", summary)
#     except Exception:
#         pass
#     # If the description suggests human approval, prompt here
#     if "check with a human" in (output.description or "").lower():
#         msg, _ = request_human_input(
#             None, prompt="Approve the task output? Type feedback or 'ok':"
#         )
#         if msg:
#             post_log(None, "INFO", f"human_approval: {msg}")


class MyCustomDuckDuckGoTool(BaseTool):
    name: str = "DuckDuckGo Search Tool"
    description: str = "Search the web for a given query."
    args_schema: Type[BaseModel] = MyCustomDuckDuckGoToolInput

    def _run(self, query: str) -> str:
        duckduckgo_tool = DuckDuckGoSearchResults()
        response = duckduckgo_tool.invoke(query)
        return response


patch_log(MyCustomDuckDuckGoTool._run, label="crewai", capture_return=True)

search_tool = MyCustomDuckDuckGoTool()


# Define your agents with roles, goals, tools, and additional attributes
researcher = Agent(
    role="Senior Research Analyst",
    goal="Uncover cutting-edge developments in AI and data science",
    backstory=(
        "You are a Senior Research Analyst at a leading tech think tank. "
        "Your expertise lies in identifying emerging trends and technologies in AI and data science. "
        "You have a knack for dissecting complex data and presenting actionable insights."
    ),
    verbose=True,
    allow_delegation=False,
    tools=[search_tool],
)
writer = Agent(
    role="Tech Content Strategist",
    goal="Craft compelling content on tech advancements",
    backstory=(
        "You are a renowned Tech Content Strategist, known for your insightful and engaging articles on technology and innovation. "
        "With a deep understanding of the tech industry, you transform complex concepts into compelling narratives."
    ),
    verbose=True,
    allow_delegation=True,
    tools=[search_tool],
    cache=False,  # Disable cache for this agent
)

# Create tasks for your agents
task1 = Task(
    description=(
        "Conduct a comprehensive analysis of the latest advancements in AI in 2025. "
        "Identify key trends, breakthrough technologies, and potential industry impacts. "
        "Compile your findings in a detailed report. "
        "Make sure to check with a human if the draft is good before finalizing your answer."
    ),
    expected_output="A comprehensive full report on the latest AI advancements in 2025, leave nothing out",
    agent=researcher,
    human_input=True,
)

task2 = Task(
    description=(
        "Using the insights from the researcher's report, develop an engaging blog post that highlights the most significant AI advancements. "
        "Your post should be informative yet accessible, catering to a tech-savvy audience. "
        "Aim for a narrative that captures the essence of these breakthroughs and their implications for the future."
    ),
    expected_output="A compelling 3 paragraphs blog post formatted as markdown about the latest AI advancements in 2025",
    agent=writer,
    human_input=True,
)

# Instantiate your crew with a sequential process
crew = Crew(
    agents=[researcher, writer],
    tasks=[task1, task2],
    verbose=True,
    memory=True,
    planning=True,  # Enable planning feature for the crew
    # step_callback=step_callback,
    # task_callback=task_callback,
)

# # Get your crew to work!
# result = crew.kickoff()

# print("######################")
# print(result)
