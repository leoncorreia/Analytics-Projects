# 🏆 FPL AI Agent

An autonomous AI agent designed to help Fantasy Premier League (FPL) managers make data-driven decisions. Powered by LangChain and Google's Gemini, this agent fetches live data directly from the official FPL API to analyze player stats, check injury updates, analyze upcoming fixtures, and review your specific FPL squad.



## ✨ Features
* **Player Scouting:** Fetches current price, total points, and form for any FPL player.
* **Fixture Analysis:** Calculates the Fixture Difficulty Rating (FDR) for a team's next 3 matches.
* **Live Injury Checking:** Reads the official FPL medical news to warn you about flags, injuries, or suspensions.
* **Squad Review:** Input your FPL Manager ID, and the agent will fetch your active 15-man squad to suggest tailored transfers.
* **Rate-Limited:** Includes built-in API rate limiting to prevent IP bans from the FPL servers.

## 🛠️ Prerequisites
* Python 3.9+
* A free [Google AI Studio](https://aistudio.google.com/) API Key for the Gemini model.

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/fpl-ai-agent.git](https://github.com/YOUR_USERNAME/fpl-ai-agent.git)
   cd fpl-ai-agent

```

2. **Install the required dependencies:**
```bash
pip install -r requirements.txt

```


3. **Set up your environment variables:**
Create a `.env` file in the root directory and add your Google Gemini API key:
```env
GOOGLE_API_KEY=your_api_key_here

```



## 💻 Usage

Run the main script to start the interactive terminal chat:

```bash
python main.py

```

### Example Prompts to Try:

* *"I'm thinking of bringing in Bukayo Saka. What are his stats and Arsenal's next 3 fixtures?"*
* *"Are there any injury updates for Alexander-Arnold or Reece James?"*
* *"My Manager ID is 123456. Can you look at my team and suggest one transfer to make this week?"*

## 📁 Project Structure

* `main.py`: The core conversational loop and LangChain agent initialization.
* `fpl_tools.py`: The custom Python tools used by the agent to query the FPL API.
* `requirements.txt`: Python package dependencies.
* `.env`: Your private environment variables (ignored by Git).

## ⚠️ Disclaimer

This project is not affiliated with the official Fantasy Premier League or the Premier League. It is a fan-made tool for educational purposes.

```


