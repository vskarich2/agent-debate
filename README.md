** SETUP
brew install uv (if you don't have it)
git clone https://github.com/YOUR_USERNAME/agent-debate.git
cd agent-debate
uv sync


** Create a .env file in content root with an OPENAI_API_KEY= and ANTHROPIC_API_KEY=

** RUN DEBATE
uv run debate.py