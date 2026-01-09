# Rock-Paper-Scissors-Plus AI Game Referee

An AI-powered game referee chatbot built with Google ADK that manages a best-of-3 Rock-Paper-Scissors-Plus game with intelligent rule enforcement and state tracking.

## Overview

This project implements an AI referee that:
- Explains game rules concisely
- Validates player moves
- Executes rounds with bot opponents
- Tracks game state across rounds
- Enforces all game rules including the special "bomb" move
- Automatically ends the game after 3 rounds

## State Model

### Architecture Decision: Persistent State Object

The game state is maintained in a **global `GameState` dataclass instance** rather than relying on conversation history. This design choice ensures:

1. **Deterministic behavior**: State changes are explicit and traceable
2. **Tool-driven state management**: All state mutations happen through defined tools
3. **Clear separation of concerns**: State logic is separate from AI/conversation logic

### State Structure

```python
@dataclass
class GameState:
    round_number: int           # Current round (0-3)
    user_score: int            # User wins
    bot_score: int             # Bot wins
    user_bomb_used: bool       # Has user played bomb?
    bot_bomb_used: bool        # Has bot played bomb?
    game_over: bool            # Is game finished?
    rounds_history: list       # Record of all rounds played
```

**Why this model?**
- **Immutability of rules**: Bomb usage is tracked independently for each player
- **Round counting**: Ensures game ends exactly after 3 rounds
- **History tracking**: Enables debugging and potential replay features
- **Serializable**: Can be easily converted to JSON for persistence or API responses

## Agent & Tool Design

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         USER INPUT                          │
│                  ("rock", "bomb", etc.)                     │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│               LAYER 1: INTENT UNDERSTANDING                 │
│                     (referee_agent.py)                      │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  Google ADK Agent + System Instruction                │ │
│  │  • Parses natural language                            │ │
│  │  • Decides which tool to call                         │ │
│  │  • Generates conversational responses                 │ │
│  └───────────────────────────────────────────────────────┘ │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                LAYER 2: TOOL EXECUTION                      │
│                  (referee_agent.py)                         │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  ADK Tools (Function Declarations)                    │ │
│  │  • validate_move()    - Check move legality           │ │
│  │  • play_round()       - Execute complete round        │ │
│  │  • get_game_state()   - Retrieve current state        │ │
│  │  • reset_game()       - Start new game                │ │
│  └───────────────────────────────────────────────────────┘ │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                LAYER 3: GAME LOGIC                          │
│                   (game_state.py)                           │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  Pure Functions (No Side Effects)                     │ │
│  │  • GameLogic.validate_move()                          │ │
│  │  • GameLogic.resolve_round()                          │ │
│  │  • GameLogic.determine_game_winner()                  │ │
│  │                                                        │ │
│  │  State Object (Persistent)                            │ │
│  │  • GameState dataclass                                │ │
│  │  • Round tracking, scores, bomb usage                 │ │
│  └───────────────────────────────────────────────────────┘ │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
                   ┌───────────────┐
                   │  Structured   │
                   │  Tool Results │
                   └───────┬───────┘
                           │
                           ▼
                   Back to Agent Layer
