import type { ReactNode } from "react";
import { Link, useLocation } from "react-router-dom";

type Props = {
  children: ReactNode;
};

export function AppLayout({ children }: Props) {
  const location = useLocation();
  return (
    <div className="app-shell">
      <div className="app-shell__glow app-shell__glow--left" />
      <div className="app-shell__glow app-shell__glow--right" />
      <div className="shell">
        <header className="topbar">
          <div>
            <p className="eyebrow">Operations cockpit</p>
            <h1>7Po8</h1>
            <p className="subtitle">Local-first AI-assisted monitoring platform</p>
          </div>
          <nav aria-label="Primary" className="topnav">
            <Link className={location.pathname === "/" ? "active" : ""} to="/">
              Waves
            </Link>
          </nav>
        </header>
        <main>{children}</main>
      </div>
    </div>
  );
}
