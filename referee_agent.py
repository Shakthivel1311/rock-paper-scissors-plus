"""
AI Game Referee Agent using Google ADK
Handles intent understanding and response generation.
"""
import random
from google import genai
from google.genai import types
from game_state import GameState, GameLogic, Move, RoundResult


# Global game state (persists across agent calls)
game_state = GameState()


def validate_move_tool(move: str) -> dict:
    """
    Tool: Validate a user's move
    
    Args:
        move: The move string provided by the user
    
    Returns:
        Dictionary with validation result and updated state
    """
    is_valid, parsed_move, error_msg = GameLogic.validate_move(
        move, 
        game_state.user_bomb_used
    )
    
    return {
        "is_valid": is_valid,
        "parsed_move": parsed_move.value if parsed_move else None,
        "error_message": error_msg,
        "current_state": game_state.to_dict()
    }


def play_round_tool(user_move: str) -> dict:
    """
    Tool: Execute a complete round of the game
    
    Args:
        user_move: The validated user move
    
    Returns:
        Dictionary with round results and updated game state
    """
    global game_state
    
    # Validate user move
    is_valid, user_move_enum, error_msg = GameLogic.validate_move(
        user_move,
        game_state.user_bomb_used
    )
    
    if not is_valid:
        # Invalid move wastes the round
        game_state.round_number += 1
        
        # Check if game should end
        if game_state.round_number >= 3:
            game_state.game_over = True
        
        return {
            "round_number": game_state.round_number,
            "result": "invalid",
            "error_message": error_msg,
            "user_move": user_move,
            "bot_move": None,
            "user_score": game_state.user_score,
            "bot_score": game_state.bot_score,
            "game_over": game_state.game_over
        }
    
    # Bot decides its move (random selection, avoiding bomb if already used)
    available_moves = [Move.ROCK, Move.PAPER, Move.SCISSORS]
    if not game_state.bot_bomb_used:
        # Bot has a small chance to use bomb strategically
        if random.random() < 0.15:  # 15% chance
            available_moves.append(Move.BOMB)
    
    bot_move_enum = random.choice(available_moves)
    
    # Update bomb usage
    if user_move_enum == Move.BOMB:
        game_state.user_bomb_used = True
    if bot_move_enum == Move.BOMB:
        game_state.bot_bomb_used = True
    
    # Resolve the round
    result = GameLogic.resolve_round(user_move_enum, bot_move_enum)
    
    # Update scores
    if result == RoundResult.USER_WIN:
        game_state.user_score += 1
    elif result == RoundResult.BOT_WIN:
        game_state.bot_score += 1
    
    # Increment round
    game_state.round_number += 1
    
    # Record round history
    round_record = {
        "round": game_state.round_number,
        "user_move": user_move_enum.value,
        "bot_move": bot_move_enum.value,
        "result": result.value
    }
    game_state.rounds_history.append(round_record)
    
    # Check if game is over
    if game_state.round_number >= 3:
        game_state.game_over = True
    
    return {
        "round_number": game_state.round_number,
        "result": result.value,
        "user_move": user_move_enum.value,
        "bot_move": bot_move_enum.value,
        "user_score": game_state.user_score,
        "bot_score": game_state.bot_score,
        "game_over": game_state.game_over,
        "user_bomb_used": game_state.user_bomb_used,
        "bot_bomb_used": game_state.bot_bomb_used
    }


def get_game_state_tool() -> dict:
    """
    Tool: Get current game state
    
    Returns:
        Current game state as dictionary
    """
    return game_state.to_dict()


def reset_game_tool() -> dict:
    """
    Tool: Reset the game to initial state
    
    Returns:
        Confirmation of reset
    """
    global game_state
    game_state = GameState()
    return {
        "message": "Game has been reset",
        "state": game_state.to_dict()
    }


# Define tools for ADK
validate_move_declaration = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="validate_move",
            description="Validates a user's move input and checks if it's legal in the current game state",
            parameters={
                "type": "object",
                "properties": {
                    "move": {
                        "type": "string",
                        "description": "The move string provided by the user (rock, paper, scissors, or bomb)"
                    }
                },
                "required": ["move"]
            }
        )
    ]
)

play_round_declaration = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="play_round",
            description="Executes a complete round: validates user move, generates bot move, determines winner, and updates game state. Use this after user provides their move.",
            parameters={
                "type": "object",
                "properties": {
                    "user_move": {
                        "type": "string",
                        "description": "The user's move for this round"
                    }
                },
                "required": ["user_move"]
            }
        )
    ]
)

get_state_declaration = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="get_game_state",
            description="Retrieves the current game state including scores, round number, and bomb usage",
            parameters={
                "type": "object",
                "properties": {}
            }
        )
    ]
)

reset_game_declaration = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="reset_game",
            description="Resets the game to initial state for a new game",
            parameters={
                "type": "object",
                "properties": {}
            }
        )
    ]
)


# Tool mapping for execution
TOOL_FUNCTIONS = {
    "validate_move": validate_move_tool,
    "play_round": play_round_tool,
    "get_game_state": get_game_state_tool,
    "reset_game": reset_game_tool
}


def create_referee_agent(api_key: str):
    """
    Create the AI Game Referee agent with ADK
    
    Args:
        api_key: Google AI API key
    
    Returns:
        Configured genai client
    """
    client = genai.Client(api_key=api_key)
    return client


def get_system_instruction() -> str:
    """Returns the system instruction for the referee agent"""
    return """You are an AI Game Referee for Rock-Paper-Scissors-Plus.

GAME RULES (explain in ≤5 lines at start):
• Best of 3 rounds
• Valid moves: rock, paper, scissors, bomb (once per game)
• bomb beats all except bomb vs bomb (draw)
• Invalid input wastes the round
• Game ends after 3 rounds automatically

YOUR ROLE:
1. INTENT UNDERSTANDING: Interpret what the user wants to do
2. GAME LOGIC: Use tools to validate moves and execute rounds
3. RESPONSE GENERATION: Provide clear, engaging feedback

TOOL USAGE:
- Use play_round tool when user provides a move
- Tool handles all validation, bot move generation, and state updates
- Always announce: round number, both moves, round winner, current score

RESPONSE FORMAT:
- Be concise and clear
- Show round results immediately
- When game ends (after round 3), declare final winner
- Encourage the user between rounds

IMPORTANT:
- State is managed by tools, not in conversation
- Invalid moves waste a round (round count increments)
- After 3 rounds, game MUST end with final results
- Be friendly but professional"""
