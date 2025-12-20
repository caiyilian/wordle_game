from flask import Flask, render_template, request, jsonify
from game import random_word, legal_word
import uuid
import re

app = Flask(__name__)

# Global state to simulate a room/channel
global_room = {
    "current_game": None,
    "chat_history": []
}

class GameSession:
    def __init__(self, word_length=5):
        self.word_length = word_length
        self.word, self.meaning = random_word("CET4", word_length) # Defaulting to CET4
        self.word = self.word.lower()
        self.guesses = [] # List of dicts: {'word': '...', 'colors': [...]}
        self.guessed_words_set = set() # Track unique guesses
        self.max_guesses = word_length + 1
        self.status = "playing" # playing, win, loss
        self.hint_revealed = False
        self.current_hint_str = "" # Snapshot of hint

    def guess(self, word):
        word = word.lower()
        if self.status != "playing":
            return
        
        # Calculate colors
        result_colors = []
        word_incorrect = ""
        # First pass to find incorrect letters for frequency counting
        for i in range(self.word_length):
            if word[i] != self.word[i]:
                word_incorrect += self.word[i]
            else:
                word_incorrect += "_" # Placeholder for correct matches

        for i in range(self.word_length):
            letter = word[i]
            if letter == self.word[i]:
                result_colors.append("green")
            elif letter in word_incorrect:
                result_colors.append("yellow")
                word_incorrect = word_incorrect.replace(letter, "_", 1)
            else:
                result_colors.append("gray")
        
        self.guesses.append({
            "word": word,
            "colors": result_colors
        })
        self.guessed_words_set.add(word)

        if word == self.word:
            self.status = "win"
        elif len(self.guesses) >= self.max_guesses:
            self.status = "loss"

    def update_hint_snapshot(self):
        letters = set()
        for g in self.guesses:
            for char in g['word']:
                if char in self.word:
                    letters.add(char)
        
        hint = ""
        for char in self.word:
            if char in letters:
                hint += char
            else:
                hint += "*"
        self.current_hint_str = hint

def build_game_state(game):
    if not game:
        return None
    
    state = {
        'word_length': game.word_length,
        'guesses': game.guesses,
        'status': game.status,
        'max_guesses': game.max_guesses
    }
    if game.hint_revealed:
        state['hint'] = game.current_hint_str
    
    if game.status != "playing":
        state['answer'] = game.word
        state['meaning'] = game.meaning
    return state

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    text = data.get('text', '').strip()
    
    game = global_room["current_game"]
    
    # 1. Check for "猜单词" command
    start_match = re.match(r'^猜单词(\s+(\d+))?$', text)
    if start_match:
        # Start new game logic
        length_str = start_match.group(2)
        if length_str:
            word_length = int(length_str)
            if word_length < 3:
                # Treat as chat according to instruction? 
                # "必须是单纯的猜单词3个字或者猜单词加空格加一个大于等于3的数字才行"
                # If length < 3, it doesn't match the valid condition, so treat as chat.
                global_room["chat_history"].append({"sender": "Player", "text": text, "is_guess": False})
                return jsonify({
                    'type': 'chat',
                    'game_state': build_game_state(game),
                    'chat_history': global_room["chat_history"]
                })
        else:
            word_length = 5
        
        # Start new game
        global_room["current_game"] = GameSession(word_length)
        game = global_room["current_game"]
        global_room["chat_history"].append({"sender": "Player", "text": text, "is_guess": False})
        global_room["chat_history"].append({"sender": "System", "text": f"游戏开始！单词长度为 {word_length}，你有 {game.max_guesses} 次机会。", "is_guess": False})
        
        return jsonify({
            'type': 'new_game',
            'game_state': build_game_state(game),
            'chat_history': global_room["chat_history"]
        })

    # 2. Check for "结束游戏" command
    if text == "结束游戏":
        global_room["chat_history"].append({"sender": "Player", "text": text, "is_guess": False})
        if game and game.status == "playing":
            game.status = "loss" # Or special status 'stopped'
            global_room["chat_history"].append({"sender": "System", "text": "游戏已手动结束。", "is_guess": False})
            return jsonify({
                'type': 'game_end',
                'game_state': build_game_state(game),
                'chat_history': global_room["chat_history"]
            })
        else:
            # Ignore command (treat as chat)
            return jsonify({
                'type': 'chat',
                'game_state': build_game_state(game),
                'chat_history': global_room["chat_history"]
            })

    # 3. Game Logic if playing
    if game and game.status == "playing":
        # Check for hint command
        if text == "提示":
            game.update_hint_snapshot()
            game.hint_revealed = True
            global_room["chat_history"].append({"sender": "Player", "text": text, "is_guess": False})
            global_room["chat_history"].append({"sender": "System", "text": "提示已显示", "is_guess": False})
        
        # Check length match
        elif len(text) == game.word_length:
            if not text.isalpha():
                # Treat as chat
                global_room["chat_history"].append({"sender": "Player", "text": text, "is_guess": False})
            elif text.lower() in game.guessed_words_set:
                 # Duplicate
                 global_room["chat_history"].append({"sender": "Player", "text": text, "is_guess": False})
                 global_room["chat_history"].append({"sender": "System", "text": "你已经猜过这个单词了", "is_guess": False})
            elif not legal_word(text):
                 # Illegal word
                 global_room["chat_history"].append({"sender": "Player", "text": text, "is_guess": False})
                 global_room["chat_history"].append({"sender": "System", "text": "单词不合法", "is_guess": False})
            else:
                 # Valid guess
                 game.guess(text)
                 global_room["chat_history"].append({"sender": "Player", "text": text, "is_guess": True})
                 return jsonify({
                    'type': 'guess',
                    'game_state': build_game_state(game),
                    'chat_history': global_room["chat_history"]
                 })
        
        else:
            # Length doesn't match, treat as chat
            global_room["chat_history"].append({"sender": "Player", "text": text, "is_guess": False})
    
    else:
        # Not playing, treat as chat
        global_room["chat_history"].append({"sender": "Player", "text": text, "is_guess": False})

    return jsonify({
        'type': 'chat',
        'game_state': build_game_state(game),
        'chat_history': global_room["chat_history"]
    })

@app.route('/get_state', methods=['GET'])
def get_state():
    game = global_room["current_game"]
    return jsonify({
        'game_state': build_game_state(game),
        'chat_history': global_room["chat_history"]
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
