import React, { useEffect, useState } from "react";
import api from "../api/axios";

export default function Dashboard() {
  const [orders, setOrders] = useState([]);

  useEffect(() => {
    api.get("/orders/").then(({ data }) => setOrders(data));
  }, []);

  const download = (linkId) => {
    window.location.href = `http://localhost:8000/api/orders/download/${linkId}/`;
  };

  return (
    <div>
      <h1 className="text-2xl font-semibold mb-4">My Orders</h1>
      <div className="space-y-3">
        {orders.map((o) => (
          <div key={o.id} className="bg-white p-4 rounded shadow">
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium">{o.product_title}</div>
                <div className="text-sm text-gray-600">Status: {o.status}</div>
              </div>
              {o.download_link ? (
                <button
                  onClick={() => download(o.download_link.id)}
                  className="px-3 py-1 bg-blue-600 text-white rounded"
                >
                  Download ({o.download_link.remaining_downloads} left)
                </button>
              ) : (
                <span className="text-sm text-gray-600">No download available</span>
              )}
            </div>
            {o.download_link && o.download_link.external_warning && (
              <div className="mt-2 text-xs text-yellow-700">Note: External link provided.</div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}