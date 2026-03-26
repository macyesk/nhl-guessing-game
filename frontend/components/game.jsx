import { useState, useEffect } from "react";

const API = "http://localhost:5001";

const CONSOLIDATED_CLUES = [
  {
    level: 0,
    title: "Birth Location",
    keys: ["birthCity", "birthStateOrProv", "birthCountry"],
  },
  { level: 1, title: "Birthdate", keys: ["birthDate"] },
  { level: 2, title: "Physical", keys: ["height", "weight"] },
  { level: 3, title: "Play Style", keys: ["shootingHand", "position"] },
  { level: 4, title: "Sweater Number", keys: ["sweaterNumber"] },
  { level: 5, title: "Team", keys: ["teamAbbr"] },
  { level: 6, title: "Picture", keys: ["headshot"] },
];

const getConsolidatedClues = (clues) => {
  if (!clues) return [];
  const consolidated = [];
  for (const group of CONSOLIDATED_CLUES) {
    const revealed = group.keys.every((key) => key in clues);
    if (revealed) {
      consolidated.push(group);
    }
  }
  return consolidated;
};

const formatBirthLocation = (clues) => {
  if (!clues) return "";
  const city = clues.birthCity || "";
  const state = clues.birthStateOrProv || "";
  const country = clues.birthCountry || "";
  return `${city}${state ? ", " + state : ""}, ${country}`;
};

const formatPlayStyle = (clues) => {
  if (!clues) return "";
  return `Shooting Hand: ${clues.shootingHand}, Position: ${clues.position}`;
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
  const [revealedName, setRevealedName] = useState(null);

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
    setRevealedName(null);
  };

  useEffect(() => {
    if (gameId && Object.keys(clues).length > 0 && !gameOver) {
      revealClue();
    }
  }, [gameId]);

  const revealClue = async () => {
    if (!gameId) return;
    
    const currentGroupCount = getConsolidatedClues(clues).length;
    let newGroupCount = currentGroupCount;
    let finalReached = false;

    while (newGroupCount === currentGroupCount && !finalReached) {
      const res = await fetch(`${API}/game/${gameId}/guess`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ guess: "" }),
      });
      const data = await res.json();

      if (data.clues) {
        setClues(data.clues);
        newGroupCount = getConsolidatedClues(data.clues).length;
      }
      if (data.final_guess) {
        setFinalGuess(true);
        setRevealedName(data.name);
        setMessage("Last chance! All clues are revealed.");
        finalReached = true;
      }
      if (data.game_over) {
        setGameOver(true);
        setRevealedName(data.name);
        finalReached = true;
      }
    }
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
      setRevealedName(data.name);
      setClues(data.clues);
      setMessage(`✅ Correct! The player was ${data.name}.`);
    } else if (data.game_over) {
      setGameOver(true);
      setCorrectName(data.name);
      setRevealedName(data.name);
      setClues(data.clues);
      setMessage(`❌ Game over! The player was ${data.name}.`);
    } else if (data.final_guess) {
      setFinalGuess(true);
      setRevealedName(data.name);
      setClues(data.clues);
      setMessage("Last chance! All clues are revealed.");
    } else {
      setClues(data.clues);
      setMessage("Wrong! Here's another clue.");
    }
    setGuess("");
  };

  const consolidatedClues = getConsolidatedClues(clues);

  return (
    <div style={{ maxWidth: 500, margin: "20px auto", fontFamily: "sans-serif", padding: "15px" }}>
      <h1 style={{ fontSize: "28px", marginBottom: "15px" }}>🏒 NHL Player Guesser</h1>

      {!gameId ? (
        <button
          onClick={startGame}
          style={{
            width: "100%",
            padding: "12px",
            fontSize: "16px",
            cursor: "pointer",
            backgroundColor: "#007bff",
            color: "white",
            border: "none",
            borderRadius: "5px",
          }}
        >
          Start Game
        </button>
      ) : (
        <>
          <div style={{ marginBottom: "15px" }}>
            <div style={{ textAlign: "center", marginBottom: "15px" }}>
              {clues.headshot ? (
                <img src={clues.headshot} alt="player" style={{ height: 120, borderRadius: "8px" }} />
              ) : (
                <div
                  style={{
                    height: 120,
                    width: 120,
                    backgroundColor: "#ddd",
                    borderRadius: "8px",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    color: "#999",
                    fontSize: "12px",
                    margin: "0 auto",
                  }}
                >
                  Picture Coming
                </div>
              )}
              {revealedName && (
                <div style={{ fontSize: "16px", fontWeight: "bold", marginTop: "10px", color: "white" }}>
                  {revealedName}
                </div>
              )}
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px", marginBottom: "15px" }}>
              {consolidatedClues.map((group) => (
                group.title !== "Picture" && (
                  <div
                    key={group.level}
                    style={{
                      border: "1px solid #ddd",
                      borderRadius: "6px",
                      padding: "12px",
                      backgroundColor: "#f9f9f9",
                    }}
                  >
                    <div style={{ fontSize: "13px", fontWeight: "bold", marginBottom: "8px", color: "#333" }}>
                      {group.title}
                    </div>
                    <div style={{ fontSize: "13px", color: "#555", lineHeight: "1.4" }}>
                      {group.title === "Birth Location" && formatBirthLocation(clues)}
                      {group.title === "Play Style" && formatPlayStyle(clues)}
                      {group.title === "Birthdate" && clues.birthDate}
                      {group.title === "Physical" && `${clues.height}, ${clues.weight} lbs`}
                      {group.title === "Sweater Number" && `#${clues.sweaterNumber}`}
                      {group.title === "Team" && clues.teamAbbr}
                    </div>
                  </div>
                )
              ))}
            </div>
          </div>

          {!gameOver && !revealedName && (
            <div style={{ marginBottom: "15px" }}>
              <div style={{ marginBottom: "10px" }}>
                <input
                  value={guess}
                  onChange={(e) => setGuess(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && submitGuess()}
                  placeholder="Enter player name..."
                  style={{
                    width: "100%",
                    padding: "10px",
                    fontSize: "14px",
                    border: "1px solid #ccc",
                    borderRadius: "5px",
                    boxSizing: "border-box",
                  }}
                />
              </div>
              <div style={{ display: "flex", gap: "10px" }}>
                <button
                  onClick={submitGuess}
                  style={{
                    flex: 1,
                    padding: "10px",
                    fontSize: "14px",
                    cursor: "pointer",
                    backgroundColor: "#28a745",
                    color: "white",
                    border: "none",
                    borderRadius: "5px",
                  }}
                >
                  {finalGuess ? "Final Guess" : "Guess"}
                </button>
                <button
                  onClick={revealClue}
                  style={{
                    flex: 1,
                    padding: "10px",
                    fontSize: "14px",
                    cursor: "pointer",
                    backgroundColor: "#ffc107",
                    color: "black",
                    border: "none",
                    borderRadius: "5px",
                  }}
                >
                  Reveal Clue
                </button>
              </div>
            </div>
          )}

          {(revealedName || gameOver) && (
            <button
              onClick={startGame}
              style={{
                width: "100%",
                padding: "10px",
                fontSize: "16px",
                cursor: "pointer",
                backgroundColor: "#007bff",
                color: "white",
                border: "none",
                borderRadius: "5px",
                marginBottom: "15px",
              }}
            >
              Play Again
            </button>
          )}
        </>
      )}
    </div>
  );
}
