"""
Rock-Paper-Scissors-Plus Web Application
Flask-based web interface for the game.
"""
import os
from flask import Flask, render_template, request, jsonify, session
from google import genai
from google.genai import types
from google.genai.errors import ClientError
import time
import secrets
from game_state import GameState, GameLogic, Move, RoundResult

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Store game states per session
game_sessions = {}


def get_or_create_game_state(session_id):
    """Get or create a game state for the session"""
    if session_id not in game_sessions:
        game_sessions[session_id] = GameState()
    return game_sessions[session_id]


def create_ai_client():
    """Create Google AI client"""
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not set")
    return genai.Client(api_key=api_key)


def get_ai_response(message, retry_count=0):
    """Get response from AI with retry logic"""
    try:
        client = create_ai_client()
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=message
        )
        return response.text
    except ClientError as e:
        if "RESOURCE_EXHAUSTED" in str(e) and retry_count < 2:
            time.sleep(2)
            return get_ai_response(message, retry_count + 1)
        raise


@app.route('/')
def index():
    """Main game page"""
    if 'session_id' not in session:
        session['session_id'] = secrets.token_hex(16)
    return render_template('index.html')


@app.route('/api/start', methods=['POST'])
def start_game():
    """Start a new game"""
    session_id = session.get('session_id')
    game_state = GameState()
    game_sessions[session_id] = game_state
    
    try:
        intro = get_ai_response(
            "Welcome the player to Rock-Paper-Scissors-Plus in 1-2 sentences. "
            "Be enthusiastic and brief."
        )
    except:
        intro = "Welcome to Rock-Paper-Scissors-Plus! Ready to play? Best of 3 rounds!"
    
    return jsonify({
        'success': True,
        'message': intro,
        'state': game_state.to_dict()
    })


@app.route('/api/play', methods=['POST'])
def play_round():
    """Play a round"""
    session_id = session.get('session_id')
    game_state = get_or_create_game_state(session_id)
    
    data = request.json
    user_move = data.get('move', '').lower()
    
    # Validate move
    is_valid, user_move_enum, error_msg = GameLogic.validate_move(
        user_move,
        game_state.user_bomb_used
    )
    
    if not is_valid:
        game_state.round_number += 1
        if game_state.round_number >= 3:
            game_state.game_over = True
        
        return jsonify({
            'success': False,
            'error': error_msg,
            'round': game_state.round_number,
            'game_over': game_state.game_over,
            'state': game_state.to_dict()
        })
    
    # Bot chooses move
    import random
    available_moves = [Move.ROCK, Move.PAPER, Move.SCISSORS]
    if not game_state.bot_bomb_used and random.random() < 0.15:
        available_moves.append(Move.BOMB)
    bot_move_enum = random.choice(available_moves)
    
    # Update bomb usage
    if user_move_enum == Move.BOMB:
        game_state.user_bomb_used = True
    if bot_move_enum == Move.BOMB:
        game_state.bot_bomb_used = True
    
    # Resolve round
    result = GameLogic.resolve_round(user_move_enum, bot_move_enum)
    
    # Update scores
    if result == RoundResult.USER_WIN:
        game_state.user_score += 1
    elif result == RoundResult.BOT_WIN:
        game_state.bot_score += 1
    
    # Increment round
    game_state.round_number += 1
    
    # Record history
    game_state.rounds_history.append({
        'round': game_state.round_number,
        'user_move': user_move_enum.value,
        'bot_move': bot_move_enum.value,
        'result': result.value
    })
    
    # Check if game over
    if game_state.round_number >= 3:
        game_state.game_over = True
        winner = GameLogic.determine_game_winner(game_state)
    else:
        winner = None
    
    # Generate AI commentary
    try:
        if game_state.game_over:
            prompt = f"Round {game_state.round_number}: User played {user_move_enum.value}, bot played {bot_move_enum.value}. Result: {result.value}. Final score: User {game_state.user_score} - Bot {game_state.bot_score}. Winner: {winner}. Give a brief, enthusiastic final comment (1 sentence)."
        else:
            prompt = f"Round {game_state.round_number}: User played {user_move_enum.value}, bot played {bot_move_enum.value}. Result: {result.value}. Current score: User {game_state.user_score} - Bot {game_state.bot_score}. Give a brief, fun comment (1 sentence)."
        
        commentary = get_ai_response(prompt)
    except:
        if result == RoundResult.USER_WIN:
            commentary = f"You win round {game_state.round_number}! 🎉"
        elif result == RoundResult.BOT_WIN:
            commentary = f"I win round {game_state.round_number}! 🤖"
        else:
            commentary = f"Round {game_state.round_number} is a draw!"
    
    return jsonify({
        'success': True,
        'round': game_state.round_number,
        'user_move': user_move_enum.value,
        'bot_move': bot_move_enum.value,
        'result': result.value,
        'user_score': game_state.user_score,
        'bot_score': game_state.bot_score,
        'game_over': game_state.game_over,
        'winner': winner,
        'commentary': commentary,
        'user_bomb_used': game_state.user_bomb_used,
        'bot_bomb_used': game_state.bot_bomb_used,
        'state': game_state.to_dict()
    })


@app.route('/api/reset', methods=['POST'])
def reset_game():
    """Reset the game"""
    session_id = session.get('session_id')
    game_sessions[session_id] = GameState()
    
    return jsonify({
        'success': True,
        'message': 'Game reset! Ready for a new match?'
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)

# Vercel serverless handler
handler = app
