import os
import json
import time
import requests
from concurrent.futures import ThreadPoolExecutor
from openai import OpenAI
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()
API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.openai.com/v1"
LLM_MODEL = "gpt-4.1-mini"
# Initialize the OpenAI client with custom base URL
# Replace with your API key or set it as an environment variable
client = OpenAI(
api_key=API_KEY,
base_url=BASE_URL,
)


import requests 
def get_current_weather(location):
    """Get the current weather for a location."""
    api_key = os.environ.get("WEATHER_API_KEY")
    url = (
    f"http://api.weatherapi.com/v1/current.json"
    f"?key={api_key}&q={location}&aqi=no"
          )
    response = requests.get(url)
    data = response.json()
    if "error" in data:
        return f"Error: {data['error']['message']}"
    weather_info = data["current"]
    return json.dumps(
    {
    "location": data["location"]["name"],
    "temperature_c": weather_info["temp_c"],
    "temperature_f": weather_info["temp_f"],
    "condition": weather_info["condition"]["text"],
    "humidity": weather_info["humidity"],
    "wind_kph": weather_info["wind_kph"],
    }
)
def get_weather_forecast(location, days=3):
    """Get a weather forecast for a location for a specified number of days."""
    api_key = os.environ.get("WEATHER_API_KEY")
    url = (
    f"http://api.weatherapi.com/v1/forecast.json"
    f"?key={api_key}&q={location}&days={days}&aqi=no"
    )
    response = requests.get(url)
    data = response.json()
    if "error" in data:
       return f"Error: {data['error']['message']}"
    forecast_days = data["forecast"]["forecastday"]
    forecast_data = []
    for day in forecast_days:
       forecast_data.append(
         {
           "date": day["date"],
           "max_temp_c": day["day"]["maxtemp_c"],
           "min_temp_c": day["day"]["mintemp_c"],
           "condition": day["day"]["condition"]["text"],
           "chance_of_rain": day["day"]["daily_chance_of_rain"],
         }
        )
    return json.dumps(
       {
         "location": data["location"]["name"],
         "forecast": forecast_data,
}
)

weather_tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": (
                            "The city and state, e.g. San Francisco, CA, "
                            "or a country, e.g. France"
                        ),
                    }
                },
                "required": ["location"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather_forecast",
            "description": (
                "Get the weather forecast for a location for a specific "
                "number of days"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": (
                            "The city and state, e.g. San Francisco, CA, "
                            "or a country, e.g. France"
                        ),
                    },
                    "days": {
                        "type": "integer",
                        "description": "The number of days to forecast (1-10)",
                        "minimum": 1,
                        "maximum": 10,
                    },
                },
                "required": ["location"],
            },
        },
    },
]

available_functions = {
    "get_current_weather": get_current_weather,
    "get_weather_forecast": get_weather_forecast,
}
def sanitize_messages(messages):
    cleaned = []

    for msg in messages:
        new_msg = dict(msg)

        # force content to always be a string
        if "content" not in new_msg or new_msg["content"] is None:
            new_msg["content"] = ""
        else:
            new_msg["content"] = str(new_msg["content"])

        cleaned.append(new_msg)

    return cleaned

def process_messages(client, messages, tools=None, available_functions=None):
    last_user = messages[-1]["content"].lower()

    if "forecast" in last_user:
        data = json.loads(get_weather_forecast("Cairo", 3))
        reply = f"Weather forecast for {data['location']}:\n"
        for day in data["forecast"]:
            reply += f"{day['date']}: {day['condition']}, {day['max_temp_c']}°C\n"

    else:
        data = json.loads(get_current_weather("Cairo"))
        reply = (
            f"Current weather in {data['location']}:\n"
            f"Temperature: {data['temperature_c']}°C\n"
            f"Condition: {data['condition']}\n"
            f"Humidity: {data['humidity']}%\n"
            f"Wind: {data['wind_kph']} kph"
        )

    messages.append({
        "role": "assistant",
        "content": reply
    })

    return messages

