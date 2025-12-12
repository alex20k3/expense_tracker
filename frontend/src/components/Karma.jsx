import React, { useEffect, useState } from "react";
import axios from "axios";

export default function Karma({ apiUrl, token, groups }) {
  const [karma, setKarma] = useState(0);
  const [error, setError] = useState("");
  const [info, setInfo] = useState("");

  const authHeader = { Authorization: `Bearer ${token}` };

  const loadMe = async () => {
    try {
      const { data } = await axios.get(`${apiUrl}/karma/me`, {
        headers: authHeader,
      });
      setKarma(data.karma_points ?? 0);
    } catch (e) {
      setError("Не удалось загрузить карму");
    }
  };

  useEffect(() => {
    loadMe();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const forgiveAllDebts = async () => {
    setError("");
    setInfo("");
    try {
      await axios.post(
        `${apiUrl}/karma/use/forgive-debt`,
        {},
        { headers: authHeader }
      );
      setInfo("Долги погашены за 100 кармы");
      await loadMe();
    } catch (e) {
      setError(e.response?.data?.detail || "Не удалось погасить долги");
    }
  };

  const lowerCoeff = async () => {
    setError("");
    setInfo("");
    try {
      await axios.post(
        `${apiUrl}/karma/use/lower-coeff`,
        {},
        { headers: authHeader }
      );
      setInfo("Коэффициент понижен за 150 кармы");
      await loadMe();
    } catch (e) {
      setError(e.response?.data?.detail || "Не удалось понизить коэффициент");
    }
  };

  return (
    <div>
      <h2>Карма</h2>

      <div style={{ marginBottom: "12px" }}>
        Текущая карма: <strong>{karma}</strong>
      </div>

      <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
        <button type="button" onClick={forgiveAllDebts}>
          Погасить все долги (100)
        </button>
        <button type="button" onClick={lowerCoeff}>
          Понизить коэффициент (150)
        </button>
      </div>

      {info && <div style={{ marginTop: "10px" }}>{info}</div>}
      {error && <div className="error" style={{ marginTop: "10px" }}>{error}</div>}
    </div>
  );
}
