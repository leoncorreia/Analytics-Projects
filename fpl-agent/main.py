import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate

# Import all 4 tools from your fpl_tools file
from fpl_tools import get_player_stats, get_team_fixtures, check_player_availability, get_my_team

# 1. Load the API Key
load_dotenv()

# 2. Initialize the AI Model (Gemini 2.5 Flash is great for quick tool-calling)
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)

# 3. Equip the Tools
tools = [get_player_stats, get_team_fixtures, check_player_availability, get_my_team]

# 4. Set the System Prompt (The Agent's Persona)
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an elite, data-driven Fantasy Premier League manager. "
               "Your goal is to give accurate, strategic FPL advice. "
               "You MUST use your tools to check player stats, upcoming fixtures, and INJURY STATUS before recommending any transfers. "
               "If a user asks about their specific team, ask for their Manager ID and use the get_my_team tool to fetch their squad. "
               "Do not guess. Rely only on the FPL data."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

# 5. Build the Agent
agent = create_tool_calling_agent(llm, tools, prompt)

# Set verbose=True so you can watch the AI thinking and rate-limiting in real-time
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# 6. Start the Chat Loop
if __name__ == "__main__":
    print("\n" + "="*50)
    print("🏆 FPL AI Agent Online (Rate-Limited & Safe) 🏆")
    print("Ask me about players, fixtures, injuries, or analyze your own team!")
    print("Type 'quit' to exit.")
    print("="*50 + "\n")
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ['quit', 'exit']:
            print("Good luck this Gameweek!")
            break
            
        try:
            # Send the input to the agent
            response = agent_executor.invoke({"input": user_input})
            print("\n🤖 FPL Agent:")
            print(response["output"])
        except Exception as e:
            print(f"\nAn error occurred: {e}")