import React from "react";
import { Routes, Route, Link, Navigate, useNavigate } from "react-router-dom";
import Home from "./pages/Home";
import ProductDetail from "./pages/ProductDetail";
import Signup from "./pages/Signup";
import Login from "./pages/Login";
import ForgotPassword from "./pages/ForgotPassword";
import Dashboard from "./pages/Dashboard";
import api from "./api/axios";

function NavBar() {
  const navigate = useNavigate();
  const isAuthed = !!localStorage.getItem("access");

  const logout = () => {
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
    navigate("/login");
  };

  return (
    <nav className="bg-white shadow">
      <div className="mx-auto max-w-6xl px-4 py-3 flex items-center justify-between">
        <Link to="/" className="font-semibold text-xl">Digital Products</Link>
        <div className="space-x-4">
          <Link to="/" className="hover:underline">Home</Link>
          {isAuthed ? (
            <>
              <Link to="/dashboard" className="hover:underline">Dashboard</Link>
              <button onClick={logout} className="px-3 py-1 bg-gray-200 rounded">Logout</button>
            </>
          ) : (
            <>
              <Link to="/signup" className="hover:underline">Signup</Link>
              <Link to="/login" className="hover:underline">Login</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}

function PrivateRoute({ children }) {
  const isAuthed = !!localStorage.getItem("access");
  return isAuthed ? children : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <div>
      <NavBar />
      <div className="mx-auto max-w-6xl px-4 py-6">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/products/:slug" element={<ProductDetail />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/login" element={<Login />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route
            path="/dashboard"
            element={
              <PrivateRoute>
                <Dashboard />
              </PrivateRoute>
            }
          />
        </Routes>
      </div>
    </div>
  );
}