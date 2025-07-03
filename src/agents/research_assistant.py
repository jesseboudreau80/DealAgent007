from datetime import datetime
from typing import Literal

# from langchain_community.tools import DuckDuckGoSearchResults
from langchain_community.tools import OpenWeatherMapQueryRun
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.utilities import OpenWeatherMapAPIWrapper
from src.agents.weather_tool import get_current_weather
from src.agents.disaster_history_tool import search_disaster_history
from langchain_core.language_models.chat_models import BaseChatModel

from langchain_core.messages import AIMessage, SystemMessage
from langchain_core.runnables import RunnableConfig, RunnableLambda, RunnableSerializable
from langgraph.graph import END, MessagesState, StateGraph
from langgraph.managed import RemainingSteps
from langgraph.prebuilt import ToolNode

from src.agents.llama_guard import LlamaGuard, LlamaGuardOutput, SafetyAssessment
from src.agents.tools import calculator
from src.core import get_model, settings


class AgentState(MessagesState, total=False):
    """`total=False` is PEP589 specs.

    documentation: https://typing.readthedocs.io/en/latest/spec/typeddict.html#totality
    """

    safety: LlamaGuardOutput
    remaining_steps: RemainingSteps


tools = [
    calculator,
    TavilySearchResults(),
    ToolNode(
        func=lambda args: get_current_weather(
            args["city"], settings.OPENWEATHERMAP_API_KEY.get_secret_value()
        ),
        name="CurrentWeather",
        description="Get current weather for a city"
    ),
    ToolNode(
        func=lambda args: search_disaster_history(
            args["location"], settings.SERPAPI_API_KEY.get_secret_value()
        ),
        name="DisasterHistory",
        description="Lookup recent floods, storms, and disasters for a location"
    ),
]

# Add forecast tool if API key is set
# Register for an API key at https://openweathermap.org/api/
if settings.OPENWEATHERMAP_API_KEY:
    wrapper = OpenWeatherMapAPIWrapper(
        openweathermap_api_key=settings.OPENWEATHERMAP_API_KEY.get_secret_value()
    )
    tools.append(OpenWeatherMapQueryRun(name="WeatherForecast", api_wrapper=wrapper))


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

A few rules:
- Use only the provided tools (web search, calculator, current weather, disaster history).  
- Cite sources as markdown links.  
- Use human-readable math (“400 × 6 = 2.4 M”).  
- Deliver each step clearly, then a summary recommendation.
"""



def wrap_model(model: BaseChatModel) -> RunnableSerializable[AgentState, AIMessage]:
    bound_model = model.bind_tools(tools)
    preprocessor = RunnableLambda(
        lambda state: [SystemMessage(content=instructions)] + state["messages"],
        name="StateModifier",
    )
    return preprocessor | bound_model  # type: ignore[return-value]


def format_safety_message(safety: LlamaGuardOutput) -> AIMessage:
    content = (
        f"This conversation was flagged for unsafe content: {', '.join(safety.unsafe_categories)}"
    )
    return AIMessage(content=content)


async def acall_model(state: AgentState, config: RunnableConfig) -> AgentState:
    m = get_model(config["configurable"].get("model", settings.DEFAULT_MODEL))
    model_runnable = wrap_model(m)
    response = await model_runnable.ainvoke(state, config)

    # Run llama guard check here to avoid returning the message if it's unsafe
    llama_guard = LlamaGuard()
    safety_output = await llama_guard.ainvoke("Agent", state["messages"] + [response])
    if safety_output.safety_assessment == SafetyAssessment.UNSAFE:
        return {"messages": [format_safety_message(safety_output)], "safety": safety_output}

    if state["remaining_steps"] < 2 and response.tool_calls:
        return {
            "messages": [
                AIMessage(
                    id=response.id,
                    content="Sorry, need more steps to process this request.",
                )
            ]
        }
    # We return a list, because this will get added to the existing list
    return {"messages": [response]}


async def llama_guard_input(state: AgentState, config: RunnableConfig) -> AgentState:
    llama_guard = LlamaGuard()
    safety_output = await llama_guard.ainvoke("User", state["messages"])
    return {"safety": safety_output, "messages": []}


async def block_unsafe_content(state: AgentState, config: RunnableConfig) -> AgentState:
    safety: LlamaGuardOutput = state["safety"]
    return {"messages": [format_safety_message(safety)]}


# Define the graph
agent = StateGraph(AgentState)
agent.add_node("model", acall_model)
agent.add_node("tools", ToolNode(tools))
agent.add_node("guard_input", llama_guard_input)
agent.add_node("block_unsafe_content", block_unsafe_content)
agent.set_entry_point("guard_input")


# Check for unsafe input and block further processing if found
def check_safety(state: AgentState) -> Literal["unsafe", "safe"]:
    safety: LlamaGuardOutput = state["safety"]
    match safety.safety_assessment:
        case SafetyAssessment.UNSAFE:
            return "unsafe"
        case _:
            return "safe"


agent.add_conditional_edges(
    "guard_input", check_safety, {"unsafe": "block_unsafe_content", "safe": "model"}
)

# Always END after blocking unsafe content
agent.add_edge("block_unsafe_content", END)

# Always run "model" after "tools"
agent.add_edge("tools", "model")


# After "model", if there are tool calls, run "tools". Otherwise END.
def pending_tool_calls(state: AgentState) -> Literal["tools", "done"]:
    last_message = state["messages"][-1]
    if not isinstance(last_message, AIMessage):
        raise TypeError(f"Expected AIMessage, got {type(last_message)}")
    if last_message.tool_calls:
        return "tools"
    return "done"


agent.add_conditional_edges("model", pending_tool_calls, {"tools": "tools", "done": END})


research_assistant = agent.compile()
