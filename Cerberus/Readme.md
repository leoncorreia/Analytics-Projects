
# 🐶 CERBERUS: The Instant Boardroom

> **3 AI Executives. 1 Idea. Zero Mercy.** > *Powered by Groq's LPU™ Inference Engine for real-time parallel judgment.*

## ⚡ What is Cerberus?
Cerberus is a multi-agent strategy tool designed to destroy (or validate) your ideas instantly. 

Instead of asking a single AI "Is this good?", Cerberus spins up three distinct C-Suite personas—**The Visionary CEO**, **The Skeptic CFO**, and **The Pragmatic CTO**—who simultaneously debate your pitch in real-time. 

Because it runs on **Groq**, the latency is near-zero. You don't wait for one agent to finish before the next begins; the entire "boardroom" speaks at once.

## 🧠 The Squad (Personas)

| Persona | Role | Model | Personality |
| :--- | :--- | :--- | :--- |
| **THE VISIONARY** | CEO | `llama-3.3-70b` | Reckless, high-growth, ignores costs. Wants global domination. |
| **THE SKEPTIC** | CFO | `llama-3.1-8b` | Stingy, risk-averse, hates lawsuits. Cares about unit economics. |
| **THE ENGINEER** | CTO | `gemma2-9b-it` | Pragmatic, tired, hates buzzwords. Cares about server load & debt. |

## 🚀 Installation

### Prerequisites
1. Python 3.8+
2. A free API Key from [Groq Console](https://console.groq.com)

### 1. Clone & Install
```bash
git clone [https://github.com/yourusername/cerberus.git](https://github.com/yourusername/cerberus.git)
cd cerberus
pip install groq colorama python-dotenv

```

### 2. Configure Credentials

Create a `.env` file in the root directory:

```bash
GROQ_API_KEY=gsk_your_actual_key_here

```

## 🖥️ Usage

### Local Terminal

Run the script directly in your terminal:

```bash
python cerberus.py

```

### Google Colab

If running in a notebook, ensure you install dependencies first:

```python
!pip install groq colorama python-dotenv

```

Then use the Colab-specific code provided in the repository (using `await run_boardroom()` instead of `asyncio.run()`).

## 📂 Example Output

**User Pitch:** *"I want to build a dating app for ghosts."*

---

**THE VISIONARY (CEO):** "Brilliant! 'Ghosting' is literally the feature. The TAM (Total Addressable Market) is everyone who has ever died. Massive virality potential. Let's burn 10M on ads immediately!"

**THE SKEPTIC (CFO):** "Absolutely not. Dead people have no disposable income. How do we monetize? You can't run ads to non-corporeal entities. This is a lawsuit waiting to happen."

**THE ENGINEER (CTO):** "Technically feasible, but the latency between the afterlife and our servers is an issue. Also, user verification is impossible. I'm not building this."

---

## 🛠️ Tech Stack

* **Engine:** [Groq API](https://groq.com) (LPU Inference)
* **Language:** Python
* **Concurrency:** `asyncio` (Parallel requests)
* **Models:** Llama 3.3, Llama 3.1, Gemma 2
