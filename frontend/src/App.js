import React from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Sidebar from "@/components/Sidebar";
import Dashboard from "@/pages/Dashboard";
import UserManagement from "@/pages/UserManagement";
import PaymentManagement from "@/pages/PaymentManagement";
import BroadcastMessages from "@/pages/BroadcastMessages";

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <div className="flex min-h-screen bg-gray-50">
          {/* Sidebar */}
          <Sidebar />
          
          {/* Main Content */}
          <div className="flex-1 ml-64">
            <div className="p-8">
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/users" element={<UserManagement />} />
                <Route path="/payments" element={<PaymentManagement />} />
                <Route path="/broadcast" element={<BroadcastMessages />} />
              </Routes>
            </div>
          </div>
        </div>
      </BrowserRouter>
    </div>
  );
}

export default App;