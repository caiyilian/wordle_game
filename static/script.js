document.addEventListener('DOMContentLoaded', () => {
    const sendBtn = document.getElementById('sendBtn');
    const messageInput = document.getElementById('messageInput');
    const gameGrid = document.getElementById('game-grid');
    const hintContainer = document.getElementById('hint-container');
    const hintSection = document.getElementById('hint-section');
    const gameLabel = document.getElementById('game-label');
    const resultMessage = document.getElementById('result-message');
    const chatHistory = document.getElementById('chat-history');

    let wordLength = 5;
    let maxGuesses = 6;

    // Load initial state
    fetchState();

    // Send Message
    sendBtn.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    function fetchState() {
        fetch('/get_state')
            .then(response => response.json())
            .then(data => {
                renderChat(data.chat_history);
                if (data.game_state) {
                    updateGameState(data.game_state);
                }
            })
            .catch(err => console.error(err));
    }

    function sendMessage() {
        const text = messageInput.value.trim();
        if (!text) return;

        fetch('/send_message', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: text
            })
        })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    appendChatMessage('System', data.error);
                    return;
                }

                // Handle New Game or Game End or Chat
                if (data.type === 'new_game') {
                    // Clear UI for new game
                    resultMessage.textContent = '';
                    hintContainer.innerHTML = '';
                    hintSection.style.display = 'none'; // Hide hint section initially
                }

                renderChat(data.chat_history);

                if (data.game_state) {
                    updateGameState(data.game_state);
                }

                messageInput.value = '';
            })
            .catch(err => {
                console.error(err);
                appendChatMessage('System', "发送失败");
            });
    }

    function renderEmptyGrid() {
        gameGrid.innerHTML = '';
        for (let i = 0; i < maxGuesses; i++) {
            const row = document.createElement('div');
            row.className = 'grid-row';
            for (let j = 0; j < wordLength; j++) {
                const cell = document.createElement('div');
                cell.className = 'grid-cell';
                row.appendChild(cell);
            }
            gameGrid.appendChild(row);
        }
    }

    function updateGameState(gameState) {
        if (!gameState) return;

        wordLength = gameState.word_length;
        maxGuesses = gameState.max_guesses;

        // Render Grid
        gameGrid.innerHTML = '';
        const guesses = gameState.guesses;

        // Show/Hide Game Label
        if (gameState.status === 'playing' || guesses.length > 0) {
            gameLabel.style.display = 'block';
        } else {
            gameLabel.style.display = 'none';
        }

        // Render guessed rows
        guesses.forEach(guess => {
            const row = document.createElement('div');
            row.className = 'grid-row';

            for (let i = 0; i < wordLength; i++) {
                const cell = document.createElement('div');
                const colorClass = `cell-${guess.colors[i]}`; // green, yellow, gray
                cell.className = `grid-cell ${colorClass}`;
                cell.textContent = guess.word[i];
                row.appendChild(cell);
            }
            gameGrid.appendChild(row);
        });

        // Render remaining empty rows
        if (gameState.status === 'playing') {
            const remaining = maxGuesses - guesses.length;
            for (let i = 0; i < remaining; i++) {
                const row = document.createElement('div');
                row.className = 'grid-row';
                for (let j = 0; j < wordLength; j++) {
                    const cell = document.createElement('div');
                    cell.className = 'grid-cell';
                    row.appendChild(cell);
                }
                gameGrid.appendChild(row);
            }
        }

        // Update Hint
        hintContainer.innerHTML = '';
        if (gameState.hint) {
            hintSection.style.display = 'flex'; // Show section
            // Render hint as blocks
            const hintStr = gameState.hint; // e.g., "*a*b*"
            for (let i = 0; i < hintStr.length; i++) {
                const char = hintStr[i];
                const cell = document.createElement('div');
                cell.className = 'grid-cell';
                if (char !== '*') {
                    cell.classList.add('cell-green'); // Known letters are green
                    cell.textContent = char.toUpperCase();
                } else {
                    // Empty/Unknown
                    // Maybe just empty white block
                }
                hintContainer.appendChild(cell);
            }
        } else {
            // No hint available yet or cleared
            if (gameState.status === 'playing') {
                // Keep section hidden if no hint
                // But wait, if we had a hint before, we might want to keep showing it?
                // The backend state sends hint only if hint_revealed is true.
                // So if it's missing, it means not revealed.
                hintSection.style.display = 'none';
            }
        }

        // Update Status
        if (gameState.status === 'win') {
            resultMessage.innerHTML = `🎉 恭喜你猜出了单词！<br>单词: ${gameState.answer}<br>释义: ${gameState.meaning}`;
            resultMessage.style.color = 'green';
        } else if (gameState.status === 'loss') {
            resultMessage.innerHTML = `😞 很遗憾，你没有猜出单词。<br>单词: ${gameState.answer}<br>释义: ${gameState.meaning}`;
            resultMessage.style.color = 'red';
        } else {
            resultMessage.textContent = '';
        }
    }

    function renderChat(history) {
        chatHistory.innerHTML = '';
        history.forEach(msg => {
            appendChatMessage(msg.sender, msg.text, msg.is_guess);
        });
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    function appendChatMessage(sender, text, isGuess = false) {
        const msgDiv = document.createElement('div');
        let typeClass = 'msg-chat';
        if (sender === 'System') typeClass = 'msg-system';
        else if (isGuess) typeClass = 'msg-guess';

        msgDiv.className = `message-item ${typeClass}`;

        const senderDiv = document.createElement('div');
        senderDiv.className = 'sender-name';
        senderDiv.textContent = sender;

        const textDiv = document.createElement('div');
        textDiv.textContent = text;

        msgDiv.appendChild(senderDiv);
        msgDiv.appendChild(textDiv);

        chatHistory.appendChild(msgDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }
});