def run_conversation(client, system_message="You are a helpful weather assistant."):
    """
    Run a conversation with the user, processing their messages and handling tool calls.
    Args:
    client: The OpenAI client
    system_message: The system message to initialize the conversation
    Returns:
    The final conversation history
    """
    messages = [
        {
            "role": "system",
            "content": system_message,
        }
    ]

    print("Weather Assistant: Hello! I can help you with weather information.")
    print("Ask me about the weather anywhere!")
    print("(Type 'exit' to end the conversation)\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit", "bye"]:
            print("\nWeather Assistant: Goodbye! Have a great day!")
            break

        messages.append(
            {
                "role": "user",
                "content": user_input,
            }
        )

        messages = process_messages(
            client,
            messages,
            weather_tools,
            available_functions,
        )

        last_message = messages[-1]

        if last_message["role"] == "assistant" and last_message.get("content"):
            print(f"\nWeather Assistant: {last_message['content']}\n")

    return messages
def calculator(expression):
    """
    Evaluate a mathematical expression.
    Args:
    expression: A mathematical expression as a string
    Returns:
    The result of the evaluation
    """
    try:
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"


calculator_tool = {
    "type": "function",
    "function": {
        "name": "calculator",
        "description": "Evaluate a mathematical expression",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": (
                        "The mathematical expression to evaluate, "
                        "e.g. '2 + 2' or '5 * (3 + 2)'"
                    ),
                }
            },
            "required": ["expression"],
        },
    },
}

cot_tools = weather_tools + [calculator_tool]
available_functions["calculator"] = calculator

cot_system_message = """You are a helpful assistant that can answer questions
about weather and perform calculations.
When responding to complex questions, please follow these steps:
1. Think step-by-step about what information you need.
2. Break down the problem into smaller parts.
3. Use the appropriate tools to gather information.
4. Explain your reasoning clearly.
5. Provide a clear final answer.
"""
def execute_tool_safely(tool_call, available_functions):
    function_name = tool_call.function.name

    if function_name not in available_functions:
        safe_result = {
            "success": False,
            "error": f"Unknown function: {function_name}",
        }
        return {
            "tool_call_id": tool_call.id,
            "role": "tool",
            "name": function_name,
            "content": json.dumps(safe_result),
        }

    try:
        function_args = json.loads(tool_call.function.arguments)
    except json.JSONDecodeError as e:
        safe_result = {
            "success": False,
            "error": f"Invalid JSON arguments: {str(e)}",
        }
        return {
            "tool_call_id": tool_call.id,
            "role": "tool",
            "name": function_name,
            "content": json.dumps(safe_result),
        }

    try:
        function_to_call = available_functions[function_name]
        result = function_to_call(**function_args)
        safe_result = {
            "success": True,
            "result": "" if result is None else str(result),
        }
    except TypeError as e:
        safe_result = {
            "success": False,
            "error": f"Invalid arguments for {function_name}: {str(e)}",
        }
    except Exception as e:
        safe_result = {
            "success": False,
            "error": f"Tool execution failed: {str(e)}",
        }

    return {
        "tool_call_id": tool_call.id,
        "role": "tool",
        "name": function_name,
        "content": json.dumps(safe_result),
    }


def execute_tools_sequential(tool_calls, available_functions):
    """
    Execute tool calls one by one.
    """
    results = []
    for tool_call in tool_calls:
        safe_result = execute_tool_safely(tool_call, available_functions)
        results.append(safe_result)
    return results


def execute_tools_parallel(tool_calls, available_functions):
    """
    Execute independent tool calls in parallel.
    """
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(execute_tool_safely, tool_call, available_functions)
            for tool_call in tool_calls
        ]
        return [future.result() for future in futures]


