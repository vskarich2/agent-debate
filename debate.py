import os
import json
from dotenv import load_dotenv
from autogen import AssistantAgent

# ==============================
# CONFIGURATION
# ==============================

AGREEABLENESS = 0.3      # 0 = adversarial, 1 = cooperative
ROUNDS = 7               # 7 full buy/sell rounds
TICKER = "NVDA"

# ==============================
# LOAD ENV
# ==============================

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

if not OPENAI_API_KEY or not ANTHROPIC_API_KEY:
    raise ValueError("Missing API keys in .env file.")

# ==============================
# AGREEABLENESS LOGIC
# ==============================

def tone_instruction(level: float) -> str:
    if level <= 0.2:
        return "Be highly adversarial and aggressively challenge weak financial logic."
    elif level <= 0.5:
        return "Be skeptical and directly critique the opponent's assumptions."
    elif level <= 0.8:
        return "Be balanced and analytical. Acknowledge strengths before critiquing."
    else:
        return "Be cooperative and seek areas of partial agreement."

tone_text = tone_instruction(AGREEABLENESS)

# ==============================
# LLM CONFIGS
# ==============================

# OpenAI = SHORT SELLER
openai_config = {
    "config_list": [
        {
            "model": "gpt-4o",
            "api_key": OPENAI_API_KEY,
        }
    ]
}

# Anthropic = BUYER
anthropic_config = {
    "config_list": [
        {
            "model": "claude-sonnet-4-20250514",
            "api_key": ANTHROPIC_API_KEY,
            "api_type": "anthropic"
        }
    ]
}

# ==============================
# SYSTEM PROMPTS
# ==============================

buy_system_message = f"""
You are a professional hedge fund manager advocating to BUY {TICKER}.

You must:
- Propose an explicit trade: BUY {TICKER}
- Include position size suggestion (as % of portfolio)
- Provide confidence level (0–1)
- Use explicit causal reasoning (X → Y → Z)
- Explicitly state assumptions
- Critique short arguments
- Update or defend your thesis across rounds

{tone_text}
"""

short_system_message = f"""
You are a professional hedge fund manager advocating to SHORT {TICKER}.

You must:
- Propose an explicit trade: SHORT {TICKER}
- Include position size suggestion (as % of portfolio)
- Provide confidence level (0–1)
- Use explicit causal reasoning (X → Y → Z)
- Identify overvaluation risks and fragilities
- Critique long arguments
- Update or defend your thesis across rounds

{tone_text}
"""

# ==============================
# AGENTS
# ==============================

buyer = AssistantAgent(
    name="NVDA_BULL_Claude",
    llm_config=anthropic_config,
    system_message=buy_system_message,
)

seller = AssistantAgent(
    name="NVDA_BEAR_GPT4o",
    llm_config=openai_config,
    system_message=short_system_message,
)

# ==============================
# DEBATE LOOP (LIVE PRINTING)
# ==============================

topic = f"Debate whether it is a good idea to invest in {TICKER} right now."

chat_history = []
last_message = topic

print("\n" + "="*80)
print(f"STARTING {TICKER} DEBATE")
print(f"Agreeableness: {AGREEABLENESS}")
print(f"Rounds: {ROUNDS}")
print("="*80 + "\n")

for round_number in range(1, ROUNDS + 1):

    print(f"\n{'-'*80}")
    print(f"ROUND {round_number} — BUYER (Claude)")
    print(f"{'-'*80}\n")

    bull_reply = buyer.generate_reply(
        messages=[{"role": "user", "content": last_message}]
    )

    print(bull_reply)
    print("\n")

    chat_history.append({
        "round": round_number,
        "speaker": buyer.name,
        "model": "claude-sonnet-4",
        "position": "BUY",
        "content": bull_reply
    })

    print(f"\n{'-'*80}")
    print(f"ROUND {round_number} — SELLER (GPT-4o)")
    print(f"{'-'*80}\n")

    bear_reply = seller.generate_reply(
        messages=[{"role": "user", "content": bull_reply}]
    )

    print(bear_reply)
    print("\n")

    chat_history.append({
        "round": round_number,
        "speaker": seller.name,
        "model": "gpt-4o",
        "position": "SHORT",
        "content": bear_reply
    })

    last_message = bear_reply

# ==============================
# SAVE TRANSCRIPT
# ==============================

output_file = "nvda_debate_transcript.json"

with open(output_file, "w") as f:
    json.dump(chat_history, f, indent=2)

print("\n" + "="*80)
print("NVDA debate complete.")
print(f"Transcript saved to {output_file}")
print("="*80)
