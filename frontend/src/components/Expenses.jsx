import React, { useState, useEffect } from "react";
import axios from "axios";

export default function Expenses({ apiUrl, token, group }) {
  const [expenses, setExpenses] = useState([]);
  const [form, setForm] = useState({
    amount: "",
    description: "",
    category_id: "",
  });
  const [error, setError] = useState("");

  const authHeader = { Authorization: `Bearer ${token}` };

  // загрузка расходов для группы
  const loadExpenses = async () => {
    try {
      setError("");
      const { data } = await axios.get(
        `${apiUrl}/expenses/group/${group.id}`,
        { headers: authHeader }
      );
      setExpenses(data);
    } catch (e) {
      setError("Не удалось загрузить расходы");
    }
  };

  // при первом рендере компонента (и при смене группы)
  useEffect(() => {
    loadExpenses();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [group.id]);

  const createExpense = async (e) => {
    e.preventDefault();
    setError("");
    try {
      const payload = {
        amount: Number(form.amount),
        description: form.description,
      };
      if (form.category_id) {
        payload.category_id = Number(form.category_id);
      }
      const { data } = await axios.post(
        `${apiUrl}/expenses/group/${group.id}`,
        payload,
        { headers: authHeader }
      );
      // можно либо заново грузить все расходы, либо просто добавить новый сверху
      setExpenses((prev) => [data, ...prev]);
      setForm({ amount: "", description: "", category_id: "" });
    } catch (e) {
      const resp = e.response?.data;
      let msg = "Не удалось создать расход";
      if (resp?.detail) {
        if (typeof resp.detail === "string") msg = resp.detail;
        else if (Array.isArray(resp.detail) && resp.detail[0]?.msg)
          msg = resp.detail[0].msg;
      }
      setError(msg);
    }
  };

  return (
    <div>
      <h2>Группа: {group.name}</h2>
      <form onSubmit={createExpense} className="expense-form">
        <input
          type="number"
          step="0.01"
          placeholder="Сумма"
          value={form.amount}
          onChange={(e) =>
            setForm((p) => ({ ...p, amount: e.target.value }))
          }
          required
        />
        <input
          placeholder="Описание"
          value={form.description}
          onChange={(e) =>
            setForm((p) => ({ ...p, description: e.target.value }))
          }
        />
        <button type="submit">Добавить расход</button>
      </form>
      {error && <div className="error">{error}</div>}

      <h3>Расходы</h3>
      {expenses.length === 0 && <p>Пока пусто</p>}
      <ul className="expense-list">
        {expenses.map((exp) => (
          <li key={exp.id} className="expense-item">
            <div>
              <strong>{exp.amount}</strong> — {exp.description}
            </div>
            {exp.shares && exp.shares.length > 0 && (
              <div className="shares">
                Доли:
                {exp.shares.map((s) => (
                  <span key={s.user_id}>
                    user {s.user_id}: {s.amount}{" "}
                    {s.is_settled ? "✔" : "—"}
                  </span>
                ))}
              </div>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
