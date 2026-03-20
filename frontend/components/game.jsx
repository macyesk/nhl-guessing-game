import { useState } from "react";

const API = "http://localhost:5001";

const CLUE_LABELS = {
  birthCountry: "Country",
  height: "Height",
  weight: "Weight (lbs)",
  sweaterNumber: "Sweater #",
  position: "Position",
  teamAbbr: "Team",
  headshot: "Headshot",
};

export default function Game() {
  const [gameId, setGameId] = useState(null);
  const [clues, setClues] = useState({});
  const [guess, setGuess] = useState("");
  const [message, setMessage] = useState("");
  const [finalGuess, setFinalGuess] = useState(false);
  const [gameOver, setGameOver] = useState(false);
  const [correctName, setCorrectName] = useState(null);
  const [won, setWon] = useState(false);

  const startGame = async () => {
    const res = await fetch(`${API}/game/new`);
    const data = await res.json();
    setGameId(data.game_id);
    setClues(data.clues);
    setGuess("");
    setMessage("");
    setFinalGuess(false);
    setGameOver(false);
    setCorrectName(null);
    setWon(false);
  };

  const submitGuess = async () => {
    if (!guess.trim()) return;
    const res = await fetch(`${API}/game/${gameId}/guess`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ guess }),
    });
    const data = await res.json();

    if (data.correct) {
      setWon(true);
      setGameOver(true);
      setCorrectName(data.name);
      setClues(data.clues);
      setMessage(`✅ Correct! The player was ${data.name}.`);
    } else if (data.game_over) {
      setGameOver(true);
      setCorrectName(data.name);
      setClues(data.clues);
      setMessage(`❌ Game over! The player was ${data.name}.`);
    } else if (data.final_guess) {
      setFinalGuess(true);
      setClues(data.clues);
      setMessage("Last chance! All clues are revealed.");
    } else {
      setClues(data.clues);
      setMessage("Wrong! Here's another clue.");
    }
    setGuess("");
  };

  return (
    <div
      style={{ maxWidth: 500, margin: "40px auto", fontFamily: "sans-serif" }}
    >
      <h1>🏒 NHL Player Guesser</h1>

      {!gameId ? (
        <button onClick={startGame}>Start Game</button>
      ) : (
        <>
          <h3>Clues:</h3>
          <ul>
            {Object.entries(clues).map(([key, value]) => (
              <li key={key}>
                <strong>{CLUE_LABELS[key] || key}:</strong>{" "}
                {key === "headshot" ? (
                  <img src={value} alt="headshot" style={{ height: 80 }} />
                ) : (
                  value
                )}
              </li>
            ))}
          </ul>

          {!gameOver && (
            <div>
              <input
                value={guess}
                onChange={(e) => setGuess(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && submitGuess()}
                placeholder="Enter player name..."
                style={{ marginRight: 8 }}
              />
              <button onClick={submitGuess}>
                {finalGuess ? "Final Guess" : "Guess"}
              </button>
            </div>
          )}

          {message && <p>{message}</p>}

          {gameOver && (
            <button onClick={startGame} style={{ marginTop: 16 }}>
              Play Again
            </button>
          )}
        </>
      )}
    </div>
  );
}
