"""
╔══════════════════════════════════════════════════════════════╗
║         COLOR PANIC - TCP/UDP Game Server                   ║
║         Komunikasi Data - Informatika 2026                  ║
║         Multiplayer Color Reaction Game                     ║
╚══════════════════════════════════════════════════════════════╝

Protokol:
- TCP  → koneksi pemain, skor, join/leave
- UDP  → broadcast warna real-time ke semua pemain
"""

import socket
import threading
import time
import random
import json

# ──────────────────────────────────────────────
# KONFIGURASI SERVER
# ──────────────────────────────────────────────
TCP_HOST = "0.0.0.0"
TCP_PORT = 5005
UDP_PORT = 5006

COLORS = ["MERAH", "BIRU", "HIJAU", "KUNING", "ORANGE", "UNGU", "PINK", "PUTIH"]
TOTAL_ROUNDS = 5
COLORS_PER_ROUND = 5   # Jumlah warna per ronde (5 warna sesuai request)
MIN_PLAYERS = 2
MAX_PLAYERS = 4

# ──────────────────────────────────────────────
# STATE GLOBAL
# ──────────────────────────────────────────────
players = {}        # { addr: { name, score, conn, ready } }
lock = threading.RLock()
game_active = False
current_sequence = []
round_number = 0

# ──────────────────────────────────────────────
# FUNGSI KIRIM PESAN
# ──────────────────────────────────────────────
def send_tcp(conn, data: dict):
    """Kirim pesan JSON ke satu pemain via TCP."""
    try:
        msg = json.dumps(data) + "\n"
        conn.sendall(msg.encode())
    except:
        pass

def broadcast_tcp(data: dict, exclude=None):
    """Broadcast pesan ke semua pemain via TCP."""
    with lock:
        for addr, p in players.items():
            if addr != exclude:
                send_tcp(p["conn"], data)

def broadcast_udp(udp_sock, data: dict):
    """Broadcast pesan via UDP ke semua pemain (real-time signal)."""
    msg = json.dumps(data).encode()
    with lock:
        for addr, p in players.items():
            try:
                udp_sock.sendto(msg, (addr[0], UDP_PORT + 1))
            except:
                pass

