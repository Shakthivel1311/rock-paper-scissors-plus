"""
Rock-Paper-Scissors-Plus Game Referee
Main entry point for the game.
"""
import os
import time
from google import genai
from google.genai import types
from google.genai.errors import ClientError
from referee_agent import (
    create_referee_agent,
    get_system_instruction,
    TOOL_FUNCTIONS,
    validate_move_declaration,
    play_round_declaration,
    get_state_declaration,
    reset_game_declaration,
    game_state
)


def run_game():
    """
    Main game loop - handles conversation flow with the AI referee
    """
    # Get API key from environment
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY environment variable not set")
        print("Please set it with: export GOOGLE_API_KEY='your-api-key'")
        return
    
    # Create the AI client
    client = create_referee_agent(api_key)
    
    # Initialize chat with system instruction and tools
    chat = client.chats.create(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=get_system_instruction(),
            tools=[
                validate_move_declaration,
                play_round_declaration,
                get_state_declaration,
                reset_game_declaration
            ],
            temperature=0.7
        )
    )
    
    print("=" * 60)
    print("🎮 ROCK-PAPER-SCISSORS-PLUS REFEREE 🎮")
    print("=" * 60)
    
    # Start the game with referee introduction
    try:
        response = chat.send_message("Start the game and explain the rules briefly.")
        print(f"\n🤖 Referee: {response.text}\n")
    except ClientError as e:
        if "RESOURCE_EXHAUSTED" in str(e):
            print("\n⏳ Rate limit reached. Waiting 2 seconds...\n")
            time.sleep(2)
            response = chat.send_message("Start the game and explain the rules briefly.")
            print(f"\n🤖 Referee: {response.text}\n")
        else:
            raise
    
    # Game loop
    while not game_state.game_over:
        # Get user input
        user_input = input("Your move: ").strip()
        
        if not user_input:
            print("Please enter a move!\n")
            continue
        
        # Check for quit command
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("\n👋 Thanks for playing! Goodbye!")
            break
        
        # Send message to agent with retry logic
        try:
            response = chat.send_message(user_input)
        except ClientError as e:
            if "RESOURCE_EXHAUSTED" in str(e):
                print("\n⏳ Rate limit reached. Waiting 2 seconds and retrying...\n")
                time.sleep(2)
                response = chat.send_message(user_input)
            else:
                print(f"\n❌ Error: {e}")
                continue
        
        # Handle tool calls
        while response.candidates[0].content.parts:
            part = response.candidates[0].content.parts[0]
            
            # Check if there's a function call
            if hasattr(part, 'function_call') and part.function_call:
                function_call = part.function_call
                function_name = function_call.name
                function_args = dict(function_call.args)
                
                # Execute the tool
                if function_name in TOOL_FUNCTIONS:
                    result = TOOL_FUNCTIONS[function_name](**function_args)
                    
                    # Send result back to model with retry logic
                    try:
                        response = chat.send_message(
                            types.Part.from_function_response(
                                name=function_name,
                                response=result
                            )
                        )
                    except ClientError as e:
                        if "RESOURCE_EXHAUSTED" in str(e):
                            print("⏳ Rate limit. Waiting 2 seconds...")
                            time.sleep(2)
                            response = chat.send_message(
                                types.Part.from_function_response(
                                    name=function_name,
                                    response=result
                                )
                            )
                        else:
                            raise
                else:
                    print(f"Unknown function: {function_name}")
                    break
            else:
                # No more function calls, show the response
                if response.text:
                    print(f"\n🤖 Referee: {response.text}\n")
                break
    
    # Game ended
    if game_state.game_over:
        print("\n" + "=" * 60)
        print("🏁 GAME OVER 🏁")
        print("=" * 60)
        print(f"Final Score - You: {game_state.user_score} | Bot: {game_state.bot_score}")
        
        from game_state import GameLogic
        winner = GameLogic.determine_game_winner(game_state)
        if winner == "user":
            print("🎉 YOU WIN! Congratulations! 🎉")
        elif winner == "bot":
            print("🤖 BOT WINS! Better luck next time!")
        else:
            print("🤝 IT'S A DRAW! Well played!")
        print("=" * 60)


if __name__ == "__main__":
    run_game()
