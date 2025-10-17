import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import api from "../api/axios";

export default function ProductDetail() {
  const { slug } = useParams();
  const [product, setProduct] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    api.get(`/products/${slug}/`).then(({ data }) => setProduct(data));
  }, [slug]);

  const buy = async () => {
    try {
      await api.post("/orders/create/", { product: product.id });
      alert("Order created and pending approval.");
      navigate("/dashboard");
    } catch (e) {
      alert("Please login to place an order.");
      navigate("/login");
    }
  };

  if (!product) return <div>Loading...</div>;

  return (
    <div className="bg-white shadow rounded p-4">
      <h1 className="text-2xl font-semibold mb-2">{product.title}</h1>
      <p className="text-gray-700">{product.description}</p>
      <div className="mt-4 flex items-center justify-between">
        <span className="font-semibold">${product.price}</span>
        <button onClick={buy} className="px-4 py-2 bg-green-600 text-white rounded">Buy</button>
      </div>
    </div>
  );
}