# ──────────────────────────────────────────────
# LOGIKA GAME
# ──────────────────────────────────────────────
def start_game(udp_sock):
    """Loop utama game: jalankan ronde demi ronde dengan banyak warna sekaligus."""
    global game_active, current_sequence, round_number

    game_active = True
    round_number = 0

    # Countdown sebelum mulai
    for i in range(3, 0, -1):
        broadcast_tcp({"type": "countdown", "value": i})
        broadcast_udp(udp_sock, {"type": "countdown", "value": i})
        time.sleep(1)

    broadcast_tcp({"type": "game_start", "total_rounds": TOTAL_ROUNDS, "colors_per_round": COLORS_PER_ROUND})

    while round_number < TOTAL_ROUNDS:
        round_number += 1

        # Generate sequence warna acak untuk ronde ini
        current_sequence = [random.choice(COLORS) for _ in range(COLORS_PER_ROUND)]
        print(f"[RONDE {round_number}] Sequence: {' → '.join(current_sequence)}")

        # Reset state pemain untuk ronde baru
        with lock:
            for p in players.values():
                p["current_index"] = 0
                p["completed"] = False

        # Kirim info awal ronde
        broadcast_tcp({
            "type": "round_start",
            "round": round_number,
            "total": TOTAL_ROUNDS,
            "sub_total": COLORS_PER_ROUND
        })

        # Kirim signal seluruh warna sekaligus
        signal_data = {
            "type": "color_signal",
            "colors": current_sequence,
            "round": round_number,
            "total": TOTAL_ROUNDS
        }
        broadcast_udp(udp_sock, signal_data)
        
        # Kirim secara personal via TCP dengan menyertakan active_powers masing-masing
        with lock:
            for addr, p in players.items():
                player_signal = {
                    "type": "color_signal",
                    "colors": current_sequence,
                    "round": round_number,
                    "total": TOTAL_ROUNDS,
                    "active_powers": p.get("pending_powers", [])
                }
                send_tcp(p["conn"], player_signal)
                p["pending_powers"] = []  # Reset setelah dikirim

        # Tunggu maks 5 detik untuk menyelesaikan seluruh sequence, lanjut jika semua selesai
        SIGNAL_TIMEOUT = 5.0
        POLL_INTERVAL = 0.1
        elapsed = 0.0
        while elapsed < SIGNAL_TIMEOUT:
            time.sleep(POLL_INTERVAL)
            elapsed += POLL_INTERVAL
            with lock:
                num_players = len(players)
                num_completed = len([p for p in players.values() if p.get("completed", False)])
            if num_players > 0 and num_completed >= num_players:
                print(f"  │  ✓ Semua pemain selesai! ({elapsed:.1f}s)")
                break

        # Kirim update skor setelah ronde selesai
        with lock:
            scoreboard = {
                p["name"]: {
                    "score": p["score"],
                    "used_powers": p.get("used_powers", [])
                }
                for p in players.values()
            }
        broadcast_tcp({"type": "round_result", "round": round_number, "scoreboard": scoreboard})
        broadcast_udp(udp_sock, {"type": "round_result", "scoreboard": scoreboard})
        print(f"  └─ Ronde {round_number} selesai!")

        # JIKA BELUM CAPAI RONDE AKHIR, MASUK FASE KEKUATAN
        if round_number < TOTAL_ROUNDS:
            time.sleep(1.0)
            with lock:
                # Reset power status
                for p in players.values():
                    p["power_used"] = False
                    p["shield_active"] = False
                    p["pending_powers"] = []
                    p.setdefault("used_powers", [])
                
                # Kirim sinyal fase kekuatan ke masing-masing client dengan sisa kekuatan yang tersedia
                player_names = [p["name"] for p in players.values()]
                all_powers = ["BOM ES", "TINTA GURITA", "BADAI ACAK", "PERISAI"]
                for addr, p in players.items():
                    available = [pow for pow in all_powers if pow not in p["used_powers"]]
                    send_tcp(p["conn"], {
                        "type": "power_phase_start",
                        "opponents": [name for name in player_names if name != p["name"]],
                        "available_powers": available,
                        "duration": 7
                    })
            
            # Tunggu 7 detik fase kekuatan
            time.sleep(7.0)
            
            # Selesaikan perisai
            with lock:
                for p in players.values():
                    if p.get("shield_active", False):
                        blocked_attacks = p.get("pending_powers", [])
                        if len(blocked_attacks) > 0:
                            blocked_str = ", ".join(blocked_attacks)
                            broadcast_tcp({
                                "type": "info",
                                "message": f"🛡️ Perisai {p['name']} berhasil memblokir serangan ({blocked_str})!"
                            })
                            print(f"[SHIELD] Perisai {p['name']} memblokir {blocked_str}")
                        p["pending_powers"] = []
                        p["shield_active"] = False
            
            # Kirim sinyal fase kekuatan berakhir
            broadcast_tcp({"type": "power_phase_end"})
            time.sleep(1.0)
        else:
            time.sleep(1.2)

    # ── GAME SELESAI ──
    game_active = False
    with lock:
        final = sorted(
            [{"name": p["name"], "score": p["score"]} for p in players.values()],
            key=lambda x: x["score"], reverse=True
        )
    broadcast_tcp({"type": "game_over", "leaderboard": final})
    broadcast_udp(udp_sock, {"type": "game_over", "leaderboard": final})
    print("\n[SERVER] Game selesai!")
    print(f"[LEADERBOARD] {final}")

    # Reset scores and spent powers for new game
    with lock:
        for p in players.values():
            p["score"] = 0
            p["ready"] = False
            p["used_powers"] = []