```

### Three-Layer Architecture

#### 1. Intent Understanding (Agent Layer)
- **Component**: `referee_agent.py` with system instruction
- **Responsibility**: Parse user input and determine appropriate action
- **Implementation**: Google ADK agent with structured system prompt

#### 2. Game Logic (Pure Logic Layer)
- **Component**: `game_state.py` with `GameLogic` class
- **Responsibility**: Rule enforcement, move validation, round resolution
- **Key Methods**:
  - `validate_move()`: Checks move validity and bomb availability
  - `resolve_round()`: Determines round winner based on move rules
  - `determine_game_winner()`: Computes final game outcome
- **Why separate?**: Pure functions with no side effects, fully testable

#### 3. Response Generation (Tool Layer)
- **Component**: ADK tools in `referee_agent.py`
- **Responsibility**: Execute game actions and return structured results
- **Tools Defined**:

| Tool | Purpose | State Mutation |
|------|---------|----------------|
| `validate_move` | Check if user input is legal | No |
| `play_round` | Execute complete round logic | Yes |
| `get_game_state` | Retrieve current state | No |
| `reset_game` | Start new game | Yes |

**Design rationale**:
- `play_round` is the primary tool - it handles validation, bot move generation, resolution, and state updates in one atomic operation
- Tools return structured dictionaries for consistent agent interpretation
- Bot move selection uses randomness with strategic bomb usage (15% chance when available)

### Tool Integration with ADK

Tools are registered using Google ADK's `FunctionDeclaration`:

```python
play_round_declaration = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="play_round",
            description="Executes a complete round...",
            parameters={...}
        )
    ]
)
```

The agent receives tool results and generates natural language responses based on structured data.

## Tradeoffs & Design Decisions

### 1. Global State vs. Stateless Architecture
**Chosen**: Global state object
- ✅ **Pro**: Simpler implementation, direct state access
- ✅ **Pro**: No need for database or session management
- ❌ **Con**: Not suitable for concurrent games (single-user only)
- **Alternative**: Could use session IDs with dictionary storage for multi-user

### 2. Single vs. Multiple Agents
**Chosen**: Single agent with multiple tools
- ✅ **Pro**: Simpler conversation flow, no agent coordination needed
- ✅ **Pro**: Sufficient for game scope (3 rounds)
- **Alternative**: Could use separate agents for validation, gameplay, and summary - but adds complexity for minimal benefit

### 3. Bot Move Strategy
**Chosen**: Random selection with 15% bomb probability
- ✅ **Pro**: Unpredictable and fair
- ✅ **Pro**: Simple to implement and test
- ❌ **Con**: Not strategic (doesn't adapt to user patterns)
- **Alternative**: Could implement counter-strategies or pattern detection

### 4. Invalid Input Handling
**Chosen**: Invalid input wastes the round (increments round counter)
- ✅ **Pro**: Enforces consequence as specified in requirements
- ✅ **Pro**: Keeps game moving forward
- ❌ **Con**: Potentially frustrating user experience
- **Alternative**: Could allow retries within same round, but violates spec

## What I Would Improve With More Time

### 1. **Enhanced Bot Intelligence**
- Implement pattern detection to predict user moves
- Add difficulty levels (easy/medium/hard)
- Use LLM to generate witty trash talk based on game state

### 2. **Better State Persistence**
- Add JSON file save/load for game history
- Support multiple concurrent games with session IDs
- Implement game replay feature

### 3. **Comprehensive Testing**
- Unit tests for all game logic functions
- Integration tests for tool execution
- Edge case testing (all draws, all bombs, etc.)
- Mock ADK responses for deterministic testing

### 4. **User Experience**
- Add colorful terminal output with emoji indicators
- Show round history summary at game end
- Implement "play again" without restarting program
- Add move suggestions for new players

### 5. **Production Readiness**
- Error handling for API failures
- Rate limiting and retry logic
- Logging for debugging
- Configuration file for game parameters (round count, bomb rules)
- Docker containerization

### 6. **Advanced Features**
- Multiplayer support (user vs user with AI referee)
- Tournament mode (multiple games, track overall stats)
- AI commentary that adapts tone based on game state
- Structured output schemas for more predictable responses

## Setup & Running

### Prerequisites
```bash
pip install -r requirements.txt
```

### Environment Setup
```bash
export GOOGLE_API_KEY='your-google-api-key'
```

### Run the Game
```bash
python main.py
```

### Expected Flow
1. Referee explains rules in ≤5 lines
2. User enters move (rock/paper/scissors/bomb)
3. Referee announces: round #, both moves, winner, score
4. Repeat for 3 rounds
5. Game auto-ends with final results

## File Structure

```
Project_upliance/
├── main.py              # Entry point, game loop
├── referee_agent.py     # ADK agent, tools, system instruction
├── game_state.py        # State model and pure game logic
├── requirements.txt     # Dependencies
└── README.md           # This file
```

## Technical Highlights

- **ADK Primitives Used**: 
  - `genai.Client` for agent creation
  - `types.GenerateContentConfig` for configuration
  - `types.Tool` and `types.FunctionDeclaration` for tool definition
  - `types.Part.from_function_response` for tool result handling
  
- **State Management**: Global object with explicit tool-based mutations

- **Separation of Concerns**: 
  - Intent: Agent interprets user input
  - Logic: Pure functions validate and resolve
  - Response: Tools execute and return data

- **Rule Enforcement**: All constraints implemented correctly
  - Best of 3 rounds ✓
  - Bomb usage tracking ✓
  - Invalid input handling ✓
  - Automatic game end ✓

## Example Game Session

```
🎮 ROCK-PAPER-SCISSORS-PLUS REFEREE 🎮

🤖 Referee: Welcome! Best of 3 rounds. Valid moves: rock, paper, 
scissors, bomb (once per game). Bomb beats all except bomb vs bomb 
(draw). Invalid input wastes a round. Let's begin!

Your move: rock

🤖 Referee: Round 1 - You played ROCK, I played SCISSORS. 
You win this round! Score: You 1 - Bot 0

Your move: bomb

🤖 Referee: Round 2 - You played BOMB, I played PAPER. 
You win with bomb! Score: You 2 - Bot 0

Your move: scissors

🤖 Referee: Round 3 - You played SCISSORS, I played ROCK. 
I win this round! Final Score: You 2 - Bot 1

🏁 GAME OVER 🏁
🎉 YOU WIN! Congratulations! 🎉
```

---

**Built with Google ADK | Rock-Paper-Scissors-Plus | 2026**