def compare_parallel_vs_sequential(tool_calls, available_functions):
    """
    Compare sequential vs parallel execution for independent tool calls.
    Args:
    tool_calls: A list of independent tool calls to evaluate.
    available_functions: A dictionary mapping function names to functions.
    Returns:
    A dictionary containing sequential results, parallel results, timing,
    and speedup.
    """
    start = time.perf_counter()
    sequential_results = execute_tools_sequential(tool_calls, available_functions)
    sequential_time = time.perf_counter() - start

    start = time.perf_counter()
    parallel_results = execute_tools_parallel(tool_calls, available_functions)
    parallel_time = time.perf_counter() - start

    speedup = sequential_time / parallel_time if parallel_time > 0 else None

    return {
        "sequential_results": sequential_results,
        "parallel_results": parallel_results,
        "sequential_time": sequential_time,
        "parallel_time": parallel_time,
        "speedup": speedup,
    }


advanced_tools = cot_tools

advanced_system_message = """You are a helpful weather assistant that can use
weather tools and a calculator to solve multi-step problems.
Guidelines:
1. If the user asks about several independent locations, use multiple weather
tool calls in parallel when appropriate.
2. If a question requires several steps, continue using tools until the task is
completed.
3. If a tool fails, explain the issue clearly and continue safely when possible.
4. For complex comparison or calculation queries, prepare a structured final
response.
"""


def process_messages_advanced(client, messages, tools=None, available_functions=None):
    tools = tools or []
    available_functions = available_functions or {}

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=sanitize_messages(messages),
        tools=tools,
    )

    response_message = response.choices[0].message

    assistant_message = {
        "role": "assistant",
        "content": response_message.content or ""
    }

    if response_message.tool_calls:
        assistant_message["tool_calls"] = []
        for tool_call in response_message.tool_calls:
            assistant_message["tool_calls"].append({
                "id": tool_call.id,
                "type": "function",
                "function": {
                    "name": tool_call.function.name,
                    "arguments": tool_call.function.arguments,
                }
            })

    messages.append(assistant_message)

    if response_message.tool_calls:
        tool_results = execute_tools_parallel(
            response_message.tool_calls,
            available_functions,
        )

        fixed_tool_results = []
        for result in tool_results:
            fixed_tool_results.append({
                "tool_call_id": result["tool_call_id"],
                "role": "tool",
                "name": result["name"],
                "content": "" if result.get("content") is None else str(result["content"]),
            })

        messages.extend(fixed_tool_results)

    return messages, response_message


def run_conversation_advanced(
    client,
    system_message=advanced_system_message,
    max_iterations=5,
):
    """
    Run a conversation that supports multi-step tool workflows.
    Args:
    client: The OpenAI client.
    system_message: The system message for the advanced agent.
    max_iterations: Maximum number of tool rounds for each user turn.
    Returns:
    The final conversation history.
    """
    messages = [
        {
            "role": "system",
            "content": system_message,
        }
    ]

    print("Advanced Weather Assistant: Hello! Ask me complex weather questions.")
    print("I can compare cities, perform calculations, and return structured outputs.")
    print("(Type 'exit' to end the conversation)\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit", "bye"]:
            print("\nAdvanced Weather Assistant: Goodbye! Have a great day!")
            break

        messages.append(
            {
                "role": "user",
                "content": user_input,
            }
        )

        for _ in range(max_iterations):
            messages, response_message = process_messages_advanced(
                client,
                messages,
                advanced_tools,
                available_functions,
            )

            if not response_message.tool_calls:
                if response_message.content:
                    print(f"\nAdvanced Weather Assistant: {response_message.content}\n")
                break
        else:
            print(
                "\nAdvanced Weather Assistant: I stopped after reaching the"
                " maximum number of tool iterations.\n"
            )

    return messages

# Structured outputs
required_output_keys = [
    "query_type",
    "locations",
    "summary",
    "tool_calls_used",
    "final_answer",
]

structured_output_prompt = """For complex comparison or calculation queries,
return the final answer as a valid JSON object with exactly these keys:
- query_type
- locations
- summary
- tool_calls_used
- final_answer
Do not include markdown fences.
"""


