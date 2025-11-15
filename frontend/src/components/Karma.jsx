import React, { useEffect, useState } from "react";
import axios from "axios";

export default function Karma({ apiUrl, token }) {
  const [karma, setKarma] = useState(null);
  const [error, setError] = useState("");
  const authHeader = { Authorization: `Bearer ${token}` };

  useEffect(() => {
    const load = async () => {
      try {
        const { data } = await axios.get(`${apiUrl}/karma/me`, {
          headers: authHeader,
        });
        setKarma(data);
      } catch (e) {
        setError("Не удалось получить карму");
      }
    };
    load();
  }, [apiUrl, token]);

  return (
    <div>
      <h2>Твоя карма</h2>
      {error && <div className="error">{error}</div>}
      {karma ? (
        <p>
          Пользователь #{karma.user_id}: <strong>{karma.karma_points}</strong> очков
        </p>
      ) : (
        <p>Загрузка...</p>
      )}
    </div>
  );
}
