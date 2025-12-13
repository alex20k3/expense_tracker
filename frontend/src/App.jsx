import React, { useState, useEffect } from "react";
import Auth from "./components/Auth.jsx";
import Groups from "./components/Groups.jsx";
import Karma from "./components/Karma.jsx";
import "./index.css";

const API_URL = import.meta.env.VITE_API_URL;

function App() {
  const [token, setToken] = useState(localStorage.getItem("token") || "");
  const [activeTab, setActiveTab] = useState("groups");

  useEffect(() => {
    if (token) {
      localStorage.setItem("token", token);
    } else {
      localStorage.removeItem("token");
    }
  }, [token]);

  if (!token) {
    return <Auth apiUrl={API_URL} onLogin={setToken} />;
  }

  return (
    <div className="app">
      <header className="topbar">
        <h1>Expense Tracker</h1>
        <div className="topbar-actions">
          <button
            className={activeTab === "groups" ? "active" : ""}
            onClick={() => setActiveTab("groups")}
          >
            Группы
          </button>
          <button
            className={activeTab === "karma" ? "active" : ""}
            onClick={() => setActiveTab("karma")}
          >
            Карма
          </button>
          <button onClick={() => setToken("")}>Выйти</button>
        </div>
      </header>
      <main>
        {activeTab === "groups" && <Groups apiUrl={API_URL} token={token} />}
        {activeTab === "karma" && <Karma apiUrl={API_URL} token={token} />}
      </main>
    </div>
  );
}

export default App;