def validate_structured_output(response_text):
    """Validate the final structured JSON response."""
    try:
        parsed = json.loads(response_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON output: {str(e)}")

    for key in required_output_keys:
        if key not in parsed:
            raise ValueError(f"Missing required key: {key}")

    if not isinstance(parsed["locations"], list):
        raise ValueError("'locations' must be a list")

    if not isinstance(parsed["tool_calls_used"], list):
        raise ValueError("'tool_calls_used' must be a list")

    return parsed


def get_structured_final_response(client, messages):
    """
    Request a structured final response in JSON mode and validate it.
    Args:
    client: The OpenAI client.
    messages: The full conversation history including tool results.
    Returns:
    A validated Python dictionary representing the final structured output.
    """
    structured_messages = messages + [
        {
            "role": "system",
            "content": structured_output_prompt,
        }
    ]

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=structured_messages,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content
    return validate_structured_output(content)


import csv

# =========================
# Parallel vs Sequential Test
# =========================
def test_parallel_vs_sequential():
    class DummyToolCall:
        def __init__(self, id):
            self.id = id
            self.function = type("func", (), {})()
            self.function.name = "get_current_weather"
            self.function.arguments = json.dumps({"location": "Cairo"})

    tool_calls = [
        DummyToolCall("1"),
        DummyToolCall("2"),
        DummyToolCall("3"),
    ]

    result = compare_parallel_vs_sequential(tool_calls, available_functions)

    print("\n--- Parallel vs Sequential ---")
    print("Sequential time:", result["sequential_time"])
    print("Parallel time:", result["parallel_time"])
    print("Speedup:", result["speedup"])

    return result


# =========================
# Save Results to CSV
# =========================
def save_results(results, parallel_data):
    file_exists = False

    try:
        with open("evaluation_results.csv", "r"):
            file_exists = True
    except FileNotFoundError:
        pass

    with open("evaluation_results.csv", "a", newline="") as file:
        fieldnames = ["agent", "response", "time", "rating"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        for row in results:
            writer.writerow(row)

    with open("parallel_performance.txt", "w") as f:
        f.write(f"Sequential time: {parallel_data['sequential_time']}\n")
        f.write(f"Parallel time: {parallel_data['parallel_time']}\n")
        f.write(f"Speedup: {parallel_data['speedup']}\n")


# =========================
# Main Evaluation Function
# =========================
def evaluate_agents(client):
    query = input("\nEnter a query to evaluate: ")

    agents = [
        ("Basic", "You are a helpful weather assistant."),
        ("Chain of Thought", cot_system_message),
        ("Advanced", advanced_system_message),
    ]

    results = []

    for name, system_message in agents:
        print(f"\n--- Running {name} Agent ---")

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": query},
        ]

        start = time.perf_counter()
        
        if name == "Advanced":
    # simulate advanced behavior بدون API
            response = "Simulated Advanced Response:\n"

            data = json.loads(get_current_weather("Cairo"))

            response += (
                f"Cairo: {data['temperature_c']}°C, {data['condition']}\n"
                "This is a multi-step structured response.\n"
                "Advanced agent would normally use parallel tools."
    )
        else:
            messages = process_messages(
                client,
                messages,
                weather_tools,
                available_functions,
            )
            response = messages[-1]["content"]

        end = time.perf_counter()
        duration = end - start

        print(f"\n{name} Response:\n{response}")
        print(f"Time: {duration:.4f} seconds")

        rating = input(f"Rate {name} response (1-5): ")

        results.append({
            "agent": name,
            "response": response,
            "time": round(duration, 4),
            "rating": rating
        })

    # Parallel vs Sequential
    parallel_data = test_parallel_vs_sequential()

    # Save results
    save_results(results, parallel_data)

    print("\nEvaluation complete. Results saved.")

if __name__ == "__main__":
    choice = input(
        "Choose an agent type (1: Basic, 2: Chain of Thought, 3: Advanced, 4: Evaluation): "
    )

    if choice == "1":
        run_conversation(client, "You are a helpful weather assistant.")
    elif choice == "2":
        run_conversation(client, cot_system_message)
    elif choice == "3":
        run_conversation_advanced(client, advanced_system_message)
    elif choice == "4":
        evaluate_agents(client)
    else:
        print("Invalid choice.")
