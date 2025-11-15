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

  // тут тоже: у нас нет GET /expenses/group/{id}, так что пока показываем только что создали
  const createExpense = async (e) => {
    e.preventDefault();
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
      setExpenses((prev) => [data, ...prev]);
      setForm({ amount: "", description: "", category_id: "" });
    } catch (e) {
      setError(e.response?.data?.detail || "Не удалось создать расход");
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
          onChange={(e) => setForm((p) => ({ ...p, amount: e.target.value }))}
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
                    user {s.user_id}: {s.amount} ({s.is_settled ? "✔" : "—"})
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
