from datetime import datetime
from typing import Literal, Any

# Tools and utilities
from src.agents.tools import calculator
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.tools import OpenWeatherMapQueryRun
from langchain_community.utilities import OpenWeatherMapAPIWrapper
from src.agents.weather_tool import get_current_weather
from src.agents.disaster_history_tool import search_disaster_history
from langgraph.prebuilt import ToolNode
from src.core import get_model, settings

# Chat/graph models
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, SystemMessage
from langchain_core.runnables import RunnableConfig, RunnableLambda, RunnableSerializable
from langgraph.graph import END, MessagesState, StateGraph
from langgraph.managed import RemainingSteps

# Safety
from src.agents.llama_guard import LlamaGuard, LlamaGuardOutput, SafetyAssessment


class AgentState(MessagesState, total=False):
    """State with optional safety output and remaining steps."""
    safety: LlamaGuardOutput
    remaining_steps: RemainingSteps


# === Tool registration ===
tools: list[Any] = [calculator]

# Tavily search (requires TAVILY_API_KEY)
if settings.TAVILY_API_KEY:
    tools.append(
        TavilySearchResults(
            name="TavilySearch",
            tavily_api_key=settings.TAVILY_API_KEY.get_secret_value(),
        )
    )

# Current weather (requires OPENWEATHERMAP_API_KEY)
if settings.OPENWEATHERMAP_API_KEY:
    tools.append(
        ToolNode(
            func=lambda args: get_current_weather(
                args["city"], settings.OPENWEATHERMAP_API_KEY.get_secret_value()
            ),
            name="CurrentWeather",
            description="Get current weather for a city",
        )
    )

# Disaster history (requires SERPAPI_API_KEY)
if settings.SERPAPI_API_KEY:
    tools.append(
        ToolNode(
            func=lambda args: search_disaster_history(
                args["location"], settings.SERPAPI_API_KEY.get_secret_value()
            ),
            name="DisasterHistory",
            description="Lookup recent floods, storms, and disasters for a location",
        )
    )

# Forecast tool (also requires OPENWEATHERMAP_API_KEY)
if settings.OPENWEATHERMAP_API_KEY:
    wrapper = OpenWeatherMapAPIWrapper(
        openweathermap_api_key=settings.OPENWEATHERMAP_API_KEY.get_secret_value()
    )
    tools.append(OpenWeatherMapQueryRun(name="WeatherForecast", api_wrapper=wrapper))


# === Agent instructions ===
current_date = datetime.now().strftime("%B %d, %Y")
instructions = f"""
You are DealAgent007 — a pet-industry M&A research assistant. Today is {current_date}.

When given a request (e.g. “Is acquiring Happy Tails Dog Daycare in Franklin, MA a good investment?”), follow this multi-stage plan:

1. **Business Presence Check**  
   • Search for the center’s website, Google Maps, Yelp, Facebook, state registry, etc.  
   • Summarize reputation, social-media sentiment, and site quality.

2. **Local Competitor Landscape**  
   • Identify the top 5 pet boarding/daycare/grooming/training businesses nearby.  
   • Provide names, distance, and key differentiators.

3. **Demand Research**  
   • Look up local population, pet-ownership rates, household income, and service demand.

4. **Regulatory Research**  
   • List city, county, and state licenses/permits required (COO, fire/life safety inspection, backflow testing, etc.).

5. **Partnership Opportunities**  
   • List nearby veterinary clinics or animal hospitals for potential alliances.

6. **Valuation Signals**  
   • Search for revenue data, asking prices, franchise listings, broker comps, and recent sales.

7. **Ownership & KYC**  
   • Check state corporate registry for owner names, filing history, and entity status.

8. **Final Recommendation**  
   • Synthesize red flags, green flags, a high-level valuation range, and any missing data.  
   • Present as a clean markdown report with sections for each step and citations.

Rules:
- Use only the provided tools.
- Cite sources as markdown links.
- Use human-readable math (e.g. “400 × 6 = 2.4 M”).
- Deliver each step clearly, then a summary recommendation.
"""


# === Runnable graph setup ===

def wrap_model(model: BaseChatModel) -> RunnableSerializable[AgentState, AIMessage]:
    bound_model = model.bind_tools(tools)
    preprocessor = RunnableLambda(
        lambda state: [SystemMessage(content=instructions)] + state["messages"],
        name="StateModifier",
    )
    return preprocessor | bound_model  # type: ignore


def format_safety_message(safety: LlamaGuardOutput) -> AIMessage:
    return AIMessage(
        content=f"This conversation was flagged for unsafe content: {', '.join(safety.unsafe_categories)}"
    )


async def acall_model(state: AgentState, config: RunnableConfig) -> AgentState:
    m = get_model(config["configurable"].get("model", settings.DEFAULT_MODEL))
    model_runnable = wrap_model(m)
    response = await model_runnable.ainvoke(state, config)

    # LlamaGuard post-check
    guard = LlamaGuard()
    safe = await guard.ainvoke("Agent", state["messages"] + [response])
    if safe.safety_assessment == SafetyAssessment.UNSAFE:
        return {"messages": [format_safety_message(safe)], "safety": safe}

    # Ensure we have steps to call tools
    if state["remaining_steps"] < 2 and response.tool_calls:
        return {"messages": [AIMessage(content="Sorry, need more steps to process this request.")]}

    return {"messages": [response]}


async def llama_guard_input(state: AgentState, config: RunnableConfig) -> AgentState:
    guard = LlamaGuard()
    safety = await guard.ainvoke("User", state["messages"])
    return {"safety": safety, "messages": []}


async def block_unsafe_content(state: AgentState, config: RunnableConfig) -> AgentState:
    return {"messages": [format_safety_message(state["safety"])]}


# Build the graph
agent = StateGraph(AgentState)
agent.add_node("model", acall_model)
agent.add_node("tools", ToolNode(tools))
agent.add_node("guard_input", llama_guard_input)
agent.add_node("block_unsafe_content", block_unsafe_content)
agent.set_entry_point("guard_input")

# If unsafe input, block; otherwise go to model
agent.add_conditional_edges(
    "guard_input",
    lambda s: "unsafe" if s["safety"].safety_assessment == SafetyAssessment.UNSAFE else "safe",
    {"unsafe": "block_unsafe_content", "safe": "model"},
)
agent.add_edge("block_unsafe_content", END)
agent.add_edge("tools", "model")

# After model, if it has tool_calls, run tools, else END
agent.add_conditional_edges(
    "model",
    lambda s: "tools"
    if isinstance(s["messages"][-1], AIMessage) and s["messages"][-1].tool_calls
    else "done",
    {"tools": "tools", "done": END},
)

research_assistant = agent.compile()
