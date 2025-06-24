document.addEventListener("DOMContentLoaded", function () {
    const gameID = "{{ game.id }}";
    const userID = "{{ request.user.id }}";
    const csrfToken = getCSRFToken();

    if (!gameID) {
        console.error("❌ Error: Game ID is missing.");
        return;
    }

    // ✅ Establish WebSocket Connection
    const socket = new WebSocket(`${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}/ws/pvp/${gameID}/`);

    socket.onopen = function () {
        console.log("🔗 WebSocket Connected to PvP Game Room:", gameID);
        displayMessage("✅ Connected to PvP Game Room!");
    };

    socket.onmessage = function (event) {
        const data = JSON.parse(event.data);
        console.log("📩 Received Message:", data);

        if (data.current_turn) {
            document.getElementById("turn-player").innerText = data.current_turn;
        }

        if (data.question) {
            document.getElementById("current-question").innerText = data.question;
            document.getElementById("answer-options").innerHTML = "";

            data.choices.forEach(choice => {
                let btn = document.createElement("button");
                btn.innerText = choice.text;
                btn.classList.add("btn", "btn-primary", "m-2");
                btn.setAttribute("data-choice-id", choice.id);

                // ✅ Use Fetch API instead of WebSocket for answer submission
                btn.addEventListener("click", function () {
                    sendAnswer(choice.id);
                });

                document.getElementById("answer-options").appendChild(btn);
            });
        }

        if (data.message) {
            displayMessage(data.message);
        }

        if (data.scores) {
            updateScores(data.scores);
        }

        if (data.game_over) {
            displayMessage(`🎉 Game Over! Winner: ${data.winner}`);
            socket.close();
        }
    };

    function sendAnswer(choiceID) {
        console.log(`🚀 Sending Answer via Fetch API: Choice ID ${choiceID}`);

        fetch(`/quizzes/pvp/play_turn/${gameID}/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken
            },
            body: JSON.stringify({ selected_choice: choiceID })
        })
        .then(response => response.json())
        .then(data => {
            console.log("✅ Response from backend:", data);
            if (data.error) {
                alert(data.error);
            } else {
                updateGameState(data);
            }
        })
        .catch(error => console.error("❌ Error submitting answer:", error));
    }

    function updateGameState(data) {
        document.getElementById("score-p1").textContent = `🏆 ${data.score_p1}`;
        document.getElementById("score-p2").textContent = `🏆 ${data.score_p2}`;
        document.getElementById("turn-player").textContent = data.next_turn;
        document.getElementById("question-counter").textContent = `${data.current_question_number} / ${data.num_questions}`;

        if (data.next_question) {
            document.getElementById("current-question").textContent = data.next_question;

            document.getElementById("answer-options").innerHTML = "";

            data.choices.forEach(choice => {
                let btn = document.createElement("button");
                btn.innerText = choice.text;
                btn.classList.add("btn", "btn-primary", "m-2");
                btn.setAttribute("data-choice-id", choice.id);

                btn.addEventListener("click", function () {
                    sendAnswer(choice.id);
                });

                document.getElementById("answer-options").appendChild(btn);
            });
        }

        if (data.game_over) {
            alert(`🎉 Game Over! Winner: ${data.winner}`);
            return;
        }
    }

    function displayMessage(message) {
        let messageBox = document.createElement("div");
        messageBox.classList.add("alert", "alert-info", "mt-3");
        messageBox.innerText = message;
        document.getElementById("quiz-container").appendChild(messageBox);

        setTimeout(() => messageBox.remove(), 5000);
    }

    function updateScores(scores) {
        let scoreText = `🏆 Scores: ${scores.player_one_username} - ${scores.player_one} | ${scores.player_two_username} - ${scores.player_two}`;
        document.getElementById("turn-status").innerText = scoreText;
    }

    function getCSRFToken() {
        return document.cookie.split("; ").find(row => row.startsWith("csrftoken"))?.split("=")[1];
    }
});
