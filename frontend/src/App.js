import React from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Toaster } from "@/components/ui/sonner";
import UserRegistration from "@/components/UserRegistration";
import OTPDashboard from "@/components/OTPDashboard";
import MagicLinkVerification from "@/components/MagicLinkVerification";
import LoginPage from "@/components/LoginPage";
import GoogleOAuthHandler from "@/components/GoogleOAuthHandler";

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<UserRegistration />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/auth/google" element={<GoogleOAuthHandler />} />
          <Route path="/registrationOfNewUser" element={<UserRegistration />} />
          <Route path="/admin" element={<OTPDashboard />} />
          <Route path="/verify" element={<MagicLinkVerification />} />
        </Routes>
      </BrowserRouter>
      <Toaster />
    </div>
  );
}

export default App;
