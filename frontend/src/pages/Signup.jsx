import React, { useState } from "react";
import api from "../api/axios";

export default function Signup() {
  const [step, setStep] = useState(1);
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [password, setPassword] = useState("");

  const requestOtp = async () => {
    await api.post("/auth/signup/request-otp/", { email });
    setStep(2);
  };

  const verifyOtp = async () => {
    await api.post("/auth/signup/verify-otp/", { email, code });
    setStep(3);
  };

  const setPass = async () => {
    await api.post("/auth/signup/set-password/", { email, password });
    alert("Password set. You can now login.");
    setStep(1);
  };

  return (
    <div className="max-w-md mx-auto bg-white p-6 rounded shadow">
      <h1 className="text-2xl font-semibold mb-4">Signup</h1>
      {step === 1 && (
        <div className="space-y-3">
          <input className="w-full border rounded px-3 py-2" type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
          <button onClick={requestOtp} className="w-full bg-blue-600 text-white py-2 rounded">Request OTP</button>
        </div>
      )}
      {step === 2 && (
        <div className="space-y-3">
          <p className="text-sm text-gray-600">Enter the 6-digit code sent to your email.</p>
          <input className="w-full border rounded px-3 py-2" type="text" placeholder="OTP Code" value={code} onChange={(e) => setCode(e.target.value)} />
          <button onClick={verifyOtp} className="w-full bg-blue-600 text-white py-2 rounded">Verify OTP</button>
        </div>
      )}
      {step === 3 && (
        <div className="space-y-3">
          <input className="w-full border rounded px-3 py-2" type="password" placeholder="Set Password" value={password} onChange={(e) => setPassword(e.target.value)} />
          <button onClick={setPass} className="w-full bg-green-600 text-white py-2 rounded">Set Password</button>
        </div>
      )}
    </div>
  );
}