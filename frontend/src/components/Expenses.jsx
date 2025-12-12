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
  const [payAmounts, setPayAmounts] = useState({}); // ключ: `${expenseId}-${userId}`

  const authHeader = { Authorization: `Bearer ${token}` };


  const calcDaysLeft = (dueDateStr) => {
  if (!dueDateStr) return null;
  const due = new Date(dueDateStr);
  const today = new Date();
  // сбрасываем время, чтобы считать "по дням"
  due.setHours(0,0,0,0);
  today.setHours(0,0,0,0);
  const diffMs = due - today;
  return Math.round(diffMs / (1000 * 60 * 60 * 24)); // может быть отрицательным
};


  // загрузка расходов...


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

    const handleDeleteExpense = async (expenseId) => {
    setError("");
    try {
      await axios.delete(`${apiUrl}/expenses/${expenseId}`, {
        headers: authHeader,
      });
      setExpenses((prev) => prev.filter((e) => e.id !== expenseId));
    } catch (e) {
      setError("Не удалось удалить расход");
    }
  };

    const handlePayShare = async (expense, share, value) => {
  const num = Number(value);

  if (!value || isNaN(num) || num <= 0) {
    setError("Введите корректное число");
    return;
  }

  const remaining = share.amount - (share.paid_amount ?? 0);

  if (num > remaining + 1e-6) {
    setError("Введите корректное число (сумма больше остатка долга)");
    return;
  }

  setError("");

  try {
    await axios.post(
      `${apiUrl}/expenses/${expense.id}/settle`,
      { amount: num },
      {
        headers: {
          ...authHeader,
          "Content-Type": "application/json",
        },
      }
    );

    // перезагружаем расходы, чтобы подхватить новый paid_amount / is_settled
    await loadExpenses();

    // очищаем поле ввода для этой доли
    const key = `${expense.id}-${share.user_id}`;
    setPayAmounts((prev) => ({ ...prev, [key]: "" }));
  } catch (e) {
    setError("Не удалось оплатить долю");
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
            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <div>
  <strong>{exp.amount}</strong> — {exp.description}

  {exp.due_date && (() => {
    const daysLeft = calcDaysLeft(exp.due_date);
    const karmaHint = daysLeft ?? 0; // столько кармы будет при ПОЛНОМ закрытии сегодня

    return (
      <div style={{ fontSize: "0.9em", opacity: 0.85, marginTop: "4px" }}>
        Дедлайн: {new Date(exp.due_date).toLocaleDateString()} ·{" "}
        {daysLeft >= 0 ? `осталось ${daysLeft} дн.` : `просрочено на ${Math.abs(daysLeft)} дн.`} ·{" "}
        Карма при закрытии сегодня: {karmaHint >= 0 ? `+${karmaHint}` : `${karmaHint}`}
      </div>
    );
  })()}
</div>

              <button
                type="button"
                onClick={() => handleDeleteExpense(exp.id)}
              >
                Удалить
              </button>
            </div>

            {exp.shares && exp.shares.length > 0 && (
  <div className="shares">
    Доли:
    {exp.shares.map((s) => {
      const key = `${exp.id}-${s.user_id}`;
      const value = payAmounts[key] || "";

      const paid = s.paid_amount ?? 0;
      const remaining = (s.amount - paid).toFixed(2);

      return (
        <div key={key} style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
          <span>
            {s.user_name}: долг {s.amount} (оплачено {paid}, осталось {remaining}){" "}
            {s.is_settled ? "✔ оплачено" : "— не оплачено"}
          </span>

          {!s.is_settled && (
            <>
              <input
                type="number"
                step="0.01"
                style={{ width: "80px" }}
                placeholder="Сумма"
                value={value}
                onChange={(e) =>
                  setPayAmounts((prev) => ({
                    ...prev,
                    [key]: e.target.value,
                  }))
                }
              />
              <button
                type="button"
                onClick={() => handlePayShare(exp, s, value)}
              >
                Оплатить
              </button>
            </>
          )}
        </div>
      );
    })}
  </div>
)}

          </li>
        ))}
      </ul>
    </div>
  );
}