def check_answer(addr, color_answer):
    """Validasi jawaban pemain, beri poin jika benar."""
    global current_sequence
    if not game_active or addr not in players:
        return

    player = players[addr]
    if player.get("completed", False):
        return

    idx = player.get("current_index", 0)
    if idx >= len(current_sequence):
        return

    expected_color = current_sequence[idx]

    if color_answer.upper() == expected_color:
        player["current_index"] = idx + 1
        player["score"] += 1  # 1 poin untuk setiap warna benar

        # Cek apakah sudah menyelesaikan seluruh sequence
        if player["current_index"] == len(current_sequence):
            player["completed"] = True
            with lock:
                completed_count = len([p for p in players.values() if p.get("completed", False)])
            # Bonus kecepatan penyelesaian sequence
            speed_bonus = max(10 - (completed_count - 1) * 2, 2)
            player["score"] += speed_bonus

            send_tcp(player["conn"], {
                "type": "answer_result",
                "correct": True,
                "index": player["current_index"],
                "completed": True,
                "points": speed_bonus + 1,
                "total_score": player["score"]
            })

            broadcast_tcp({
                "type": "info",
                "message": f"🏆 {player['name']} menyelesaikan sequence ke-{completed_count}! (+{speed_bonus} poin bonus)"
            })
            print(f"[✓] {player['name']} menyelesaikan seluruh sequence! (Posisi {completed_count}, +{speed_bonus} bonus)")
        else:
            send_tcp(player["conn"], {
                "type": "answer_result",
                "correct": True,
                "index": player["current_index"],
                "completed": False,
                "points": 1,
                "total_score": player["score"]
            })
            print(f"[✓] {player['name']} benar: {color_answer} ({player['current_index']}/{len(current_sequence)})")
    else:
        send_tcp(player["conn"], {
            "type": "answer_result",
            "correct": False,
            "index": idx,
            "completed": False,
            "points": 0,
            "total_score": player["score"]
        })
        print(f"[✗] {player['name']} salah! (jawab: {color_answer}, benar: {expected_color})")


