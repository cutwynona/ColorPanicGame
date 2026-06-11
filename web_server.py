"""
╔══════════════════════════════════════════════════════════════╗
║         COLOR PANIC - WebSocket Bridge Server               ║
║         Jalankan ini untuk akses via browser                ║
║         Komunikasi Data - Informatika 2026                  ║
╚══════════════════════════════════════════════════════════════╝

Cara pakai:
  1. Jalankan server.py dulu
  2. Jalankan web_server.py
  3. Buka browser: http://localhost:8080
"""

import asyncio
import websockets
import json
import socket
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import os

# HTML game interface
HTML_CONTENT = r"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🌈 Color Panic — Multiplayer Game</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;700&display=swap');

  :root {
    --bg:       #06060c;
    --surface:  #0e0e1e;
    --card:     #141430;
    --border:   rgba(120,100,255,0.1);
    --border-hi:rgba(120,100,255,0.3);
    --text:     #eeeef8;
    --muted:    #6a6a9a;
    --accent:   #7c5af0;
    --accent2:  #a78bfa;
    --accent3:  #c4b5fd;
    --success:  #22d37f;
    --danger:   #ff5a6e;
    --warn:     #f0b922;

    --red:    #ff4d5a; --blue:   #4d8aff; --green:  #22d37f; --yellow: #ffd633;
    --orange: #ff8c00; --purple: #b34dff; --pink:   #ff66cc; --white:  #f0f0ff;

    --glass: rgba(18,18,42,0.7);
    --glass-border: rgba(120,100,255,0.12);
    --r: 16px; --r-lg: 24px;
  }

  * { margin:0; padding:0; box-sizing:border-box; }

  body {
    font-family:'Space Grotesk',sans-serif;
    background:var(--bg);
    color:var(--text);
    min-height:100vh;
    overflow-x:hidden;
  }

  /* ── BG EFFECTS ── */
  body::before {
    content:''; position:fixed; inset:0; z-index:0; pointer-events:none;
    background:
      radial-gradient(ellipse 800px 600px at 10% 15%, rgba(255, 77, 90, 0.15) 0%, transparent 70%),
      radial-gradient(ellipse 700px 700px at 90% 80%, rgba(77, 138, 255, 0.15) 0%, transparent 70%),
      radial-gradient(ellipse 600px 500px at 50% 10%, rgba(179, 77, 255, 0.15) 0%, transparent 70%),
      radial-gradient(ellipse 600px 600px at 80% 20%, rgba(34, 211, 127, 0.12) 0%, transparent 70%);
    animation: bgPulse 15s ease-in-out infinite alternate;
  }
  @keyframes bgPulse { 0%{opacity:.8} 50%{opacity:1.1} 100%{opacity:.6} }
  #particles { position:fixed; inset:0; z-index:0; pointer-events:none; }

  /* ── HEADER ── */
  header {
    position:relative; z-index:1; text-align:center;
    padding:28px 20px 18px;
    background:linear-gradient(180deg, rgba(10,5,25,0.95) 0%, transparent 100%);
    border-bottom:2px solid rgba(120,100,255,0.25);
    box-shadow: 0 4px 20px rgba(124, 90, 240, 0.15);
    backdrop-filter:blur(20px);
  }
  header h1 {
    font-size:2.6rem; font-weight:800; letter-spacing:-0.04em;
    background:linear-gradient(135deg, #ff6ec4, #7873f5 50%, #4adede);
    background-size:200% 200%;
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    animation:gradFlow 5s ease infinite;
    filter:drop-shadow(0 0 30px rgba(120,115,245,0.3));
  }
  @keyframes gradFlow { 0%,100%{background-position:0% 50%} 50%{background-position:100% 50%} }
  header p { color:var(--muted); font-size:.82rem; margin-top:4px; letter-spacing:.06em; text-transform:uppercase; }

  /* ── LAYOUT ── */
  .app { position:relative; z-index:1; max-width:960px; margin:0 auto; padding:20px 16px; }

  /* ── SCREENS ── */
  .screen { display:none !important; }
  .screen.active { display:block !important; }

  /* ── STATUS BAR ── */
  #status-bar {
    display:flex; align-items:center; gap:10px;
    padding:10px 18px; background:var(--glass); backdrop-filter:blur(16px);
    border:1px solid var(--glass-border); border-radius:var(--r);
    margin-bottom:18px; font-size:.83rem; color:var(--muted);
  }
  .dot { width:8px; height:8px; border-radius:50%; background:var(--danger); transition:.3s; box-shadow:0 0 6px rgba(255,90,110,.5); }
  .dot.connected { background:var(--success); box-shadow:0 0 10px rgba(34,211,127,.6); animation:dotPulse 2s ease-in-out infinite; }
  @keyframes dotPulse { 0%,100%{box-shadow:0 0 6px rgba(34,211,127,.4)} 50%{box-shadow:0 0 16px rgba(34,211,127,.9)} }

  /* ── JOIN SCREEN ── */
  #join-screen.active {
    display:flex !important; flex-direction:column; align-items:center;
    justify-content:center; min-height:72vh; gap:20px;
    position: relative;
  }
  
  .join-blob {
    position: absolute; width: 300px; height: 300px; border-radius: 50%;
    filter: blur(120px); opacity: 0.12; z-index: 0;
    animation: blobMove 10s ease-in-out infinite alternate;
    pointer-events: none;
  }
  .join-blob-1 { background: var(--accent); top: 10%; left: 20%; }
  .join-blob-2 { background: var(--danger); bottom: 10%; right: 20%; }
  @keyframes blobMove {
    0% { transform: translate(0, 0) scale(1); }
    100% { transform: translate(40px, -40px) scale(1.15); }
  }

  .join-card {
    background: rgba(16, 16, 36, 0.65);
    backdrop-filter: blur(40px); -webkit-backdrop-filter: blur(40px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 28px;
    padding: 45px 40px; width: 100%; max-width: 440px; text-align: center;
    box-shadow: 
      0 20px 50px rgba(0,0,0,0.5), 
      inset 0 1px 0 rgba(255,255,255,0.1),
      0 0 40px rgba(124, 90, 240, 0.05);
    animation: cardIn .8s cubic-bezier(.16,1,.3,1);
    position: relative; overflow: hidden;
    z-index: 1;
  }
  .join-card::before {
    content: ''; position: absolute; top: 0; left: -50%; width: 200%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.03), transparent);
    transform: rotate(45deg); transition: 0.5s; pointer-events: none;
  }
  .join-card:hover::before { left: 100%; transition: 0.8s ease-in-out; }
  
  .login-badge-wrap {
    display: flex; justify-content: center; margin-bottom: 20px;
  }
  .login-badge {
    width: 68px; height: 68px; border-radius: 50%;
    background: linear-gradient(135deg, rgba(124,90,240,0.2), rgba(255,90,110,0.1));
    border: 1px solid rgba(124, 90, 240, 0.3);
    display: flex; align-items: center; justify-content: center;
    font-size: 2.2rem;
    box-shadow: 0 10px 25px rgba(124,90,240,0.25), inset 0 2px 5px rgba(255,255,255,0.2);
    animation: floatBadge 4s ease-in-out infinite alternate;
  }
  @keyframes floatBadge {
    0% { transform: translateY(0) rotate(0deg); }
    100% { transform: translateY(-6px) rotate(5deg); }
  }

  .join-card h2 {
    font-size: 1.8rem; margin-bottom: 8px; font-weight: 800;
    background: linear-gradient(135deg, #fff 40%, var(--accent3));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    letter-spacing: -0.02em;
  }
  .join-card p { color: var(--muted); font-size: .84rem; margin-bottom: 30px; line-height: 1.5; }
  
  .input-group { margin-bottom: 22px; text-align: left; }
  .input-group label {
    display: flex; align-items: center; gap: 6px;
    font-size: .7rem; color: var(--accent2); margin-bottom: 8px;
    font-weight: 700; text-transform: uppercase; letter-spacing: .1em;
  }
  .label-dot {
    width: 6px; height: 6px; border-radius: 50%; background: var(--accent);
    box-shadow: 0 0 8px var(--accent);
  }
  .input-group input {
    width: 100%; padding: 14px 18px; 
    background: rgba(10, 10, 24, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.08); 
    border-radius: 14px; color: var(--text);
    font-family: inherit; font-size: 0.95rem; transition: all 0.3s ease;
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.4);
  }
  .input-group input:focus {
    outline: none; 
    border-color: var(--accent); 
    box-shadow: 0 0 15px rgba(124,90,240,0.2), inset 0 1px 2px rgba(0,0,0,0.5); 
    background: rgba(10, 10, 26, 0.95);
    transform: translateY(-1px);
  }
  .input-group input::placeholder {
    color: rgba(255,255,255,0.25);
  }
  
  #join-btn {
    padding: 15px 28px;
    border-radius: 14px;
    font-size: 1rem;
    background: linear-gradient(135deg, var(--accent), #9370ff, #ff5a6e);
    background-size: 200% auto;
    box-shadow: 0 6px 20px rgba(124,90,240,0.3);
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  }
  #join-btn:hover {
    background-position: right center;
    transform: translateY(-3px) scale(1.02);
    box-shadow: 0 10px 25px rgba(124,90,240,0.45), 0 0 15px rgba(255,90,110,0.2);
  }
  #join-btn:active {
    transform: translateY(-1px) scale(0.99);
  }

  /* ── BUTTONS ── */
  .btn {
    padding:14px 28px; border:none; border-radius:12px;
    font-family:inherit; font-size:1rem; font-weight:700;
    cursor:pointer; transition:.2s cubic-bezier(.16,1,.3,1);
    position:relative; overflow:hidden;
  }
  .btn-primary {
    background:linear-gradient(135deg, var(--accent), #9370ff, #7c5af0);
    background-size:200% 200%; animation:btnGrad 4s ease infinite;
    color:white; width:100%; box-shadow:0 4px 20px rgba(124,90,240,.35);
    letter-spacing:.02em;
  }
  @keyframes btnGrad { 0%,100%{background-position:0% 50%} 50%{background-position:100% 50%} }
  .btn-primary:hover { transform:translateY(-2px); box-shadow:0 8px 32px rgba(124,90,240,.5); }
  .btn-primary:active { transform:translateY(0); }
  .btn-primary:disabled { opacity:.5; cursor:not-allowed; transform:none; box-shadow:none; }
  .btn-primary::after {
    content:''; position:absolute; inset:0;
    background:linear-gradient(135deg, transparent 40%, rgba(255,255,255,.12) 50%, transparent 60%);
    background-size:250%; background-position:100%; transition:background-position .6s;
  }
  .btn-primary:hover::after { background-position:0; }

  /* ── GAME LAYOUT ── */
  #game-screen.active {
    display:grid !important; grid-template-columns:1fr 300px; gap:20px;
    animation:fadeUp .5s cubic-bezier(.16,1,.3,1);
  }
  @keyframes fadeUp { from{opacity:0;transform:translateY(20px)} to{opacity:1;transform:none} }

  .main-panel { display:flex; flex-direction:column; gap:14px; }

  /* ── ROUND INFO ── */
  .round-info {
    display:flex; align-items:center; gap:14px;
    padding:14px 22px; background:var(--glass); backdrop-filter:blur(16px);
    border-radius:var(--r); border:1px solid var(--glass-border);
  }
  .round-badge { font-size:.78rem; color:var(--accent2); font-family:'JetBrains Mono',monospace; font-weight:700; white-space:nowrap; }
  .score-display { font-size:1.1rem; font-weight:800; color:var(--warn); text-shadow:0 0 14px rgba(240,185,34,.35); white-space:nowrap; }
  .score-display.pop { animation:scorePop .4s cubic-bezier(.34,1.56,.64,1); }
  @keyframes scorePop { 0%{transform:scale(1)} 50%{transform:scale(1.3)} 100%{transform:scale(1)} }

  /* ── TIMER BAR ── */
  #timer-bar-wrap { flex:1; height:6px; background:rgba(120,100,255,.08); border-radius:3px; overflow:hidden; }
  #timer-bar {
    height:100%; border-radius:3px; transition:width .1s linear; width:100%;
    background:linear-gradient(90deg, var(--success) 0%, var(--warn) 50%, var(--danger) 100%);
    box-shadow:0 0 10px rgba(34,211,127,.3);
  }

  /* ── SEQUENCE DOTS ── */
  .sequence-bar {
    display: none !important;
  }

  /* ── COLOR DISPLAY ── */
  #color-display {
    border-radius:var(--r-lg); height:auto; min-height:240px; padding:20px 10px;
    display:flex; align-items:center; justify-content:center; flex-direction:column; gap:10px;
    background:var(--card); border:2px solid var(--border);
    transition:all .3s cubic-bezier(.34,1.56,.64,1);
    position:relative; overflow:hidden;
    box-shadow:0 8px 40px rgba(0,0,0,.25);
  }
  #color-display.pulse { animation:colorPop .5s cubic-bezier(.34,1.56,.64,1); }
  @keyframes colorPop { 0%{transform:scale(1)} 35%{transform:scale(1.05)} 100%{transform:scale(1)} }
  #color-display .waiting-text { color:var(--muted); font-size:1rem; }
  #color-display::after {
    content:''; position:absolute; inset:0;
    background:radial-gradient(ellipse at center, rgba(255,255,255,.06) 0%, transparent 70%);
    pointer-events:none;
  }

  /* ── TARGET SEQUENCE CARDS ── */
  .target-title {
    font-size: 1.1rem; font-weight: 700; color: var(--accent2); margin-top: 5px;
    letter-spacing: .02em; text-transform: uppercase; z-index: 1;
  }
  .target-list {
    display: flex; flex-wrap: wrap; justify-content: center; align-items: center; gap: 10px;
    padding: 10px 10px; width: 100%; z-index: 1;
  }
  .target-item {
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    padding: 8px 12px; border-radius: 16px; min-width: 90px; height: 90px;
    border: 2px solid rgba(255,255,255,0.05);
    transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
    box-shadow: 0 8px 24px rgba(0,0,0,0.3);
    color: #fff; font-weight: 800; font-size: 0.85rem; text-shadow: 0 1px 3px rgba(0,0,0,0.5);
    position: relative;
  }
  .target-item .emoji { font-size: 1.5rem; margin-bottom: 2px; }
  .target-item.active {
    transform: scale(1.15) translateY(-5px);
    border-color: #fff !important;
    box-shadow: 0 15px 30px var(--current-color, currentColor), inset 0 1px 2px rgba(255,255,255,0.4);
    animation: targetActivePulse 1.2s ease-in-out infinite alternate;
  }
  .target-item.wrong {
    animation: wrongShake 0.5s ease;
  }
  @keyframes targetActivePulse {
    0% { filter: brightness(1); }
    100% { filter: brightness(1.25); }
  }
  .target-item.cleared {
    opacity: 0.20 !important;
    transform: scale(0.9);
    filter: grayscale(0.9) !important;
    box-shadow: none !important;
    border-color: transparent !important;
  }
  .target-item.cleared::after {
    content: '✓'; position: absolute; inset: 0;
    display: flex; align-items: center; justify-content: center;
    font-size: 2.5rem; color: var(--success); font-weight: 900;
    text-shadow: 0 0 8px rgba(0,0,0,0.8);
    filter: none !important;
  }
  .target-arrow {
    font-size: 1.4rem; color: rgba(120, 100, 255, 0.4);
    transition: all 0.3s ease;
    text-shadow: 0 0 10px rgba(120, 100, 255, 0.2);
    user-select: none;
    z-index: 1;
  }
  .target-arrow.cleared {
    color: var(--success);
    text-shadow: 0 0 12px var(--success);
  }
  .target-footer {
    font-size: 0.8rem; color: var(--muted); margin-bottom: 5px;
    font-family: 'JetBrains Mono', monospace; z-index: 1;
  }

  /* ── COLOR BUTTONS ── */
  .color-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:10px; }
  .color-btn {
    height:82px; border:3px solid rgba(255,255,255,.06);
    border-radius:var(--r); font-family:inherit; font-size:.8rem; font-weight:700;
    cursor:pointer; transition:all .2s cubic-bezier(.16,1,.3,1);
    display:flex; flex-direction:column; align-items:center; justify-content:center;
    gap:3px; position:relative; overflow:hidden;
    box-shadow:0 4px 16px rgba(0,0,0,.25); letter-spacing:.03em;
  }
  .color-btn::before {
    content:''; position:absolute; inset:0;
    background:linear-gradient(180deg, rgba(255,255,255,.15) 0%, transparent 50%);
    pointer-events:none;
  }
  .color-btn:hover {
    transform:translateY(-5px) scale(1.05); filter:brightness(1.15);
    box-shadow:0 12px 30px rgba(0,0,0,.35); border-color:rgba(255,255,255,.25);
  }
  .color-btn:active { transform:scale(.93); }
  .color-btn.correct { animation:correctGlow .6s ease; }
  .color-btn.wrong { animation:wrongShake .5s ease; }
  .color-btn.answered {
    opacity:.5; pointer-events:none; transform:scale(.95);
    filter:grayscale(.5);
  }
  .color-btn .key-hint {
    position:absolute; top:4px; right:6px; font-size:.6rem; opacity:.5;
    font-family:'JetBrains Mono',monospace; background:rgba(0,0,0,.25);
    padding:1px 5px; border-radius:4px;
  }

  @keyframes correctGlow {
    0%,100% { filter:brightness(1); box-shadow:0 4px 16px rgba(0,0,0,.25); }
    50% { filter:brightness(2) saturate(1.5); box-shadow:0 0 50px rgba(34,211,127,.6); }
  }
  @keyframes wrongShake {
    0%,100%{transform:translateX(0)} 20%{transform:translateX(-10px)} 40%{transform:translateX(10px)} 60%{transform:translateX(-6px)} 80%{transform:translateX(6px)}
  }

  .btn-MERAH  { background:linear-gradient(145deg,#ff5a5a,#d02828); color:white; }
  .btn-BIRU   { background:linear-gradient(145deg,#5a90ff,#2850d0); color:white; }
  .btn-HIJAU  { background:linear-gradient(145deg,#30e88a,#15a855); color:#0d2a1a; }
  .btn-KUNING { background:linear-gradient(145deg,#ffe040,#d8b010); color:#2a2000; }
  .btn-ORANGE { background:linear-gradient(145deg,#ff9a20,#d06800); color:white; }
  .btn-UNGU   { background:linear-gradient(145deg,#c060ff,#8020d0); color:white; }
  .btn-PINK   { background:linear-gradient(145deg,#ff78d0,#d04898); color:white; }
  .btn-PUTIH  { background:linear-gradient(145deg,#f8f8ff,#d0d0e8); color:#1a1a2e; border-color:rgba(120,100,255,.12); }

  /* ── FEEDBACK ── */
  #feedback {
    padding:14px 22px; border-radius:var(--r); font-weight:600; text-align:center;
    font-size:.95rem; min-height:50px; display:flex; align-items:center; justify-content:center;
    background:var(--glass); backdrop-filter:blur(12px);
    border:1px solid var(--glass-border); color:var(--muted);
    transition:all .35s cubic-bezier(.16,1,.3,1);
  }
  #feedback.correct { background:rgba(34,211,127,.12); border-color:rgba(34,211,127,.4); color:var(--success); box-shadow:0 0 24px rgba(34,211,127,.12); }
  #feedback.wrong { background:rgba(255,90,110,.12); border-color:rgba(255,90,110,.4); color:var(--danger); box-shadow:0 0 24px rgba(255,90,110,.12); }
  #feedback.timeout { background:rgba(240,185,34,.1); border-color:rgba(240,185,34,.3); color:var(--warn); }

  /* ── SIDEBAR ── */
  .sidebar { display:flex; flex-direction:column; gap:16px; }
  .sidebar-card {
    background:var(--glass); backdrop-filter:blur(16px);
    border:1px solid var(--glass-border); border-radius:var(--r-lg);
    padding:20px; box-shadow:0 4px 24px rgba(0,0,0,.18);
  }
  .sidebar-card h3 {
    font-size:.7rem; text-transform:uppercase; letter-spacing:.14em;
    color:var(--accent2); margin-bottom:14px; font-weight:600;
  }

  .lb-entry {
    display:flex; align-items:center; gap:10px;
    padding:9px 8px; border-bottom:1px solid rgba(120,100,255,.06);
    border-radius:8px; transition:all 0.2s ease;
  }
  .lb-entry:hover { background:rgba(124,90,240,.05); }
  .lb-entry:last-child { border-bottom:none; }
  .lb-entry.me {
    background: rgba(124, 90, 240, 0.12);
    border: 1px solid rgba(124, 90, 240, 0.35);
  }
  .lb-rank {
    font-size: 0.8rem; font-weight: 800;
    width: 22px; height: 22px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    color: var(--muted);
    font-family: 'JetBrains Mono', monospace;
    flex-shrink: 0;
  }
  .lb-rank.rank-1 {
    background: #ffd700; color: #000;
    box-shadow: 0 0 8px rgba(255, 215, 0, 0.4);
    font-weight: 900;
  }
  .lb-rank.rank-2 {
    background: #c0c0c0; color: #000;
    box-shadow: 0 0 6px rgba(192, 192, 192, 0.3);
    font-weight: 900;
  }
  .lb-rank.rank-3 {
    background: #cd7f32; color: #000;
    box-shadow: 0 0 6px rgba(205, 127, 50, 0.3);
    font-weight: 900;
  }
  .lb-avatar {
    width: 30px; height: 30px; border-radius: 50%;
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.12);
    display: flex; align-items: center; justify-content: center;
    font-weight: 800; font-size: 0.75rem; color: #fff;
    flex-shrink: 0;
  }
  .lb-name { font-weight: 600; font-size: .84rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .lb-name.me { color: var(--accent3); }
  .lb-info-col { flex: 1; display: flex; flex-direction: column; min-width: 0; }
  .player-used-powers { display: flex; gap: 6px; margin-top: 4px; align-items: center; }
  .used-badge { font-size: 0.75rem; opacity: 0.15; filter: grayscale(1); transition: all 0.3s ease; }
  .used-badge.active { opacity: 1; filter: none; }
  .lb-score { font-family: 'JetBrains Mono', monospace; font-size: .86rem; color: var(--warn); font-weight: 700; flex-shrink: 0; }

  #game-log {
    height:150px; overflow-y:auto; font-size:.74rem;
    font-family:'JetBrains Mono',monospace; color:var(--muted);
    display:flex; flex-direction:column; gap:4px; padding-right:4px;
  }
  #game-log::-webkit-scrollbar { width:3px; }
  #game-log::-webkit-scrollbar-thumb { background:var(--border-hi); border-radius:4px; }
  .log-entry { line-height:1.5; animation:logIn .25s ease; }
  @keyframes logIn { from{opacity:0;transform:translateX(-6px)} to{opacity:1;transform:none} }
  .log-entry.success { color:var(--success); }
  .log-entry.danger { color:var(--danger); }
  .log-entry.warn { color:var(--warn); }
  .log-entry.info { color:#8ab4ff; }

  .chat-input-row { display:flex; gap:8px; margin-top:10px; }
  .chat-input-row input {
    flex:1; padding:9px 14px; background:rgba(14,14,30,.9);
    border:1px solid var(--border); border-radius:10px; color:var(--text);
    font-family:inherit; font-size:.8rem; transition:.25s;
  }
  .chat-input-row input:focus { outline:none; border-color:var(--accent); box-shadow:0 0 0 2px rgba(124,90,240,.15); }
  .chat-send {
    padding:9px 16px; background:linear-gradient(135deg,var(--accent),#9370ff);
    border:none; border-radius:10px; color:white; cursor:pointer;
    font-size:.82rem; font-weight:700; transition:.2s;
    box-shadow:0 2px 10px rgba(124,90,240,.25);
  }
  .chat-send:hover { transform:translateY(-1px); box-shadow:0 4px 14px rgba(124,90,240,.4); }

  /* ── COUNTDOWN ── */
  #countdown-overlay {
    display:none; position:fixed; inset:0;
    background:rgba(6,6,12,.95); backdrop-filter:blur(24px);
    z-index:100; align-items:center; justify-content:center; flex-direction:column;
  }
  #countdown-overlay.show { display:flex; }
  #countdown-num {
    font-size:10rem; font-weight:800;
    animation:countPop .8s cubic-bezier(.34,1.56,.64,1);
    background:linear-gradient(135deg,#ff6ec4,#7873f5,#4adede);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    filter:drop-shadow(0 0 60px rgba(120,115,245,.5));
  }
  #countdown-overlay p { color:var(--muted); font-size:1.1rem; margin-top:16px; letter-spacing:.1em; text-transform:uppercase; }
  @keyframes countPop {
    0%{transform:scale(.2) rotate(-15deg);opacity:0}
    60%{transform:scale(1.2) rotate(3deg)}
    100%{transform:scale(1) rotate(0);opacity:1}
  }

  /* ── ROUND OVERLAY (NEW) ── */
  .round-overlay {
    display: none; position: fixed; inset: 0;
    background: rgba(6,6,12,0.85); backdrop-filter: blur(20px);
    z-index: 99; align-items: center; justify-content: center; flex-direction: column;
    opacity: 0; transition: opacity 0.3s ease;
  }
  .round-overlay.show {
    display: flex; opacity: 1;
  }
  .round-title-glow {
    font-size: 8rem; font-weight: 900;
    background: linear-gradient(135deg, var(--accent2), var(--accent3), #4adede);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    filter: drop-shadow(0 0 50px rgba(124,90,240,0.5));
    transform: scale(0.7); opacity: 0;
    transition: all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
  }
  .round-overlay.show .round-title-glow {
    transform: scale(1); opacity: 1;
  }
  .round-overlay p {
    color: var(--muted); font-size: 1.2rem; margin-top: 10px;
    letter-spacing: .15em; text-transform: uppercase;
    opacity: 0; transform: translateY(10px);
    transition: all 0.5s ease 0.2s;
  }
  .round-overlay.show p {
    opacity: 1; transform: translateY(0);
  }

  /* ── GAME OVER ── */
  #gameover-screen.active {
    display:flex !important; flex-direction:column; align-items:center;
    gap:28px; padding:48px 0; animation:fadeUp .6s cubic-bezier(.16,1,.3,1);
  }
  .final-card {
    background:rgba(18, 18, 38, 0.7); backdrop-filter:blur(30px);
    border:1px solid rgba(255, 255, 255, 0.08); border-radius:28px;
    padding:40px 30px; width:100%; max-width:550px; text-align:center;
    box-shadow:0 20px 60px rgba(0,0,0,.5), 0 0 0 1px rgba(120,100,255,.05) inset;
  }
  .final-card h2 {
    font-size:2.4rem; margin-bottom:28px;
    background:linear-gradient(135deg,#ffd700,#ffaa00,#ffd700);
    background-size:200%; animation:goldShine 3s ease infinite;
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    filter:drop-shadow(0 0 20px rgba(255,215,0,.3));
  }
  @keyframes goldShine { 0%,100%{background-position:0% 50%} 50%{background-position:100% 50%} }

  /* ── PODIUM LEADERS ── */
  .podium-container {
    display: flex; align-items: flex-end; justify-content: center; gap: 24px;
    margin: 40px 0 25px; padding-bottom: 20px;
    border-bottom: 1px solid rgba(120, 100, 255, 0.1);
  }
  .podium-step {
    display: flex; flex-direction: column; align-items: center;
    position: relative; width: 100px;
  }
  .podium-step.step-1 { order: 2; z-index: 2; }
  .podium-step.step-2 { order: 1; }
  .podium-step.step-3 { order: 3; }
  
  .podium-avatar {
    width: 68px; height: 68px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-weight: 800; color: #fff; margin-bottom: 10px;
    background: rgba(255, 255, 255, 0.05);
    border: 3px solid #fff;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
    position: relative;
    transition: all 0.3s ease;
  }
  .podium-step.step-1 .podium-avatar {
    width: 86px; height: 86px;
    border-color: #ffd700;
    box-shadow: 0 0 25px rgba(255, 215, 0, 0.35);
  }
  .podium-step.step-2 .podium-avatar {
    border-color: #c0c0c0;
    box-shadow: 0 0 15px rgba(192, 192, 192, 0.2);
  }
  .podium-step.step-3 .podium-avatar {
    border-color: #cd7f32;
    box-shadow: 0 0 15px rgba(205, 127, 50, 0.15);
  }
  
  .podium-rank-badge {
    position: absolute; bottom: -8px;
    width: 24px; height: 24px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.75rem; font-weight: 800; color: #000;
  }
  .podium-step.step-1 .podium-rank-badge { background: #ffd700; }
  .podium-step.step-2 .podium-rank-badge { background: #c0c0c0; }
  .podium-step.step-3 .podium-rank-badge { background: #cd7f32; }

  .crown-icon {
    font-size: 2.2rem; position: absolute; top: -30px;
    filter: drop-shadow(0 4px 8px rgba(255, 215, 0, 0.4));
    animation: crownFloat 2s ease-in-out infinite alternate;
  }
  @keyframes crownFloat {
    0% { transform: translateY(0) rotate(-4deg); }
    100% { transform: translateY(-4px) rotate(4deg); }
  }

  .podium-name {
    font-size: 0.9rem; font-weight: 700; color: var(--text);
    max-width: 100px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
  }
  .podium-name.me { color: var(--accent3); }
  .podium-score {
    font-size: 0.85rem; font-weight: 800; color: var(--warn);
    font-family: 'JetBrains Mono', monospace; margin-top: 2px;
  }
  .avatar-text {
    text-shadow: 0 2px 4px rgba(0,0,0,0.5); text-transform: uppercase;
  }
  .podium-step.step-1 .avatar-text { font-size: 1.4rem; }
  .podium-step.step-2 .avatar-text, .podium-step.step-3 .avatar-text { font-size: 1.15rem; }

  /* ── LEADERBOARD LIST ── */
  .lb-list-container {
    display: flex; flex-direction: column; gap: 8px;
    width: 100%; max-width: 480px; margin: 10px auto 0;
  }
  .lb-list-item {
    display: flex; align-items: center; padding: 12px 18px;
    border-radius: 16px; background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.05);
    transition: all 0.3s ease;
    opacity: 0; transform: translateY(15px);
    animation: listSlideUp 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
  }
  @keyframes listSlideUp {
    to { opacity: 1; transform: translateY(0); }
  }
  .lb-list-item:nth-child(1) { animation-delay: 0.1s; }
  .lb-list-item:nth-child(2) { animation-delay: 0.15s; }
  .lb-list-item:nth-child(3) { animation-delay: 0.2s; }
  .lb-list-item:nth-child(4) { animation-delay: 0.25s; }
  .lb-list-item:nth-child(5) { animation-delay: 0.3s; }
  .lb-list-item:nth-child(6) { animation-delay: 0.35s; }
  .lb-list-item:nth-child(7) { animation-delay: 0.4s; }
  .lb-list-item:nth-child(8) { animation-delay: 0.45s; }

  .lb-list-item:hover {
    transform: translateY(-2px);
    background: rgba(124, 90, 240, 0.08);
    border-color: rgba(124, 90, 240, 0.2);
  }
  .lb-list-item.me {
    background: rgba(124, 90, 240, 0.15);
    border-color: rgba(124, 90, 240, 0.35);
    box-shadow: 0 0 15px rgba(124,90,240,0.1);
  }
  
  .lb-list-rank {
    font-size: 1.1rem; font-weight: 800; color: var(--muted); width: 32px; text-align: left;
  }
  .lb-list-avatar {
    width: 40px; height: 40px; border-radius: 50%;
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.15);
    display: flex; align-items: center; justify-content: center;
    font-weight: 800; font-size: 0.9rem; color: #fff;
    margin-right: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.15);
  }
  .lb-list-name {
    flex: 1; font-size: 0.95rem; font-weight: 700; color: var(--text); text-align: left;
  }
  .lb-list-name.me { color: var(--accent3); }
  .lb-list-score {
    font-size: 1.05rem; font-weight: 800; color: var(--warn);
    font-family: 'JetBrains Mono', monospace; text-shadow: 0 0 10px rgba(240, 185, 34, 0.25);
  }
  .you-badge {
    font-size:.65rem; background:linear-gradient(135deg,var(--accent),#9370ff);
    color:white; padding:3px 10px; border-radius:20px; font-weight:700;
    letter-spacing:.04em; box-shadow:0 2px 10px rgba(124,90,240,.35);
    margin-left: 8px;
  }

  /* ── WAITING ── */
  #waiting-screen.active {
    display:flex !important; flex-direction:column; align-items:center;
    justify-content:center; min-height:62vh; gap:24px; text-align:center;
    animation:fadeUp .5s ease;
  }
  .spinner {
    width:52px; height:52px;
    border:4px solid rgba(120,100,255,.12); border-top-color:var(--accent);
    border-radius:50%; animation:spin .8s cubic-bezier(.4,.15,.6,.85) infinite;
    box-shadow:0 0 24px rgba(124,90,240,.2);
  }
  @keyframes spin { to{transform:rotate(360deg)} }
  #waiting-screen h2 { font-size:1.5rem; font-weight:700; }
  #player-list {
    color:var(--muted); font-size:.88rem;
    background:var(--glass); padding:12px 24px; border-radius:var(--r);
    border:1px solid var(--glass-border);
  }

  /* ── RESPONSIVE ── */
  @media(max-width:720px) {
    #game-screen.active { grid-template-columns:1fr !important; }
    .color-btn { height:68px; font-size:.72rem; }
    #color-display .color-name { font-size:2.6rem; }
    .join-card { padding:36px 24px; }
    header h1 { font-size:1.8rem; }
    #color-display { height:200px; }
  }
  @media(max-width:420px) {
    .color-grid { grid-template-columns:repeat(2,1fr); }
    .color-btn { height:72px; }
  }

  /* ── POWER OVERLAY ── */
  .power-overlay {
    display: none; position: fixed; inset: 0;
    background: rgba(6,6,12,0.92); backdrop-filter: blur(24px);
    z-index: 99; align-items: center; justify-content: center; flex-direction: column;
    padding: 20px; opacity: 0; transition: opacity 0.3s ease;
  }
  .power-overlay.show {
    display: flex; opacity: 1;
  }
  .power-header {
    text-align: center; margin-bottom: 30px; max-width: 500px; width: 100%;
  }
  .power-tag {
    font-size: 0.75rem; background: linear-gradient(135deg, var(--accent), #9370ff);
    color: white; padding: 4px 12px; border-radius: 20px; font-weight: 700;
    letter-spacing: 0.1em; text-shadow: 0 1px 2px rgba(0,0,0,0.3);
    display: inline-block; margin-bottom: 10px;
    box-shadow: 0 0 15px rgba(124,90,240,0.4);
    animation: floatBadge 3s ease-in-out infinite alternate;
  }
  .power-header h2 {
    font-size: 2.2rem; font-weight: 900; letter-spacing: -0.02em;
    background: linear-gradient(135deg, #ffd633, #ff8c00, #ff4d5a);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    filter: drop-shadow(0 0 20px rgba(255,140,0,0.25));
  }
  .power-timer-bar-wrap {
    width: 100%; height: 6px; background: rgba(255,255,255,0.05);
    border-radius: 3px; margin-top: 15px; overflow: hidden;
  }
  #power-timer-bar {
    height: 100%; width: 100%; background: linear-gradient(90deg, #ff4d5a, #b34dff);
    transition: width 0.1s linear;
    box-shadow: 0 0 10px rgba(179,77,255,0.5);
  }
  
  .power-card-container {
    display: flex; gap: 24px; max-width: 900px; width: 100%;
    justify-content: center; align-items: stretch;
  }
  @media(max-width: 780px) {
    .power-card-container { flex-direction: column; }
  }
  
  .power-selection-box {
    flex: 1.3; background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: var(--r-lg); padding: 25px;
    display: flex; flex-direction: column;
  }
  .power-grid-selection {
    display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 10px;
  }
  @media(max-width: 480px) {
    .power-grid-selection { grid-template-columns: 1fr; }
  }
  .power-select-card {
    background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08);
    border-radius: var(--r); padding: 15px 12px; cursor: pointer;
    transition: all 0.25s ease; display: flex; flex-direction: column;
    align-items: center; text-align: center; justify-content: center;
  }
  .power-select-card:hover {
    background: rgba(255,255,255,0.08); border-color: rgba(255,255,255,0.2);
    transform: translateY(-2px);
  }
  .power-select-card.selected {
    background: rgba(124, 90, 240, 0.2) !important; border-color: var(--accent) !important;
    box-shadow: 0 0 15px rgba(124,90,240,0.3);
    transform: scale(1.02);
  }
  .power-icon { font-size: 1.8rem; margin-bottom: 6px; }
  .power-select-card .power-name { font-weight: 800; font-size: 0.85rem; color: #fff; margin-bottom: 4px; }
  .power-select-card .power-desc { font-size: 0.68rem; color: var(--muted); line-height: 1.3; margin-bottom: 4px; }
  
  .power-select-card.used {
    display: none !important;
  }
  
  .power-targets-section {
    flex: 1; background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: var(--r-lg); padding: 25px;
    display: flex; flex-direction: column;
    transition: opacity 0.3s;
  }
  .power-targets-title {
    font-size: 0.8rem; color: var(--accent2); text-transform: uppercase; letter-spacing: 0.08em;
    margin-bottom: 15px; font-weight: 700;
  }
  .power-targets-list {
    display: flex; flex-direction: column; gap: 10px; overflow-y: auto; max-height: 250px;
  }
  .power-target-card {
    display: flex; align-items: center; padding: 12px 16px;
    background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08);
    border-radius: var(--r); transition: all 0.25s ease;
  }
  .power-target-card:hover {
    background: rgba(255,255,255,0.07); border-color: rgba(255,255,255,0.15);
    transform: translateX(4px);
  }
  .power-target-avatar {
    width: 38px; height: 38px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-weight: 800; font-size: 0.85rem; color: white;
    margin-right: 12px;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
  }
  .power-target-name {
    flex: 1; font-weight: 700; font-size: 0.95rem;
  }
  .btn-attack {
    padding: 8px 16px; font-size: 0.8rem; border-radius: 8px; font-weight: 800;
    background: linear-gradient(135deg, var(--danger), #ff8c00);
    color: white; border: none; cursor: pointer; transition: all 0.2s;
    box-shadow: 0 4px 12px rgba(255, 77, 90, 0.3);
  }
  .btn-attack:hover {
    transform: scale(1.05); box-shadow: 0 6px 16px rgba(255, 77, 90, 0.5);
  }
  .btn-attack:active { transform: scale(0.95); }
  .btn-attack.disabled {
    background: rgba(255,255,255,0.05); color: var(--muted);
    cursor: not-allowed; box-shadow: none; transform: none;
  }

  .power-action-area {
    display: flex; flex-direction: column; gap: 12px; height: 100%; justify-content: center;
  }
  .shield-activation-box {
    text-align: center; padding: 20px 10px; display: flex; flex-direction: column; align-items: center; gap: 15px;
  }
  .btn-shield-activate {
    padding: 12px 24px; font-size: 0.95rem; font-weight: 800; border-radius: 12px;
    background: linear-gradient(135deg, var(--success), #15a855); color: white;
    border: none; cursor: pointer; transition: all 0.2s;
    box-shadow: 0 4px 14px rgba(34,211,127,0.4);
    width: 100%;
  }
  .btn-shield-activate:hover {
    transform: translateY(-2px) scale(1.03); box-shadow: 0 6px 20px rgba(34,211,127,0.6);
  }
  .btn-shield-activate.disabled {
    background: rgba(255,255,255,0.05); color: var(--muted); cursor: not-allowed; box-shadow: none; transform: none;
  }
  
  /* ── POWER PENALTY OVERLAYS ── */
  .ice-overlay {
    position: absolute; inset: -4px; z-index: 10;
    background: rgba(200, 240, 255, 0.25);
    backdrop-filter: blur(4px); -webkit-backdrop-filter: blur(4px);
    border: 4px solid #4adede; border-radius: var(--r-lg);
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    pointer-events: all;
    box-shadow: 0 0 30px rgba(74, 222, 222, 0.3) inset, 0 0 25px rgba(74, 222, 222, 0.2);
    animation: icePulse 1s ease-in-out infinite alternate;
    transition: opacity 0.4s ease;
  }
  @keyframes icePulse {
    0% { border-color: rgba(74, 222, 222, 0.8); }
    100% { border-color: rgba(255, 255, 255, 1); }
  }
  .ice-text {
    font-size: 1.4rem; font-weight: 900; color: #fff;
    text-shadow: 0 0 15px #4adede, 0 2px 4px rgba(0,0,0,0.6);
    text-align: center;
  }
  .ice-sub {
    font-size: 0.8rem; color: #c0f2f2; margin-top: 5px; font-weight: 700;
    text-shadow: 0 1px 2px rgba(0,0,0,0.5);
  }
  .ice-overlay.shatter {
    animation: iceShatter 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
    opacity: 0; pointer-events: none;
  }
  @keyframes iceShatter {
    0% { transform: scale(1); opacity: 1; }
    100% { transform: scale(1.15); opacity: 0; filter: blur(8px); }
  }
  
  .ink-overlay {
    position: absolute; inset: 0; z-index: 10;
    background: transparent; pointer-events: auto;
    display: flex; align-items: center; justify-content: center;
  }
  .ink-splat {
    width: 140px; height: 140px;
    background: radial-gradient(circle, #000 0%, #15092a 60%, transparent 85%);
    border-radius: 50%;
    box-shadow: 0 0 15px rgba(0,0,0,0.8);
    filter: drop-shadow(5px 5px 8px rgba(0,0,0,0.7));
    cursor: pointer; position: relative;
    transition: transform 0.15s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    display: flex; align-items: center; justify-content: center;
    animation: inkFloat 3s ease-in-out infinite alternate;
    user-select: none;
  }
  @keyframes inkFloat {
    0% { transform: translateY(0) scale(1); }
    100% { transform: translateY(-8px) scale(1.05); }
  }
  .ink-splat::after {
    content: '👾 TINTA!';
    color: #e0b3ff; font-weight: 900; font-size: 0.9rem;
    text-shadow: 0 2px 4px #000, 0 0 10px #b34dff;
    text-align: center;
  }
  .ink-hint {
    position: absolute; bottom: 12px;
    font-size: 0.75rem; color: #c4b5fd; font-weight: 700;
    text-shadow: 0 1px 3px rgba(0,0,0,0.8);
    text-align: center; width: 100%; pointer-events: none;
  }
  .ink-splat.hit {
    animation: inkHit 0.25s ease;
  }
  @keyframes inkHit {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(0.85) rotate(-10deg); filter: brightness(1.3); }
  }
  
  .shuffled-cue {
    border: 3px dashed #ffd633 !important;
    animation: borderRotate 4s linear infinite, shuffleGlow 1.5s ease-in-out infinite alternate;
  }
  @keyframes borderRotate {
    100% { filter: hue-rotate(360deg); }
  }
  @keyframes shuffleGlow {
    0% { box-shadow: 0 0 10px rgba(255, 214, 51, 0.2); }
    100% { box-shadow: 0 0 25px rgba(255, 214, 51, 0.5); }
  }
</style>
</head>
<body>

<canvas id="particles"></canvas>

<header>
  <h1>🌈 COLOR PANIC</h1>
  <p>Multiplayer Color Reaction Game · Komunikasi Data 2026</p>
</header>

<div id="countdown-overlay">
  <div id="countdown-num">3</div>
  <p>Bersiap...</p>
</div>

<div id="round-overlay" class="round-overlay">
  <div class="round-title-glow" id="round-overlay-text">RONDE 1</div>
  <p>Bersiap... Cepat & Tepat! ⚡</p>
</div>

<div id="power-overlay" class="power-overlay">
  <div class="power-header">
    <span class="power-tag">FASE KEKUATAN</span>
    <h2>Pilih Aksi & Kekuatan Anda! ⚡</h2>
    <div class="power-timer-bar-wrap"><div id="power-timer-bar"></div></div>
  </div>
  <div class="power-card-container">
    <!-- Kiri: Pilihan Kekuatan -->
    <div class="power-selection-box">
      <div class="power-targets-title">Pilih Kekuatan/Aksi:</div>
      <div class="power-grid-selection">
        <div class="power-select-card" id="card-BOM-ES" onclick="selectPowerChoice('BOM ES')">
          <div class="power-icon">❄️</div>
          <div class="power-name">BOM ES</div>
          <div class="power-desc">Bekukan tombol lawan (1.5s)</div>
        </div>
        <div class="power-select-card" id="card-TINTA-GURITA" onclick="selectPowerChoice('TINTA GURITA')">
          <div class="power-icon">👾</div>
          <div class="power-name">TINTA GURITA</div>
          <div class="power-desc">Tutupi sequence lawan dengan tinta</div>
        </div>
        <div class="power-select-card" id="card-BADAI-ACAK" onclick="selectPowerChoice('BADAI ACAK')">
          <div class="power-icon">🌀</div>
          <div class="power-name">BADAI ACAK</div>
          <div class="power-desc">Acak posisi tombol lawan</div>
        </div>
        <div class="power-select-card" id="card-PERISAI" onclick="selectPowerChoice('PERISAI')">
          <div class="power-icon">🛡️</div>
          <div class="power-name">PERISAI</div>
          <div class="power-desc">Blokir seluruh serangan lawan ronde ini</div>
        </div>
      </div>
    </div>
    
    <!-- Kanan: Target Serangan / Konfirmasi Perisai -->
    <div class="power-targets-section" id="power-targets-section" style="opacity: 0.5; pointer-events: none;">
      <div class="power-targets-title" id="action-target-title">Pilih Target / Aktifkan:</div>
      <div id="power-action-area" class="power-action-area">
        <!-- Rendered dynamically -->
      </div>
    </div>
  </div>
</div>

<div class="app">
  <div id="status-bar">
    <div class="dot" id="conn-dot"></div>
    <span id="conn-status">Belum terhubung</span>
  </div>

  <!-- JOIN -->
  <div id="join-screen" class="screen active">
    <div class="join-blob join-blob-1"></div>
    <div class="join-blob join-blob-2"></div>
    <div class="join-card">
      <div class="login-badge-wrap">
        <div class="login-badge">🎮</div>
      </div>
      <h2>Masuk ke Game</h2>
      <p>Hubungkan ke server dan masukkan nama untuk mulai bermain</p>
      <div class="input-group">
        <label><span class="label-dot"></span> Alamat Server</label>
        <input type="text" id="server-host" value="localhost:8765" placeholder="localhost:8765">
      </div>
      <div class="input-group">
        <label><span class="label-dot"></span> Nama Pemain</label>
        <input type="text" id="player-name" placeholder="Nama kamu..." maxlength="12"
               onkeydown="if(event.key==='Enter') joinGame()">
      </div>
      <button class="btn btn-primary" id="join-btn" onclick="joinGame()">🚀 Gabung Sekarang</button>
    </div>
  </div>

  <!-- WAITING -->
  <div id="waiting-screen" class="screen">
    <div class="spinner"></div>
    <h2>Menunggu Pemain Lain...</h2>
    <p style="color:var(--muted)">Minimal 2 pemain untuk memulai game</p>
    <div id="player-list"></div>
  </div>

  <!-- GAME -->
  <div id="game-screen" class="screen">
    <div class="main-panel">
      <div class="round-info">
        <span class="round-badge" id="round-label">RONDE 0 / 5</span>
        <div id="timer-bar-wrap"><div id="timer-bar"></div></div>
        <span class="score-display" id="score-wrap">⭐ <span id="my-score">0</span> poin</span>
      </div>

      <!-- Sequence dots -->
      <div class="sequence-bar" id="sequence-bar"></div>

      <div id="color-display">
        <span class="waiting-text">⏳ Menunggu ronde berikutnya...</span>
      </div>

      <div id="feedback">Tekan warna yang muncul secepat mungkin! 🎯</div>

      <div class="color-grid" id="color-buttons"></div>
    </div>

    <div class="sidebar">
      <div class="sidebar-card">
        <h3>📊 Papan Skor</h3>
        <div id="scoreboard"></div>
      </div>
      <div class="sidebar-card">
        <h3>📋 Log Permainan</h3>
        <div id="game-log"></div>
        <div class="chat-input-row">
          <input type="text" id="chat-input" placeholder="Kirim pesan..." maxlength="80"
                 onkeydown="if(event.key==='Enter') sendChat()">
          <button class="chat-send" onclick="sendChat()">→</button>
        </div>
      </div>
    </div>
  </div>

  <!-- GAME OVER -->
  <div id="gameover-screen" class="screen">
    <div class="final-card">
      <h2>🏆 Game Selesai!</h2>
      <div id="final-leaderboard"></div>
    </div>
    <button class="btn btn-primary" style="max-width:320px" onclick="resetToJoin()">🔄 Main Lagi</button>
  </div>
</div>

<script>
// ── PARTICLES ──
(function(){
  const c=document.getElementById('particles'), ctx=c.getContext('2d');
  let P=[];
  const N=80, CS=['rgba(255,77,90,','rgba(77,138,255,','rgba(34,211,127,','rgba(255,214,51,','rgba(179,77,255,','rgba(255,102,204,'];
  function resize(){c.width=innerWidth;c.height=innerHeight}
  resize(); addEventListener('resize',resize);
  for(let i=0;i<N;i++) P.push({
    x:Math.random()*c.width, y:Math.random()*c.height,
    vx:(Math.random()-.5)*.45, vy:(Math.random()-.5)*.45,
    s:Math.random()*3+1, col:CS[Math.floor(Math.random()*CS.length)],
    a:Math.random()*.35+.08
  });
  (function draw(){
    ctx.clearRect(0,0,c.width,c.height);
    P.forEach(p=>{
      p.x+=p.vx; p.y+=p.vy;
      if(p.x<0)p.x=c.width; if(p.x>c.width)p.x=0;
      if(p.y<0)p.y=c.height; if(p.y>c.height)p.y=0;
      ctx.beginPath(); ctx.arc(p.x,p.y,p.s,0,Math.PI*2);
      ctx.fillStyle=p.col+p.a+')'; ctx.fill();
    });
    requestAnimationFrame(draw);
  })();
})();

// ── GAME ──
const COLORS=[
  {name:"MERAH",emoji:"🔴",key:"1"},{name:"BIRU",emoji:"🔵",key:"2"},
  {name:"HIJAU",emoji:"🟢",key:"3"},{name:"KUNING",emoji:"🟡",key:"4"},
  {name:"ORANGE",emoji:"🟠",key:"5"},{name:"UNGU",emoji:"🟣",key:"6"},
  {name:"PINK",emoji:"🩷",key:"7"},{name:"PUTIH",emoji:"⚪",key:"8"},
];
const COLOR_MAP={};
COLORS.forEach(c=>{COLOR_MAP[c.key]=c.name});

const BG_MAP={
  MERAH:"linear-gradient(145deg,#ff5a5a,#d02828)",
  BIRU:"linear-gradient(145deg,#5a90ff,#2850d0)",
  HIJAU:"linear-gradient(145deg,#30e88a,#15a855)",
  KUNING:"linear-gradient(145deg,#ffe040,#d8b010)",
  ORANGE:"linear-gradient(145deg,#ff9a20,#d06800)",
  UNGU:"linear-gradient(145deg,#c060ff,#8020d0)",
  PINK:"linear-gradient(145deg,#ff78d0,#d04898)",
  PUTIH:"linear-gradient(145deg,#f0f0ff,#c8c8e8)"
};
const TEXT_MAP={MERAH:"#fff",BIRU:"#fff",HIJAU:"#0d2a1a",KUNING:"#2a2000",ORANGE:"#fff",UNGU:"#fff",PINK:"#fff",PUTIH:"#1a1a2e"};
const GLOW_MAP={MERAH:"rgba(255,77,90,.4)",BIRU:"rgba(77,138,255,.4)",HIJAU:"rgba(34,211,127,.4)",KUNING:"rgba(255,214,51,.4)",ORANGE:"rgba(255,140,0,.4)",UNGU:"rgba(179,77,255,.4)",PINK:"rgba(255,102,204,.4)",PUTIH:"rgba(200,200,255,.3)"};

let ws=null, myName="", myScore=0, canAnswer=false;
let timerInterval=null, timerStart=0;
let activeColors=[];
let localIndex=0;
let isBadaiAcak = false;
let isInkBlocked = false;
let inkClicksLeft = 3;
let powerPhaseInterval = null;

function buildColorButtons(){
  const grid=document.getElementById("color-buttons");
  grid.innerHTML="";
  
  // Clean up any old overlays (e.g. ice)
  const existingIce = grid.querySelector(".ice-overlay");
  if (existingIce) existingIce.remove();
  
  let btnsToRender = [...COLORS];
  if (isBadaiAcak) {
    // Fisher-Yates shuffle
    for (let i = btnsToRender.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [btnsToRender[i], btnsToRender[j]] = [btnsToRender[j], btnsToRender[i]];
    }
  }

  btnsToRender.forEach((c,i)=>{
    const btn=document.createElement("button");
    btn.className=`color-btn btn-${c.name}`;
    if (isBadaiAcak) {
      btn.classList.add("shuffled-cue");
    }
    btn.id=`btn-${c.name}`;
    btn.innerHTML=`<span class="key-hint">${c.key}</span>${c.name}`;
    btn.onclick=()=>sendAnswer(c.name,btn);
    grid.appendChild(btn);
  });
}

function buildSequenceDots(count){
  const bar=document.getElementById("sequence-bar");
  bar.innerHTML="";
  for(let i=0;i<count;i++){
    if(i>0) bar.innerHTML+=`<div class="seq-connector" id="seq-conn-${i}"></div>`;
    bar.innerHTML+=`<div class="seq-dot" id="seq-dot-${i}"></div>`;
  }
}

function updateSequenceDots(current, total){
  for(let i=0;i<total;i++){
    const dot=document.getElementById(`seq-dot-${i}`);
    const conn=document.getElementById(`seq-conn-${i}`);
    if(!dot) continue;
    dot.className='seq-dot';
    if(i<current-1){ dot.classList.add('done'); }
    else if(i===current-1){ dot.classList.add('active'); }
    if(conn){ conn.className='seq-connector'; if(i<current) conn.classList.add('done'); }
  }
}

function joinGame(){
  const host=document.getElementById("server-host").value.trim()||"localhost:8765";
  myName=document.getElementById("player-name").value.trim();
  if(!myName){alert("Masukkan nama dulu!");return}
  document.getElementById("join-btn").disabled=true;
  document.getElementById("join-btn").textContent="Menghubungkan...";
  ws=new WebSocket(`ws://${host}`);
  ws.onopen=()=>{ setConnected(true); send({type:"join",name:myName}); showScreen("waiting"); log("Terhubung ke server!","info"); };
  ws.onmessage=e=>{ try{handleMsg(JSON.parse(e.data))}catch(err){} };
  ws.onclose=()=>{ setConnected(false); log("Koneksi terputus.","danger"); };
  ws.onerror=()=>{
    setConnected(false); log("Gagal terhubung.","danger");
    document.getElementById("join-btn").disabled=false;
    document.getElementById("join-btn").textContent="🚀 Gabung Sekarang";
    showScreen("join");
  };
}

function handleMsg(msg){
  switch(msg.type){
    case "joined":
      updatePlayerList(msg.players);
      log(`Bergabung sebagai ${msg.name}`,"info");
      break;
    case "player_joined":
      log(`${msg.name} bergabung (${msg.count} pemain)`,"info");
      break;
    case "player_left":
      log(`${msg.name} keluar`,"danger");
      break;
    case "info":
      log(msg.message,"warn");
      break;
    case "countdown":
      showCountdown(msg.value);
      break;
    case "game_start":
      showScreen("game");
      buildColorButtons();
      log(`Game dimulai! ${msg.total_rounds} ronde`,"warn");
      break;
    case "round_start":
      isBadaiAcak = false;
      isInkBlocked = false;
      resetButtonStates();
      document.getElementById("round-label").textContent=`RONDE ${msg.round} / ${msg.total}`;
      setFeedback("🎯 Bersiap untuk sequence warna!","");
      showRoundOverlay(msg.round);
      break;
    case "color_signal":
      activeColors = msg.colors || [];
      localIndex = 0;
      canAnswer = true;
      isBadaiAcak = msg.active_powers && msg.active_powers.includes("BADAI ACAK");
      buildColorButtons();
      renderTargetColors(activeColors, msg.round, msg.total);
      startTimer(5);
      resetButtonStates();
      applyActivePowers(msg.active_powers || []);
      break;
    case "answer_result":
      if(msg.correct){
        myScore=msg.total_score;
        animateScore();
        if(msg.completed){
          setFeedback(`🏆 SEQUENCE SELESAI! (+${msg.points} poin)`,"correct");
          log(`Menyelesaikan sequence! +${msg.points} poin`,"success");
        } else {
          log(`Benar! +1 poin`,"success");
        }
      } else {
        setFeedback("❌ SALAH! Coba lagi!","wrong");
        log("Salah!","danger");
      }
      break;
    case "round_result":
      updateScoreboard(msg.scoreboard);
      stopTimer();
      break;
    case "game_over":
      showGameOver(msg.leaderboard);
      break;
    case "chat":
      log(`💬 ${msg.from}: ${msg.message}`,"");
      break;
    case "power_phase_start":
      showPowerPhase(msg.available_powers || [], msg.opponents, msg.duration);
      break;
    case "power_used_broadcast":
      log(`💥 [KEKUATAN] ${msg.by} menyerang ${msg.target} dengan ${msg.power}!`, "warn");
      break;
    case "power_phase_end":
      hidePowerPhase();
      break;
  }
}

function renderTargetColors(colors, round, total) {
  const d = document.getElementById("color-display");
  d.style.background = "var(--surface)";
  d.style.color = "var(--text)";
  d.style.borderColor = "var(--border)";
  d.style.boxShadow = "0 8px 40px rgba(0,0,0,.25)";
  
  let listHtml = "";
  colors.forEach((col, idx) => {
    const bg = BG_MAP[col] || "#333";
    const tc = TEXT_MAP[col] || "#fff";
    const glow = GLOW_MAP[col] || "rgba(255,255,255,0.2)";
    const activeClass = idx === 0 ? "active" : "";
    
    if (idx > 0) {
      listHtml += `<div class="target-arrow" id="arrow-${idx}">➔</div>`;
    }
    
    listHtml += `
      <div class="target-item ${activeClass}" id="target-${idx}" style="background: ${bg}; color: ${tc}; --current-color: ${glow};">
        <span>${col}</span>
      </div>
    `;
  });
  
  d.innerHTML = `
    <div class="target-list">${listHtml}</div>
    <div class="target-footer">Ronde ${round}/${total} · Total: ${colors.length} warna</div>
  `;
  
  d.classList.remove("pulse"); void d.offsetWidth; d.classList.add("pulse");
  setFeedback("🎯 Tekan warna-warna di atas sesuai urutan secepat mungkin!","");
}

function sendAnswer(color, btn) {
  if (!canAnswer || activeColors.length === 0) return;
  
  const expected = activeColors[localIndex];
  if (color === expected) {
    // Kirim ke server
    send({type: "answer", color: color});
    
    // Animasi tombol benar
    if (btn) {
      btn.classList.add('correct');
      setTimeout(() => btn.classList.remove('correct'), 300);
    }
    
    // Update UI target lama
    const oldTarget = document.getElementById(`target-${localIndex}`);
    if (oldTarget) {
      oldTarget.classList.remove('active');
      oldTarget.classList.add('cleared');
    }
    
    // Update arrow lama ke cleared
    const oldArrow = document.getElementById(`arrow-${localIndex + 1}`);
    if (oldArrow) {
      oldArrow.classList.add('cleared');
    }
    
    localIndex++;
    
    // Cek apakah sudah menyelesaikan seluruh sequence
    if (localIndex >= activeColors.length) {
      canAnswer = false;
      setFeedback("🏆 SEQUENCE SELESAI! Menunggu pemain lain...", "correct");
      log("Berhasil menyelesaikan semua warna!", "success");
    } else {
      // Aktifkan target berikutnya
      const nextTarget = document.getElementById(`target-${localIndex}`);
      if (nextTarget) {
        nextTarget.classList.add('active');
      }
      setFeedback(`🎯 Warna berikutnya: ${activeColors[localIndex]}`, "");
    }
  } else {
    // Animasi salah pada tombol
    if (btn) {
      btn.classList.add('wrong');
      setTimeout(() => btn.classList.remove('wrong'), 500);
    }
    setFeedback(`❌ SALAH! Ketuk: ${expected}`, "wrong");
    
    // Animasi salah pada target card saat ini
    const currentTarget = document.getElementById(`target-${localIndex}`);
    if (currentTarget) {
      currentTarget.classList.add('wrong');
      setTimeout(() => currentTarget.classList.remove('wrong'), 500);
    }
  }
}

function resetButtonStates(){
  document.querySelectorAll('.color-btn').forEach(b=>{
    b.classList.remove('answered','correct','wrong');
  });
}

function animateScore(){
  const el=document.getElementById("my-score");
  el.textContent=myScore;
  const wrap=document.getElementById("score-wrap");
  wrap.classList.remove("pop"); void wrap.offsetWidth; wrap.classList.add("pop");
}

function setFeedback(text,cls){
  const el=document.getElementById("feedback");
  el.className=cls; el.textContent=text;
}

function updateScoreboard(scores){
  const el=document.getElementById("scoreboard");
  const sorted=Object.entries(scores).sort((a,b)=>b[1].score - a[1].score);
  const avatarGradients = [
    "linear-gradient(135deg, #ff4d5a, #ff78d0)",
    "linear-gradient(135deg, #4d8aff, #4adede)",
    "linear-gradient(135deg, #b34dff, #ff66cc)",
    "linear-gradient(135deg, #22d37f, #ffd633)",
    "linear-gradient(135deg, #ff8c00, #ff4d5a)"
  ];
  el.innerHTML=sorted.map(([name,data],i)=>{
    const score = data.score;
    const usedPowers = data.used_powers || [];
    const rankClass = i === 0 ? 'rank-1' : (i === 1 ? 'rank-2' : (i === 2 ? 'rank-3' : ''));
    const rankText = i < 3 ? (i + 1) : `#${i+1}`;
    const initials = name.substring(0, 2).toUpperCase();
    const avatarBg = avatarGradients[i % avatarGradients.length];
    
    const isBomEsUsed = usedPowers.includes('BOM ES');
    const isTintaUsed = usedPowers.includes('TINTA GURITA');
    const isBadaiUsed = usedPowers.includes('BADAI ACAK');
    const isPerisaiUsed = usedPowers.includes('PERISAI');

    return `
      <div class="lb-entry ${name===myName?'me':''}">
        <span class="lb-rank ${rankClass}">${rankText}</span>
        <div class="lb-avatar" style="background: ${avatarBg}; border-color: rgba(255,255,255,0.25);">
          <span class="avatar-text">${initials}</span>
        </div>
        <div class="lb-info-col">
          <span class="lb-name ${name===myName?'me':''}">${name}${name===myName?' (kamu)':''}</span>
          <div class="player-used-powers">
            <span class="used-badge ${isBomEsUsed?'active':''}" title="BOM ES ${isBomEsUsed?'(Terpakai)':'(Belum dipakai)'}">❄️</span>
            <span class="used-badge ${isTintaUsed?'active':''}" title="TINTA GURITA ${isTintaUsed?'(Terpakai)':'(Belum dipakai)'}">👾</span>
            <span class="used-badge ${isBadaiUsed?'active':''}" title="BADAI ACAK ${isBadaiUsed?'(Terpakai)':'(Belum dipakai)'}">🌀</span>
            <span class="used-badge ${isPerisaiUsed?'active':''}" title="PERISAI ${isPerisaiUsed?'(Terpakai)':'(Belum dipakai)'}">🛡️</span>
          </div>
        </div>
        <span class="lb-score">${score}</span>
      </div>
    `;
  }).join("");
}

function showGameOver(lb){
  stopTimer();
  
  const avatarGradients = [
    "linear-gradient(135deg, #ff4d5a, #ff78d0)",
    "linear-gradient(135deg, #4d8aff, #4adede)",
    "linear-gradient(135deg, #b34dff, #ff66cc)",
    "linear-gradient(135deg, #22d37f, #ffd633)",
    "linear-gradient(135deg, #ff8c00, #ff4d5a)"
  ];
  
  // Render Podium
  const top1 = lb[0] ? lb[0] : null;
  const top2 = lb[1] ? lb[1] : null;
  const top3 = lb[2] ? lb[2] : null;
  
  let podiumHtml = "";
  if (top1 || top2 || top3) {
    podiumHtml += `<div class="podium-container">`;
    
    // Rank 2 (Left)
    if (top2) {
      const initials = top2.name.substring(0, 2).toUpperCase();
      const isMe = top2.name === myName ? "me" : "";
      const avatarBg = avatarGradients[1 % avatarGradients.length];
      podiumHtml += `
        <div class="podium-step step-2">
          <div class="podium-avatar" style="background: ${avatarBg};">
            <span class="avatar-text">${initials}</span>
            <div class="podium-rank-badge">2</div>
          </div>
          <div class="podium-name ${isMe}">${top2.name}</div>
          <div class="podium-score">${top2.score} pts</div>
        </div>
      `;
    }
    
    // Rank 1 (Center)
    if (top1) {
      const initials = top1.name.substring(0, 2).toUpperCase();
      const isMe = top1.name === myName ? "me" : "";
      const avatarBg = avatarGradients[0 % avatarGradients.length];
      podiumHtml += `
        <div class="podium-step step-1">
          <div class="crown-icon">👑</div>
          <div class="podium-avatar" style="background: ${avatarBg};">
            <span class="avatar-text">${initials}</span>
            <div class="podium-rank-badge">1</div>
          </div>
          <div class="podium-name ${isMe}">${top1.name}</div>
          <div class="podium-score">${top1.score} pts</div>
        </div>
      `;
    }
    
    // Rank 3 (Right)
    if (top3) {
      const initials = top3.name.substring(0, 2).toUpperCase();
      const isMe = top3.name === myName ? "me" : "";
      const avatarBg = avatarGradients[2 % avatarGradients.length];
      podiumHtml += `
        <div class="podium-step step-3">
          <div class="podium-avatar" style="background: ${avatarBg};">
            <span class="avatar-text">${initials}</span>
            <div class="podium-rank-badge">3</div>
          </div>
          <div class="podium-name ${isMe}">${top3.name}</div>
          <div class="podium-score">${top3.score} pts</div>
        </div>
      `;
    }
    
    podiumHtml += `</div>`;
  }
  
  // Render List
  let listHtml = `<div class="lb-list-container">`;
  lb.forEach((e, i) => {
    const initials = e.name.substring(0, 2).toUpperCase();
    const isMe = e.name === myName;
    const meClass = isMe ? "me" : "";
    const nameClass = isMe ? "me" : "";
    const badgeHtml = isMe ? `<span class="you-badge">KAMU</span>` : "";
    const avatarBg = avatarGradients[i % avatarGradients.length];
    
    listHtml += `
      <div class="lb-list-item ${meClass}">
        <div class="lb-list-rank">${i + 1}</div>
        <div class="lb-list-avatar" style="background: ${avatarBg}; border-color: rgba(255,255,255,0.25);">
          <span class="avatar-text">${initials}</span>
        </div>
        <div class="lb-list-name ${nameClass}">${e.name}${badgeHtml}</div>
        <div class="lb-list-score">${e.score} pts</div>
      </div>
    `;
  });
  listHtml += `</div>`;
  
  document.getElementById("final-leaderboard").innerHTML = podiumHtml + listHtml;
  showScreen("gameover");
  log("🏆 Game selesai!","warn");
}

function showCountdown(val){
  const o=document.getElementById("countdown-overlay"), n=document.getElementById("countdown-num");
  o.classList.add("show"); n.textContent=val;
  n.style.animation='none'; void n.offsetWidth; n.style.animation='';
  setTimeout(()=>{if(val<=1) o.classList.remove("show")},900);
}

function showRoundOverlay(roundNum) {
  const o = document.getElementById("round-overlay");
  const t = document.getElementById("round-overlay-text");
  t.textContent = `RONDE ${roundNum}`;
  o.classList.add("show");
  setTimeout(() => {
    o.classList.remove("show");
  }, 1200);
}

function updatePlayerList(players){
  document.getElementById("player-list").innerHTML="👥 Pemain: "+players.join(", ");
}

function startTimer(seconds){
  stopTimer(); timerStart=Date.now();
  const bar=document.getElementById("timer-bar"); bar.style.width="100%";
  timerInterval=setInterval(()=>{
    const elapsed=(Date.now()-timerStart)/1000;
    const pct=Math.max(0,100-(elapsed/seconds*100));
    bar.style.width=pct+"%";
    // Change glow color based on time
    if(pct<30) bar.style.boxShadow='0 0 12px rgba(255,90,110,.4)';
    else if(pct<60) bar.style.boxShadow='0 0 10px rgba(240,185,34,.3)';
    else bar.style.boxShadow='0 0 10px rgba(34,211,127,.3)';
    if(elapsed>=seconds){stopTimer(); if(canAnswer){canAnswer=false; setFeedback("⏰ Waktu habis!","timeout");}}
  },50);
}

function stopTimer(){ if(timerInterval){clearInterval(timerInterval);timerInterval=null} }

function sendChat(){
  const inp=document.getElementById("chat-input");
  if(!inp.value.trim()) return;
  send({type:"chat",message:inp.value.trim()}); inp.value="";
}

function log(text,cls=""){
  const el=document.getElementById("game-log");
  const e=document.createElement("div");
  e.className=`log-entry ${cls}`;
  e.textContent=`[${new Date().toLocaleTimeString()}] ${text}`;
  el.appendChild(e); el.scrollTop=el.scrollHeight;
}

function showScreen(name){
  ["join","waiting","game","gameover"].forEach(s=>{
    document.getElementById(`${s}-screen`).classList.toggle("active",s===name);
  });
}

function setConnected(ok){
  document.getElementById("conn-dot").className="dot"+(ok?" connected":"");
  document.getElementById("conn-status").textContent=ok?`Terhubung — ${myName}`:"Terputus";
}

function resetToJoin(){
  if(ws){ws.close();ws=null}
  myScore=0; canAnswer=false;
  isBadaiAcak = false;
  isInkBlocked = false;
  hidePowerPhase();
  document.getElementById("my-score").textContent="0";
  document.getElementById("join-btn").disabled=false;
  document.getElementById("join-btn").textContent="🚀 Gabung Sekarang";
  setConnected(false); showScreen("join");
}

function send(data){ if(ws&&ws.readyState===WebSocket.OPEN) ws.send(JSON.stringify(data)); }

// Keyboard shortcuts
document.addEventListener("keydown",e=>{
  if(!canAnswer) return;
  if(COLOR_MAP[e.key]){
    const name=COLOR_MAP[e.key];
    const btn=document.getElementById(`btn-${name}`);
    sendAnswer(name,btn);
  }
});

// ── POWER UP HELPERS ──
let selectedPowerChoice = null;
let availableOpponents = [];

function showPowerPhase(availablePowers, opponents, durationSeconds) {
  // Clear any existing intervals
  if (powerPhaseInterval) clearInterval(powerPhaseInterval);
  
  selectedPowerChoice = null;
  availableOpponents = opponents || [];
  
  // Set used state on select cards based on availablePowers
  const allPowerKeys = ["BOM ES", "TINTA GURITA", "BADAI ACAK", "PERISAI"];
  allPowerKeys.forEach(pow => {
    const cardId = "card-" + pow.replace(" ", "-");
    const card = document.getElementById(cardId);
    if (card) {
      if (availablePowers.includes(pow)) {
        card.classList.remove("used");
      } else {
        card.classList.add("used");
      }
    }
  });
  
  // Reset selection styles
  document.querySelectorAll(".power-select-card").forEach(c => {
    c.classList.remove("selected");
    c.style.pointerEvents = c.classList.contains("used") ? "none" : "auto";
  });
  
  // Lock target area initially
  const targetSec = document.getElementById("power-targets-section");
  targetSec.style.opacity = "0.5";
  targetSec.style.pointerEvents = "none";
  document.getElementById("power-action-area").innerHTML = `
    <div style="color:var(--muted); text-align:center; padding: 20px; font-size: 0.9rem;">Pilih salah satu kekuatan di sebelah kiri terlebih dahulu.</div>
  `;
  
  // Show overlay
  const overlay = document.getElementById("power-overlay");
  overlay.classList.add("show");
  
  // Animate timer bar
  const bar = document.getElementById("power-timer-bar");
  bar.style.width = "100%";
  
  const startTime = Date.now();
  const durationMs = durationSeconds * 1000;
  
  powerPhaseInterval = setInterval(() => {
    const elapsed = Date.now() - startTime;
    const pct = Math.max(0, 100 - (elapsed / durationMs * 100));
    bar.style.width = pct + "%";
    if (elapsed >= durationMs) {
      clearInterval(powerPhaseInterval);
      powerPhaseInterval = null;
    }
  }, 50);
}

function selectPowerChoice(powerName) {
  selectedPowerChoice = powerName;
  
  // Highlight card
  document.querySelectorAll(".power-select-card").forEach(c => {
    c.classList.toggle("selected", c.id === "card-" + powerName.replace(" ", "-"));
  });
  
  // Enable target area
  const targetSec = document.getElementById("power-targets-section");
  targetSec.style.opacity = "1";
  targetSec.style.pointerEvents = "auto";
  
  const actionArea = document.getElementById("power-action-area");
  const actionTitle = document.getElementById("action-target-title");
  
  if (powerName === "PERISAI") {
    actionTitle.textContent = "Aktifkan Perisai Pelindung:";
    actionArea.innerHTML = `
      <div class="shield-activation-box">
        <div class="power-icon" style="font-size: 3.2rem;">🛡️</div>
        <p style="font-size: 0.82rem; color: var(--muted); line-height: 1.4; max-width:280px; margin:0 auto;">Perisai ini akan melindungimu dari seluruh serangan (Es, Tinta, Acak) lawan ronde berikutnya!</p>
        <button class="btn-shield-activate" id="btn-shield-trigger" onclick="activateShield(this)">🛡️ AKTIFKAN PERISAI</button>
      </div>
    `;
  } else {
    actionTitle.textContent = "Pilih Target Lawan:";
    let listHtml = `<div class="power-targets-list">`;
    if (availableOpponents.length === 0) {
      listHtml += `<div style="color:var(--muted); text-align:center; padding: 20px; font-size: 0.9rem;">Tidak ada lawan untuk diserang.</div>`;
    } else {
      const avatarGradients = [
        "linear-gradient(135deg, #ff4d5a, #ff78d0)",
        "linear-gradient(135deg, #4d8aff, #4adede)",
        "linear-gradient(135deg, #b34dff, #ff66cc)",
        "linear-gradient(135deg, #22d37f, #ffd633)"
      ];
      availableOpponents.forEach((opp, i) => {
        const initials = opp.substring(0, 2).toUpperCase();
        const avatarBg = avatarGradients[i % avatarGradients.length];
        
        listHtml += `
          <div class="power-target-card">
            <div class="power-target-avatar" style="background: ${avatarBg};">
              <span>${initials}</span>
            </div>
            <span class="power-target-name">${opp}</span>
            <button class="btn-attack" onclick="usePowerAttack('${opp.replace(/'/g, "\\'")}', this)">SERANG</button>
          </div>
        `;
      });
    }
    listHtml += `</div>`;
    actionArea.innerHTML = listHtml;
  }
}

function activateShield(btn) {
  // Send shield command to server
  send({type: "use_power", power: "PERISAI", target: "self"});
  
  // Disable selection
  lockPowerSelections();
  
  if (btn) {
    btn.disabled = true;
    btn.classList.add("disabled");
    btn.textContent = "🛡️ PERISAI AKTIF!";
    btn.style.background = "linear-gradient(135deg, var(--success), #15a855)";
    btn.style.boxShadow = "0 0 15px rgba(34,211,127,0.5)";
  }
  log("Mengaktifkan Perisai Pelindung! 🛡️", "info");
}

function usePowerAttack(targetPlayer, btn) {
  // Send power attack command to server
  send({type: "use_power", power: selectedPowerChoice, target: targetPlayer});
  
  // Disable selection
  lockPowerSelections();
  
  // Disable attack buttons
  document.querySelectorAll('.btn-attack').forEach(b => {
    b.disabled = true;
    b.classList.add('disabled');
    b.textContent = 'TERKIRIM';
  });
  
  if (btn) {
    btn.textContent = 'TERSERANG! 💥';
    btn.style.background = 'linear-gradient(135deg, var(--success), #15a855)';
    btn.style.boxShadow = '0 0 15px rgba(34,211,127,0.5)';
  }
  log(`Mengirim serangan ${selectedPowerChoice} ke ${targetPlayer}!`, "info");
}

function lockPowerSelections() {
  document.querySelectorAll(".power-select-card").forEach(c => {
    c.style.pointerEvents = "none";
  });
  const targetSec = document.getElementById("power-targets-section");
  targetSec.style.pointerEvents = "none";
}

function hidePowerPhase() {
  const overlay = document.getElementById("power-overlay");
  if (overlay) overlay.classList.remove("show");
  if (powerPhaseInterval) {
    clearInterval(powerPhaseInterval);
    powerPhaseInterval = null;
  }
}

function applyActivePowers(powers) {
  // Clean up any existing penalty overlays first
  const existingIce = document.querySelector(".ice-overlay");
  if (existingIce) existingIce.remove();
  const existingInk = document.querySelector(".ink-overlay");
  if (existingInk) existingInk.remove();
  
  isIceBlocked = false;
  isInkBlocked = false;
  
  // 1. Bom Es Effect
  if (powers.includes("BOM ES")) {
    isIceBlocked = true;
    canAnswer = false; // block inputs
    log("⚠️ Kamu terkena BOM ES! Tombol beku selama 1.5 detik!", "danger");
    
    const grid = document.getElementById("color-buttons");
    const ice = document.createElement("div");
    ice.className = "ice-overlay";
    ice.innerHTML = `
      <div class="ice-text">❄️ BEKU! ❄️</div>
      <div class="ice-sub">Mencair dalam <span id="ice-countdown">1.5</span> detik</div>
    `;
    grid.appendChild(ice);
    
    let iceLeft = 1.5;
    const iceInterval = setInterval(() => {
      iceLeft -= 0.1;
      if (iceLeft <= 0) {
        clearInterval(iceInterval);
        ice.classList.add("shatter");
        setTimeout(() => {
          ice.remove();
          isIceBlocked = false;
          // Only re-enable answering if the client has not finished the sequence and timer is running
          if (localIndex < activeColors.length && timerInterval) {
            canAnswer = true;
          }
        }, 400);
      } else {
        const countEl = document.getElementById("ice-countdown");
        if (countEl) countEl.textContent = iceLeft.toFixed(1);
      }
    }, 100);
  }
  
  // 2. Tinta Gurita Effect
  if (powers.includes("TINTA GURITA")) {
    isInkBlocked = true;
    log("⚠️ Kamu terkena TINTA GURITA! Klik noda tinta 3x untuk membersihkan!", "danger");
    
    const disp = document.getElementById("color-display");
    const ink = document.createElement("div");
    ink.className = "ink-overlay";
    ink.innerHTML = `
      <div class="ink-splat" onclick="hitInk(this)">
        <div class="ink-hint">KLIK TINTA 3x UNTUK MEMBERSIHKAN!</div>
      </div>
    `;
    disp.appendChild(ink);
    inkClicksLeft = 3;
  }
  
  // 3. Badai Acak Effect
  if (powers.includes("BADAI ACAK")) {
    log("⚠️ Kamu terkena BADAI ACAK! Posisi tombol warna diacak!", "danger");
  }
}

function hitInk(el) {
  inkClicksLeft--;
  el.classList.add("hit");
  setTimeout(() => el.classList.remove("hit"), 250);
  
  // Shrink the ink splat
  el.style.transform = `scale(${inkClicksLeft / 3})`;
  const hint = el.querySelector(".ink-hint");
  if (hint) {
    hint.textContent = `KLIK ${inkClicksLeft}x LAGI!`;
  }
  
  if (inkClicksLeft <= 0) {
    const overlay = document.querySelector(".ink-overlay");
    if (overlay) {
      overlay.style.transition = "all 0.3s ease";
      overlay.style.opacity = 0;
      overlay.style.transform = "scale(0.5)";
      setTimeout(() => {
        overlay.remove();
        isInkBlocked = false;
      }, 300);
    }
  }
}

buildColorButtons();

// Set default server host dynamically to the serving IP/domain so remote players can connect
if (window.location.hostname) {
  document.getElementById("server-host").value = window.location.hostname + ":8765";
}
</script>
</body>
</html>"""


# ──────────────────────────────────────────────
# WEBSOCKET BRIDGE (browser ↔ TCP server)
# ──────────────────────────────────────────────

async def ws_handler(websocket):
    """Jembatan antara browser (WebSocket) dan game server (TCP)."""
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        tcp_sock.connect(("127.0.0.1", 5005))
        tcp_sock.setblocking(False)
    except Exception as e:
        await websocket.send(json.dumps({
            "type": "info",
            "message": f"❌ Server game tidak ditemukan. Jalankan server.py dulu! ({e})"
        }))
        return

    loop = asyncio.get_event_loop()
    tcp_buffer = ""

    async def tcp_to_ws():
        nonlocal tcp_buffer
        while True:
            try:
                data = await loop.run_in_executor(None, lambda: tcp_sock.recv(4096))
                if not data:
                    break
                tcp_buffer += data.decode()
                while "\n" in tcp_buffer:
                    line, tcp_buffer = tcp_buffer.split("\n", 1)
                    if line.strip():
                        await websocket.send(line)
            except BlockingIOError:
                await asyncio.sleep(0.01)
            except Exception:
                break

    async def ws_to_tcp():
        async for message in websocket:
            try:
                tcp_sock.sendall((message + "\n").encode())
            except Exception:
                break

    try:
        await asyncio.gather(tcp_to_ws(), ws_to_tcp())
    finally:
        tcp_sock.close()


# ──────────────────────────────────────────────
# HTTP SERVER (serve HTML)
# ──────────────────────────────────────────────

class HTMLHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(HTML_CONTENT.encode())

    def log_message(self, format, *args):
        pass  # suppress logs


def run_http(port=8080):
    server = HTTPServer(("", port), HTMLHandler)
    server.serve_forever()


async def main():
    print("=" * 56)
    print("   🌐  COLOR PANIC — Web Server")
    print("=" * 56)
    print("[HTTP] http://localhost:8080  ← buka di browser")
    print("[WS]   ws://localhost:8765    ← bridge ke game server")
    print("[INFO] Pastikan server.py sudah berjalan!")
    print("=" * 56)

    # HTTP server di thread terpisah
    t = threading.Thread(target=run_http, daemon=True)
    t.start()

    # WebSocket bridge
    async with websockets.serve(ws_handler, "0.0.0.0", 8765):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
