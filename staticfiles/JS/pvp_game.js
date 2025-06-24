// ✅ Extract game and user IDs from template
const gameID = "{{ game.id }}";
const userID = "{{ request.user.id }}";

// ✅ Ensure gameID is not null before proceeding
if (!gameID) {
    console.error("❌ Error: Game ID is missing.");
} else {
    // ✅ Establish WebSocket Connection with HTTPS Fix
    const socket = new WebSocket(`${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}/ws/pvp/${gameID}/`);

    socket.onopen = function () {
        console.log("🔗 WebSocket Connected to PvP Game Room:", gameID);
        displayMessage("✅ Connected to PvP Game Room!");
    };

    // ✅ Handle Incoming Messages
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
                btn.innerText = choice;
                btn.classList.add("btn", "btn-primary", "m-2");
                btn.onclick = () => sendAnswer(choice);
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

    // ✅ Improved WebSocket Reconnect Logic
    socket.onclose = function (event) {
        console.log("❌ WebSocket Disconnected", event);
        displayMessage("⚠️ Connection lost! Attempting to reconnect...");
        setTimeout(() => {
            console.log("🔄 Reconnecting to WebSocket...");
            location.reload();
        }, 5000);
    };

    socket.onerror = function (error) {
        console.error("⚠️ WebSocket Error:", error);
        displayMessage("❌ Connection error! Please refresh the page.");
    };

    // ✅ Send Answer
    function sendAnswer(answer) {
        console.log(`🚀 Sending Answer: ${answer}`);
        socket.send(JSON.stringify({ user_id: userID, answer: answer }));
    }

    // ✅ Display Messages
    function displayMessage(message) {
        let messageBox = document.createElement("div");
        messageBox.classList.add("alert", "alert-info", "mt-3");
        messageBox.innerText = message;
        document.getElementById("quiz-container").appendChild(messageBox);

        setTimeout(() => messageBox.remove(), 5000);
    }

    // ✅ Update Scoreboard
    function updateScores(scores) {
        let scoreText = `🏆 Scores: Player 1 - ${scores.player_one} | Player 2 - ${scores.player_two}`;
        document.getElementById("turn-status").innerText = scoreText;
    }
}

// ✅ Fix CSRF Token Handling
function getCSRFToken() {
    let token = document.cookie.split("; ")
        .find(row => row.startsWith("csrftoken"))
        ?.split("=")[1];

    if (!token) {
        console.error("❌ CSRF Token Missing!");
        alert("Authentication issue! Please refresh and log in.");
    }
    return token;
}

// ✅ PvP Start Button Fix
document.getElementById("start-pvp-btn").addEventListener("click", function() {
    fetch("/quizzes/pvp/start/", {  // ✅ Ensure URL is correct
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken(),
        },
        credentials: "include"  // ✅ Ensures authentication cookies are sent
    })
    .then(response => response.json())
    .then(data => {
        console.log("✅ PvP Challenge Started:", data);
        if (data.game_id) {
            window.location.href = `/quizzes/pvp/game/${data.game_id}/`;
        } else {
            alert("❌ " + data.error);
        }
    })
    .catch(error => console.error("⚠️ Error:", error));
});
