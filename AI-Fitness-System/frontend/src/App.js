import React, { useState } from "react";
import { UserProvider, useUser } from "./context/UserContext";
import Navbar from "./components/Navbar";
import Dashboard from "./pages/Dashboard";
import Profile from "./pages/Profile";
import FoodTracking from "./pages/FoodTracking";
import ActivityTracking from "./pages/ActivityTracking";
import Recommendations from "./pages/Recommendations";
import Progress from "./pages/Progress";

function Shell() {
  const { userId, user, logout } = useUser();
  const [tab, setTab] = useState(userId ? "dashboard" : "profile");

  const goToProfile = () => setTab("profile");

  const handleLogout = () => {
    logout();
    setTab("profile");
  };

  let content;
  switch (tab) {
    case "food":
      content = <FoodTracking />;
      break;
    case "activity":
      content = <ActivityTracking />;
      break;
    case "recommendations":
      content = <Recommendations />;
      break;
    case "progress":
      content = <Progress />;
      break;
    case "profile":
      content = <Profile onSaved={() => setTab("dashboard")} />;
      break;
    default:
      content = <Dashboard onGoToProfile={goToProfile} />;
  }

  return (
    <div className="app-shell">
      <Navbar active={tab} onChange={setTab} userName={user?.name} onLogout={handleLogout} />
      <main className="app-main">{content}</main>
      <footer className="app-footer">
        AI-Powered Adaptive Fitness &amp; Nutrition Recommendation System
      </footer>
    </div>
  );
}

export default function App() {
  return (
    <UserProvider>
      <Shell />
    </UserProvider>
  );
}
