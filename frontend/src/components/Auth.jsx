import React, { useState } from "react";
import axios from "axios";

export default function Auth({ apiUrl, onLogin }) {
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    income_category: "medium",
  });
  const [error, setError] = useState("");

  const handleChange = (e) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const register = async () => {
    try {
      await axios.post(`${apiUrl}/auth/register`, {
        name: form.name,
        email: form.email,
        password: form.password,
        income_category: form.income_category,
      });
      // после регистрации сразу логиним
      await login();
    } catch (e) {
      setError(e.response?.data?.detail || "Ошибка регистрации");
    }
  };

  const login = async () => {
    try {
      // у нас login принимает email и password как form data? мы делали как query-параметры.
      // проще — отправим как form-data:
      const params = new URLSearchParams();
      params.append("email", form.email);
      params.append("password", form.password);

      const { data } = await axios.post(`${apiUrl}/auth/login`, params, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      });
      onLogin(data.access_token);
    } catch (e) {
      setError(e.response?.data?.detail || "Ошибка входа");
    }
  };

  const onSubmit = (e) => {
    e.preventDefault();
    if (mode === "login") {
      login();
    } else {
      register();
    }
  };

  return (
    <div className="auth-container">
      <h2>{mode === "login" ? "Вход" : "Регистрация"}</h2>
      <form onSubmit={onSubmit} className="auth-form">
        {mode === "register" && (
          <>
            <input
              name="name"
              placeholder="Имя"
              value={form.name}
              onChange={handleChange}
              required
            />
            <select
              name="income_category"
              value={form.income_category}
              onChange={handleChange}
            >
              <option value="low">Малый доход</option>
              <option value="medium">Средний доход</option>
              <option value="high">Высокий доход</option>
            </select>
          </>
        )}
        <input
          name="email"
          type="email"
          placeholder="Email"
          value={form.email}
          onChange={handleChange}
          required
        />
        <input
          name="password"
          type="password"
          placeholder="Пароль"
          value={form.password}
          onChange={handleChange}
          required
        />
        <button type="submit">
          {mode === "login" ? "Войти" : "Зарегистрироваться"}
        </button>
      </form>
      <p className="auth-switch">
        {mode === "login" ? (
          <>
            Нет аккаунта?{" "}
            <button type="button" onClick={() => setMode("register")}>
              Зарегистрируйся
            </button>
          </>
        ) : (
          <>
            Уже есть аккаунт?{" "}
            <button type="button" onClick={() => setMode("login")}>
              Войти
            </button>
          </>
        )}
      </p>
      {error && <div className="error">{error}</div>}
    </div>
  );
}
