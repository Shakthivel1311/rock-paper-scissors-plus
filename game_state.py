"""
Game State Management for Rock-Paper-Scissors-Plus
Handles all game state tracking and validation logic.
"""
from dataclasses import dataclass
from typing import Literal, Optional
from enum import Enum


class Move(Enum):
    """Valid game moves"""
    ROCK = "rock"
    PAPER = "paper"
    SCISSORS = "scissors"
    BOMB = "bomb"


class RoundResult(Enum):
    """Possible round outcomes"""
    USER_WIN = "user_win"
    BOT_WIN = "bot_win"
    DRAW = "draw"
    INVALID = "invalid"


@dataclass
class GameState:
    """
    Maintains complete game state across rounds.
    State persists in this object rather than just in conversation history.
    """
    round_number: int = 0
    user_score: int = 0
    bot_score: int = 0
    user_bomb_used: bool = False
    bot_bomb_used: bool = False
    game_over: bool = False
    rounds_history: list = None
    
    def __post_init__(self):
        if self.rounds_history is None:
            self.rounds_history = []
    
    def to_dict(self) -> dict:
        """Convert state to dictionary for tool returns"""
        return {
            "round_number": self.round_number,
            "user_score": self.user_score,
            "bot_score": self.bot_score,
            "user_bomb_used": self.user_bomb_used,
            "bot_bomb_used": self.bot_bomb_used,
            "game_over": self.game_over,
            "rounds_history": self.rounds_history
        }


class GameLogic:
    """
    Core game logic separated from agent/UI concerns.
    Handles move validation, round resolution, and win conditions.
    """
    
    @staticmethod
    def validate_move(move: str, player_bomb_used: bool) -> tuple[bool, Optional[Move], str]:
        """
        Validate a player's move.
        
        Returns:
            (is_valid, move_enum, error_message)
        """
        move_lower = move.lower().strip()
        
        # Check if move is valid
        try:
            parsed_move = Move(move_lower)
        except ValueError:
            return False, None, f"Invalid move '{move}'. Valid moves: rock, paper, scissors, bomb"
        
        # Check bomb usage
        if parsed_move == Move.BOMB and player_bomb_used:
            return False, None, "Bomb has already been used this game"
        
        return True, parsed_move, ""
    
    @staticmethod
    def resolve_round(user_move: Move, bot_move: Move) -> RoundResult:
        """
        Determine the winner of a round based on moves.
        
        Rules:
        - bomb beats everything except bomb
        - bomb vs bomb is a draw
        - rock > scissors > paper > rock
        """
        # Handle bomb cases
        if user_move == Move.BOMB and bot_move == Move.BOMB:
            return RoundResult.DRAW
        if user_move == Move.BOMB:
            return RoundResult.USER_WIN
        if bot_move == Move.BOMB:
            return RoundResult.BOT_WIN
        
        # Standard RPS rules
        winning_moves = {
            Move.ROCK: Move.SCISSORS,
            Move.SCISSORS: Move.PAPER,
            Move.PAPER: Move.ROCK
        }
        
        if user_move == bot_move:
            return RoundResult.DRAW
        elif winning_moves[user_move] == bot_move:
            return RoundResult.USER_WIN
        else:
            return RoundResult.BOT_WIN
    
    @staticmethod
    def determine_game_winner(state: GameState) -> str:
        """Determine final game winner"""
        if state.user_score > state.bot_score:
            return "user"
        elif state.bot_score > state.user_score:
            return "bot"
        else:
            return "draw"
