import React, { useState, useEffect } from "react";
import axios from "axios";
import Expenses from "./Expenses.jsx";

export default function Groups({ apiUrl, token }) {
  const [groups, setGroups] = useState([]);
  const [newGroup, setNewGroup] = useState({ name: "", description: "" });
  const [selectedGroup, setSelectedGroup] = useState(null);
  const [error, setError] = useState("");

  const [search, setSearch] = useState("");            //  строка поиска
  const [searchResults, setSearchResults] = useState([]); //  найденные группы

  const authHeader = { Authorization: `Bearer ${token}` };

  // загрузка групп с сервера
  const loadGroups = async () => {
    try {
      setError("");
      const { data } = await axios.get(`${apiUrl}/groups/`, {
        headers: authHeader,
      });
      setGroups(data);
      // если раньше уже была выбрана группа, попробуем её восстановить
      if (data.length > 0 && !selectedGroup) {
        setSelectedGroup(data[0]);
      }
    } catch (e) {
      setError("Не удалось загрузить группы");
    }
  };

  // вызывать при первом монтировании компонента
  useEffect(() => {
    loadGroups();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const createGroup = async (e) => {
    e.preventDefault();
    setError("");
    try {
      const { data } = await axios.post(`${apiUrl}/groups/`, newGroup, {
        headers: authHeader,
      });
      // после создания можно либо просто добавить в список,
      // либо перезагрузить группы с сервера — я добавляю вручную:
      setGroups((prev) => [...prev, data]);
      setNewGroup({ name: "", description: "" });
    } catch (e) {
      setError(e.response?.data?.detail || "Не удалось создать группу");
    }
  };

    const searchGroups = async (e) => {
    e.preventDefault();
    if (!search.trim()) return;
    setError("");
    try {
      const { data } = await axios.get(
        `${apiUrl}/groups/search`,
        {
          params: { q: search },
          headers: authHeader,
        }
      );
      setSearchResults(data);
    } catch (e) {
      setError("Не удалось выполнить поиск групп");
    }
  };

  const joinGroup = async (group) => {
    setError("");
    try {
      await axios.post(
        `${apiUrl}/groups/${group.id}/join`,
        {},
        { headers: authHeader }
      );
      // обновим список моих групп
      await loadGroups();
    } catch (e) {
      setError("Не удалось вступить в группу");
    }
  };


    return (
    <div className="groups-layout">
      <div className="groups-list">
        <h2>Группы</h2>

        {/* Создать группу */}
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

        {/* Поиск и вступление */}
        <h3 style={{ marginTop: "1.5rem" }}>Найти и вступить в группу</h3>
<div className="group-form">
  <form onSubmit={searchGroups}>
    <input
      value={search}
      onChange={(e) => setSearch(e.target.value)}
      placeholder="Часть названия"
    />
    <button type="submit">Найти</button>
  </form>
  {searchResults.length > 0 && (
    <ul style={{ marginTop: "0.5rem" }}>
      {searchResults.map((g) => (
        <li key={g.id}>
          {g.name}{" "}
          <button type="button" onClick={() => joinGroup(g)}>
            Вступить
          </button>
        </li>
      ))}
    </ul>
  )}
</div>


        {error && <div className="error">{error}</div>}

        <h4 style={{ marginTop: "1rem" }}>Мои группы</h4>
        <ul>
          {groups.map((g) => (
            <li key={g.id}>
              <button onClick={() => setSelectedGroup(g)}>{g.name}</button>
            </li>
          ))}
        </ul>
      </div>

      <div className="groups-content">
        {selectedGroup ? (
          <Expenses apiUrl={apiUrl} token={token} group={selectedGroup} />
        ) : (
          <p>Выбери группу, чтобы увидеть расходы</p>
        )}
      </div>
    </div>
  );
}

