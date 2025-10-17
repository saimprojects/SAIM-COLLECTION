import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api/axios";

export default function Home() {
  const [products, setProducts] = useState([]);

  useEffect(() => {
    api.get("/products/").then(({ data }) => setProducts(data));
  }, []);

  return (
    <div>
      <h1 className="text-2xl font-semibold mb-4">Products</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {products.map((p) => (
          <div key={p.id} className="bg-white shadow rounded p-4">
            <h2 className="text-xl font-medium">{p.title}</h2>
            <p className="text-sm text-gray-600 line-clamp-3">{p.description}</p>
            <div className="mt-2 flex items-center justify-between">
              <span className="font-semibold">${p.price}</span>
              <Link to={`/products/${p.slug}`} className="px-3 py-1 bg-blue-600 text-white rounded">View</Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}