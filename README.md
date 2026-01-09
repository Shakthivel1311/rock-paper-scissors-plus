# Rock-Paper-Scissors-Plus 🎮

A fun Rock-Paper-Scissors game with a twist - there's a special **bomb** move! Play against an AI referee powered by Google's Gemini.

## What's This?

It's the classic game you know, but better:
- Play best of 3 rounds
- Each player gets ONE bomb move per game (beats everything!)
- AI referee tracks the score and enforces rules
- Beautiful web interface with animations

## How to Play

**Live Version**: [rock-paper-scissor-game-xi-woad.vercel.app](https://rock-paper-scissor-game-xi-woad.vercel.app)

Or run it locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Set your Google API key
export GOOGLE_API_KEY='your-key-here'

# Start the web app
python app.py
```

Then open `http://localhost:5000` in your browser!

## The Rules

1. Best of 3 rounds wins
2. Rock beats scissors, scissors beats paper, paper beats rock
3. **Bomb beats everything** (except another bomb - that's a draw)
4. You can only use bomb once per game
5. Invalid moves waste your turn

## What's Cool About It

**Smart AI**: Built with Google ADK, so the referee actually understands what you're saying

**Clean Code**: The game logic is separate from the AI, making it easy to test and modify

**Web Interface**: Smooth animations and a nice purple gradient theme

## Files

```
├── app.py              # Flask web app
├── main.py             # Terminal version
├── referee_agent.py    # AI referee logic
├── game_state.py       # Game rules & state
├── templates/          # HTML interface
└── index.py            # Vercel deployment
```

## How It Works

The AI referee uses Google's ADK with 4 tools:
- `play_round` - Runs a complete round
- `validate_move` - Checks if your move is valid
- `get_game_state` - Shows current score
- `reset_game` - Starts fresh

The bot picks random moves but strategically uses its bomb (15% chance when available).

## Want to Improve It?

Ideas for the future:
- Make the bot smarter (predict your patterns)
- Add multiplayer mode
- Save game history
- Different difficulty levels
- More trash talk from the AI

## Example Game

```
You: rock
AI: Round 1 - You played ROCK, I played SCISSORS. You win! 
    Score: You 1 - Bot 0

You: bomb
AI: Round 2 - You played BOMB, I played PAPER. Boom! You win! 
    Score: You 2 - Bot 0

You: scissors  
AI: Round 3 - You played SCISSORS, I played ROCK. I win this round!
    Final: You 2 - Bot 1. YOU WIN! 🎉
```

---

Made with Google ADK and Flask
