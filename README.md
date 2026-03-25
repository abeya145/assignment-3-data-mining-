# assignment-3-data-mining-
Building Conversational Agents with Tool Use and Reasoning Techniques

Description

This project is a conversational weather assistant that answers user questions about the weather using external APIs. The goal was to simulate how an AI system can use tools to retrieve real-time data and respond to different types of queries.

The assistant supports:

Current weather retrieval
Weather forecast
Simple comparisons between cities
Step-by-step reasoning for more complex questions
Setup Instructions
1. Install required libraries
pip install openai requests python-dotenv
2. Create a .env file

Add your API keys in the following format:

API_KEY=your_api_key_here
BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4.1-mini
WEATHER_API_KEY=your_weather_api_key
3. Run the program
python conversational_agent.py

Then choose the agent type:

1 → Basic
2 → Chain of Thought
3 → Advanced
Implementation Overview

The assistant is built using WeatherAPI to retrieve real-time data and a set of tool functions that simulate how AI systems interact with external services.

Main components:

get_current_weather() retrieves current weather data
get_weather_forecast() retrieves forecast data
process_messages() handles user input and tool execution
Advanced functions support parallel execution and multi-step workflows

The system is designed to mimic how a conversational agent decides when to call a tool and how to use the returned data.

Example Conversations
Basic Agent
You: What is the weather in Cairo?
Assistant:
Current weather in Cairo:
Temperature: 15°C
Condition: Clear
Humidity: 63%
Wind: 7.9 kph
Chain of Thought Agent
You: What is the temperature in Cairo and Riyadh?

Assistant:
Step 1: Getting weather data for both cities
Step 2: Comparing temperatures

Final Answer:
Cairo is cooler than Riyadh.
Advanced Agent
You: Compare the weather in Cairo, London, and Dubai

Assistant:
Cairo: 15°C, Clear
London: 8°C, Cloudy
Dubai: 25°C, Sunny

Dubai is the warmest city among the three.
Analysis

From testing the different agent types:

The Basic Agent works well for simple queries but does not provide detailed reasoning.
The Chain of Thought Agent improves clarity by breaking the problem into steps before giving the final answer.
The Advanced Agent can handle more complex queries, including comparisons and multi-step workflows.

Parallel execution improves performance when multiple locations are involved, since requests can be handled at the same time instead of sequentially.

Using tools makes the responses more accurate because the assistant relies on real data instead of generating approximate answers.

Challenges and Solutions

One of the main challenges was dealing with API errors such as authentication issues and quota limits. This required adjusting the setup and testing different configurations.

Another issue was model compatibility, where some models were not supported or required credits. This was handled by switching to supported configurations and simplifying execution when needed.

Initially, the output was returned as raw JSON, which was not user-friendly. This was improved by formatting the responses into readable text.

Finally, ensuring stability was important. Some inputs caused issues, so message sanitization and basic error handling were added.

Conclusion

This project helped me understand how conversational systems can integrate external tools, manage multi-step tasks, and handle real-world constraints like API limits.

#bonus discussion

Parallel tool execution improves performance the most when multiple independent requests are needed. For example, when comparing weather in different cities, each city can be queried separately at the same time instead of waiting for one request to finish before starting the next. This reduces the total execution time.

In my measurements, I observed that parallel execution was faster than sequential execution. The total time for parallel processing was lower because multiple tool calls were handled simultaneously, while sequential execution required waiting for each call to complete before moving to the next one. This resulted in a noticeable speedup.

However, multi-step reasoning is still necessary even when parallel execution is available. Some tasks depend on previous results, such as calculating temperature differences or making comparisons. In these cases, the system must first retrieve the data and then process it step by step. Therefore, parallel execution is most useful for independent tasks, while multi-step reasoning is required for dependent or more complex queries.


It also highlighted the importance of designing systems that are both functional and user-friendly.
