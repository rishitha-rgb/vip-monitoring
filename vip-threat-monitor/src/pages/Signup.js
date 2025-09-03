// Signup.js
import React from "react";
import SignupForm from "../components/SignupForm";

const Signup = () => (
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
      <h2 style={{ textAlign: "center", color: "#00bfff" }}>Create Account</h2>
      <SignupForm />
    </div>
  </div>
);

export default Signup;