# ──────────────────────────────────────────────
# HANDLE CLIENT (Thread per Pemain)
# ──────────────────────────────────────────────
def handle_client(conn, addr, udp_sock):
    """Thread handler untuk tiap pemain yang konek via TCP."""
    print(f"[+] Koneksi baru dari {addr}")
    buffer = ""

    try:
        # Minta nama pemain
        send_tcp(conn, {"type": "welcome", "message": "Selamat datang di COLOR PANIC! 🎨"})
        send_tcp(conn, {"type": "ask_name"})

        while True:
            data = conn.recv(1024).decode()
            if not data:
                break

            buffer += data
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                if not line.strip():
                    continue
                try:
                    msg = json.loads(line)
                except json.JSONDecodeError:
                    continue

                msg_type = msg.get("type")

                # ── JOIN ──
                if msg_type == "join":
                    name = msg.get("name", f"Player{len(players)+1}")[:12]
                    with lock:
                        players[addr] = {
                            "name": name,
                            "score": 0,
                            "conn": conn,
                            "ready": False,
                            "pending_powers": [],
                            "power_used": False,
                            "shield_active": False,
                            "used_powers": []
                        }
                    send_tcp(conn, {
                        "type": "joined",
                        "name": name,
                        "players": [p["name"] for p in players.values()]
                    })
                    broadcast_tcp(
                        {"type": "player_joined", "name": name, "count": len(players)},
                        exclude=addr
                    )
                    print(f"[JOIN] {name} bergabung ({len(players)} pemain)")

                    # Auto-start kalau cukup pemain dan belum main
                    if len(players) >= MIN_PLAYERS and not game_active:
                        broadcast_tcp({
                            "type": "info",
                            "message": f"⚡ {len(players)} pemain terhubung! Game mulai dalam 3 detik..."
                        })
                        t = threading.Thread(target=start_game, args=(udp_sock,), daemon=True)
                        t.start()

                # ── JAWABAN WARNA ──
                elif msg_type == "answer":
                    check_answer(addr, msg.get("color", ""))

                # ── GUNAKAN KEKUATAN ──
                elif msg_type == "use_power":
                    target_name = msg.get("target")
                    power_type = msg.get("power", "")
                    with lock:
                        attacker = players.get(addr)
                        if attacker and not attacker.get("power_used"):
                            attacker.setdefault("used_powers", [])
                            if power_type in attacker["used_powers"]:
                                print(f"[POWER] {attacker['name']} mencoba menggunakan {power_type} lagi (ditolak)")
                                continue
                            
                            if power_type == "PERISAI":
                                attacker["shield_active"] = True
                                attacker["power_used"] = True
                                attacker["used_powers"].append("PERISAI")
                                broadcast_tcp({
                                    "type": "power_used_broadcast",
                                    "by": attacker["name"],
                                    "target": "dirinya sendiri",
                                    "power": "PERISAI"
                                })
                                print(f"[POWER] {attacker['name']} menggunakan PERISAI")
                            elif power_type in ["BOM ES", "TINTA GURITA", "BADAI ACAK"]:
                                # Cari target player berdasarkan name
                                target_player = None
                                for p_addr, p in players.items():
                                    if p["name"] == target_name:
                                        target_player = p
                                        break
                                
                                if target_player and target_player != attacker:
                                    attacker["used_powers"].append(power_type)
                                    target_player.setdefault("pending_powers", []).append(power_type)
                                    attacker["power_used"] = True
                                    
                                    # Broadcast log/info ke semua player
                                    broadcast_tcp({
                                        "type": "power_used_broadcast",
                                        "by": attacker["name"],
                                        "target": target_name,
                                        "power": power_type
                                    })
                                    print(f"[POWER] {attacker['name']} menggunakan {power_type} ke {target_name}")

                # ── CHAT ──
                elif msg_type == "chat":
                    with lock:
                        sender = players.get(addr, {}).get("name", "?")
                    broadcast_tcp({
                        "type": "chat",
                        "from": sender,
                        "message": msg.get("message", "")[:100]
                    })

                # ── PING ──
                elif msg_type == "ping":
                    send_tcp(conn, {"type": "pong"})

    except Exception as e:
        print(f"[ERR] {addr}: {e}")
    finally:
        with lock:
            name = players.pop(addr, {}).get("name", str(addr))
        broadcast_tcp({"type": "player_left", "name": name, "count": len(players)})
        conn.close()
        print(f"[-] {name} keluar")


# ──────────────────────────────────────────────
# MAIN SERVER
# ──────────────────────────────────────────────
def main():
    def get_local_ip():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    local_ip = get_local_ip()
    print("=" * 56)
    print("   🎨  COLOR PANIC — Game Server  🎨")
    print("   Komunikasi Data | Informatika 2026")
    print("=" * 56)
    print(f"[TCP] Listening on {TCP_HOST}:{TCP_PORT} (IP lokal: {local_ip})")
    print(f"[UDP] Broadcasting on port {UDP_PORT}")
    print(f"[GAME] {TOTAL_ROUNDS} ronde | {len(COLORS)} warna | {MIN_PLAYERS}-{MAX_PLAYERS} pemain")
    print("=" * 56)

    # Setup UDP socket untuk broadcast real-time
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # Setup TCP server
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcp_sock.bind((TCP_HOST, TCP_PORT))
    tcp_sock.listen(MAX_PLAYERS)

    print("[SERVER] Menunggu pemain...")

    while True:
        try:
            conn, addr = tcp_sock.accept()
            t = threading.Thread(
                target=handle_client,
                args=(conn, addr, udp_sock),
                daemon=True
            )
            t.start()
        except KeyboardInterrupt:
            print("\n[SERVER] Server dihentikan.")
            break
        except Exception as e:
            print(f"[ERR] Accept gagal: {e}")

    tcp_sock.close()
    udp_sock.close()


if __name__ == "__main__":
    main()
