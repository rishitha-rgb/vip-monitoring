// Login.js
import React from "react";
import LoginForm from "../components/LoginForm";

const Login = () => (
  <div
    style={{
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      height: "100vh",
      background: "#000",
    }}
  >
    <div
      style={{
        padding: 24,
        background: "#141414",
        borderRadius: 12,
        width: 400,
      }}
    >
      <h2 style={{ textAlign: "center", color: "#00bfff" }}>
        VIP Threat Monitor
      </h2>
      <p style={{ textAlign: "center", color: "#aaa" }}>
        Advanced Misinformation & Threat Detection
      </p>
      <LoginForm />
    </div>
  </div>
);

export default Login;
