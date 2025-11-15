import React, { useEffect, useState } from "react";
import axios from "axios";
import Expenses from "./Expenses.jsx";

export default function Groups({ apiUrl, token }) {
  const [groups, setGroups] = useState([]);
  const [newGroup, setNewGroup] = useState({ name: "", description: "" });
  const [selectedGroup, setSelectedGroup] = useState(null);
  const [error, setError] = useState("");

  const authHeader = { Authorization: `Bearer ${token}` };

  // у нас пока нет эндпоинта GET /groups — на бэке его нужно будет дописать.
  // временно сделаем так: будем хранить последнюю созданную группу в стейте.
  const createGroup = async (e) => {
    e.preventDefault();
    try {
      const { data } = await axios.post(
        `${apiUrl}/groups/`,
        newGroup,
        { headers: authHeader }
      );
      setGroups((prev) => [...prev, data]);
      setNewGroup({ name: "", description: "" });
    } catch (e) {
      setError(e.response?.data?.detail || "Не удалось создать группу");
    }
  };

  return (
    <div className="groups-layout">
      <div className="groups-list">
        <h2>Группы</h2>
        <form onSubmit={createGroup} className="group-form">
          <input
            value={newGroup.name}
            onChange={(e) =>
              setNewGroup((p) => ({ ...p, name: e.target.value }))
            }
            placeholder="Название группы"
            required
          />
          <input
            value={newGroup.description}
            onChange={(e) =>
              setNewGroup((p) => ({ ...p, description: e.target.value }))
            }
            placeholder="Описание"
          />
          <button type="submit">Создать</button>
        </form>
        {error && <div className="error">{error}</div>}

        <ul>
          {groups.map((g) => (
            <li key={g.id}>
              <button onClick={() => setSelectedGroup(g)}>
                {g.name}
              </button>
            </li>
          ))}
        </ul>
      </div>
      <div className="groups-content">
        {selectedGroup ? (
          <Expenses
            apiUrl={apiUrl}
            token={token}
            group={selectedGroup}
          />
        ) : (
          <p>Выбери группу, чтобы увидеть расходы</p>
        )}
      </div>
    </div>
  );
}
