import React, { useState, useEffect } from "react";
import api from "../api/axios";

export default function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [token, setToken] = useState("");
  const [newPassword, setNewPassword] = useState("");

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const e = params.get("email");
    const t = params.get("token");
    if (e) setEmail(e);
    if (t) setToken(t);
  }, []);

  const requestReset = async () => {
    await api.post("/auth/password/reset/", { email });
    alert("If the email exists, a reset link has been sent.");
  };

  const confirmReset = async () => {
    await api.post("/auth/password/reset/confirm/", { email, token, new_password: newPassword });
    alert("Password reset successful. You can now login.");
  };

  return (
    <div className="max-w-md mx-auto bg-white p-6 rounded shadow space-y-4">
      <h1 className="text-2xl font-semibold">Forgot Password</h1>
      <div className="space-y-2">
        <input className="w-full border rounded px-3 py-2" type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
        <button onClick={requestReset} className="w-full bg-blue-600 text-white py-2 rounded">Request Reset Link</button>
      </div>
      <div className="space-y-2">
        <input className="w-full border rounded px-3 py-2" type="text" placeholder="Token" value={token} onChange={(e) => setToken(e.target.value)} />
        <input className="w-full border rounded px-3 py-2" type="password" placeholder="New Password" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} />
        <button onClick={confirmReset} className="w-full bg-green-600 text-white py-2 rounded">Set New Password</button>
      </div>
    </div>
  );
}