"""
╔══════════════════════════════════════════════════════════════╗
║         COLOR PANIC - CLI Client                            ║
║         Komunikasi Data - Informatika 2026                  ║
╚══════════════════════════════════════════════════════════════╝

Cara pakai:
  python3 client.py
  python3 client.py --host 192.168.1.x --port 5000
"""

import socket
import threading
import json
import sys
import time
import argparse
import random

# ──────────────────────────────────────────────
# WARNA TERMINAL (ANSI)
# ──────────────────────────────────────────────
ANSI = {
    "MERAH":  "\033[41m\033[97m",
    "BIRU":   "\033[44m\033[97m",
    "HIJAU":  "\033[42m\033[30m",
    "KUNING": "\033[43m\033[30m",
    "ORANGE": "\033[48;5;214m\033[30m",
    "UNGU":   "\033[45m\033[97m",
    "PINK":   "\033[48;5;213m\033[30m",
    "PUTIH":  "\033[47m\033[30m",
}
RESET  = "\033[0m"
BOLD   = "\033[1m"
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
CYAN   = "\033[96m"
DIM    = "\033[2m"

COLOR_KEYS = {
    "1": "MERAH",
    "2": "BIRU",
    "3": "HIJAU",
    "4": "KUNING",
    "5": "ORANGE",
    "6": "UNGU",
    "7": "PINK",
    "8": "PUTIH",
}

# ──────────────────────────────────────────────
# STATE CLIENT
# ──────────────────────────────────────────────
my_name = ""
my_score = 0
can_answer = False
game_running = False
current_round = 0
active_colors = []
local_index = 0

# Status efek dari musuh
is_ice_blocked = False
is_ink_blocked = False
ink_clicks_left = 0
is_shuffled = False
shuffled_keys = {}

# Power Phase state
in_power_phase = False
power_options = []
opponents_list = []
chosen_power = None
action_completed = False

# ──────────────────────────────────────────────
# TAMPILAN
# ──────────────────────────────────────────────
def clear():
    print("\033[2J\033[H", end="")

def banner():
    print(f"{BOLD}{CYAN}")
    print("╔══════════════════════════════════════════════╗")
    print("║   🌈  C O L O R   P A N I C  🌈            ║")
    print("║   Multiplayer Color Reaction Game           ║")
    print("║   Komunikasi Data — Informatika 2026        ║")
    print("╚══════════════════════════════════════════════╝")
    print(f"{RESET}")

def show_sequence_panel(colors, index):
    global is_ink_blocked, is_shuffled, shuffled_keys
    if is_ink_blocked:
        print(f"\n{BOLD}Urutan Warna Ronde Ini:{RESET}")
        print(f"{RED}{BOLD}[👾 TINTA GURITA - HITAM PEKAT ██████████]{RESET}")
        return

    print(f"\n{BOLD}Urutan Warna Ronde Ini (Selesaikan dari kiri ke kanan!):{RESET}")
    
    # Reverse lookup for keys
    current_key_map = shuffled_keys if is_shuffled else COLOR_KEYS
    color_to_key = {v: k for k, v in current_key_map.items()}

    parts = []
    for i, col in enumerate(colors):
        bg = ANSI.get(col, "")
        key_num = color_to_key.get(col, "?")
        
        if i < index:
            parts.append(f"{DIM}[✓] ({key_num}) {col}{RESET}")
        elif i == index:
            parts.append(f"{bg}{BOLD} ▶ ({key_num}) {col} ◀ {RESET}")
        else:
            parts.append(f"{bg}  ({key_num}) {col}  {RESET}")
    print(" ➔ ".join(parts))
    print(f"{'═'*60}\n")

def show_color_menu():
    print(f"\n{BOLD}Pilih warna (ketik angka + Enter):{RESET}")
    pairs = list(COLOR_KEYS.items())
    for i in range(0, len(pairs), 2):
        k1, v1 = pairs[i]
        bg1 = ANSI.get(v1, "")
        left = f"  [{k1}] {bg1} {v1:<8}{RESET}"
        if i + 1 < len(pairs):
            k2, v2 = pairs[i+1]
            bg2 = ANSI.get(v2, "")
            right = f"  [{k2}] {bg2} {v2:<8}{RESET}"
            print(f"{left}{right}")
        else:
            print(left)
    print()

def show_shuffled_menu(shuffled):
    print(f"\n{BOLD}{YELLOW}🌀 BADAI ACAK AKTIF! Tata letak tombol diacak:{RESET}")
    pairs = list(shuffled.items())
    for i in range(0, len(pairs), 2):
        k1, v1 = pairs[i]
        bg1 = ANSI.get(v1, "")
        left = f"  [{k1}] {bg1} {v1:<8}{RESET}"
        if i + 1 < len(pairs):
            k2, v2 = pairs[i+1]
            bg2 = ANSI.get(v2, "")
            right = f"  [{k2}] {bg2} {v2:<8}{RESET}"
            print(f"{left}{right}")
        else:
            print(left)
    print()

def show_scoreboard(scoreboard: dict):
    print(f"\n{BOLD}{CYAN}{'─'*40}")
    print(f"  📊  PAPAN SKOR SEMENTARA")
    print(f"{'─'*40}{RESET}")
    sorted_scores = sorted(scoreboard.items(), key=lambda x: x[1]["score"], reverse=True)
    medals = ["🥇", "🥈", "🥉"]
    for i, (name, data) in enumerate(sorted_scores):
        medal = medals[i] if i < 3 else "   "
        marker = f"{GREEN}◀ KAMU{RESET}" if name == my_name else ""
        
        score = data["score"]
        used_powers = data.get("used_powers", [])
        
        # Build list of used powers
        used_list = []
        if "BOM ES" in used_powers:
            used_list.append("❄️")
        if "TINTA GURITA" in used_powers:
            used_list.append("👾")
        if "BADAI ACAK" in used_powers:
            used_list.append("🌀")
        if "PERISAI" in used_powers:
            used_list.append("🛡️")
            
        if used_list:
            powers_str = f"Terpakai: " + " ".join(used_list)
        else:
            powers_str = "Terpakai: -"
            
        print(f"  {medal} {BOLD}{name:<12}{RESET}  {YELLOW}{score:>4} poin{RESET}  [{powers_str}]  {marker}")
    print(f"{CYAN}{'─'*40}{RESET}\n")

def show_leaderboard(leaderboard: list):
    clear()
    banner()
    print(f"\n{BOLD}{YELLOW}🏆  GAME SELESAI — LEADERBOARD FINAL  🏆{RESET}\n")
    medals = ["🥇", "🥈", "🥉"]
    for i, entry in enumerate(leaderboard):
        medal = medals[i] if i < 3 else f"  #{i+1}"
        marker = f"  {GREEN}← KAMU!{RESET}" if entry["name"] == my_name else ""
        print(f"  {medal}  {BOLD}{entry['name']:<14}{RESET}  {YELLOW}{entry['score']:>4} poin{RESET}{marker}")
    print()

# ──────────────────────────────────────────────
# RECEIVE LOOP (thread)
# ──────────────────────────────────────────────
def receive_loop(sock):
    global my_score, can_answer, game_running, current_round, active_colors, local_index
    global is_shuffled, shuffled_keys, is_ice_blocked, is_ink_blocked, ink_clicks_left
    global in_power_phase, power_options, opponents_list, chosen_power, action_completed

    buffer = ""
    try:
        while True:
            data = sock.recv(4096).decode()
            if not data:
                break
            buffer += data
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                if not line.strip():
                    continue
                try:
                    msg = json.loads(line)
                except:
                    continue

                t = msg.get("type")

                if t == "welcome":
                    print(f"\n{GREEN}{msg['message']}{RESET}")

                elif t == "ask_name":
                    pass

                elif t == "joined":
                    print(f"{GREEN}[✓] Bergabung sebagai {BOLD}{msg['name']}{RESET}")
                    print(f"{DIM}Pemain terhubung: {', '.join(msg['players'])}{RESET}")

                elif t == "player_joined":
                    print(f"{CYAN}[+] {msg['name']} bergabung! ({msg['count']} pemain){RESET}")

                elif t == "player_left":
                    print(f"{RED}[-] {msg['name']} keluar ({msg['count']} pemain){RESET}")

                elif t == "info":
                    print(f"\n{YELLOW}ℹ  {msg['message']}{RESET}")

                elif t == "countdown":
                    print(f"\n{BOLD}{YELLOW}  ⏳  {msg['value']}...{RESET}")
                    time.sleep(0.2)

                elif t == "game_start":
                    game_running = True
                    print(f"\n{BOLD}{GREEN}🚀 GAME DIMULAI! {msg['total_rounds']} RONDE!{RESET}")

                elif t == "round_start":
                    can_answer = False
                    in_power_phase = False
                    chosen_power = None
                    action_completed = False
                    print(f"\n{BOLD}{YELLOW}🏁 RONDE {msg['round']} / {msg['total']} DIMULAI!{RESET}")
                    print(f"Bersiaplah... sequence warna akan segera muncul! ⚡")

                elif t == "color_signal":
                    current_round = msg["round"]
                    active_colors = msg["colors"]
                    local_index = 0
                    can_answer = True
                    is_shuffled = False
                    is_ice_blocked = False
                    is_ink_blocked = False

                    # Cek Badai Acak
                    active_powers = msg.get("active_powers", [])
                    if "BADAI ACAK" in active_powers:
                        is_shuffled = True
                        colors_list = list(COLOR_KEYS.values())
                        keys = list(COLOR_KEYS.keys())
                        random.shuffle(keys)
                        shuffled_keys = {keys[i]: colors_list[i] for i in range(len(keys))}
                        show_shuffled_menu(shuffled_keys)
                    else:
                        show_color_menu()

                    # Cek Bom Es
                    if "BOM ES" in active_powers:
                        is_ice_blocked = True
                        can_answer = False
                        print(f"\n{BLUE}{BOLD}❄️ TERCENGKERAM ES! Tombol beku selama 1.5 detik... ❄️{RESET}")
                        def unfreeze():
                            global is_ice_blocked, can_answer
                            time.sleep(1.5)
                            is_ice_blocked = False
                            if local_index < len(active_colors):
                                can_answer = True
                            print(f"\n{GREEN}❄️ Es mencair! Silakan ketik jawaban!{RESET}")
                            if not is_ink_blocked:
                                show_sequence_panel(active_colors, local_index)
                            else:
                                print(f"{YELLOW}👾 TINTA GURITA masih menutupi sequence warna! Ketik 'c' 3x!{RESET}")
                        threading.Thread(target=unfreeze, daemon=True).start()

                    # Cek Tinta Gurita
                    if "TINTA GURITA" in active_powers:
                        is_ink_blocked = True
                        ink_clicks_left = 3
                        print(f"\n{RED}{BOLD}👾 TINTA GURITA! Sequence Anda tertutup tinta!{RESET}")
                        print(f"{YELLOW}Ketik 'c' + Enter sebanyak 3 kali untuk membersihkannya!{RESET}")

                    if not is_ink_blocked and not is_ice_blocked:
                        show_sequence_panel(active_colors, local_index)

                elif t == "answer_result":
                    if msg["correct"]:
                        my_score = msg["total_score"]
                        if msg["completed"]:
                            can_answer = False
                            print(f"{GREEN}{BOLD}🏆  SEQUENCE SELESAI! (+{msg['points']} poin bonus) → Total: {my_score}{RESET}")
                        else:
                            print(f"{GREEN}✓ Benar! (+1 poin) → Total: {my_score}{RESET}")
                    else:
                        print(f"{RED}❌  SALAH! Coba lagi!{RESET}")

                elif t == "round_result":
                    can_answer = False
                    show_scoreboard(msg["scoreboard"])

                elif t == "power_phase_start":
                    in_power_phase = True
                    chosen_power = None
                    action_completed = False
                    power_options = msg.get("available_powers", [])
                    opponents_list = msg.get("opponents", [])

                    clear()
                    banner()
                    print(f"\n{BOLD}{CYAN}⚡ FASE KEKUATAN! (Durasi: {msg.get('duration', 7)} detik) ⚡{RESET}")
                    print("Pilih kekuatan untuk digunakan:")
                    
                    # Filter and show only available powers
                    available_powers_list = [p for p in ["BOM ES", "TINTA GURITA", "BADAI ACAK", "PERISAI"] if p in power_options]
                    for i, pow in enumerate(available_powers_list):
                        print(f"  [{i+1}] {pow:<12}")
                    
                    if available_powers_list:
                        print(f"\n{DIM}Ketik angka (1-{len(available_powers_list)}) dan tekan Enter untuk memilih kekuatan...{RESET}")
                    else:
                        print(f"\n{RED}Semua kekuatan Anda sudah habis dipakai!{RESET}")
                        action_completed = True

                elif t == "power_used_broadcast":
                    print(f"\n{YELLOW}💥 [KEKUATAN] {msg['by']} menggunakan {msg['power']} ke {msg['target']}!{RESET}")

                elif t == "power_phase_end":
                    in_power_phase = False
                    chosen_power = None
                    action_completed = False
                    print(f"\n{CYAN}⚡ Fase kekuatan berakhir! Menunggu ronde baru dimulai...{RESET}")

                elif t == "game_over":
                    game_running = False
                    show_leaderboard(msg["leaderboard"])
                    print(f"{DIM}Ketik 'chat <pesan>' untuk ngobrol, atau Ctrl+C untuk keluar.{RESET}")

                elif t == "chat":
                    print(f"{CYAN}💬 {msg['from']}: {msg['message']}{RESET}")

                elif t == "pong":
                    pass

    except Exception as e:
        print(f"\n{RED}[DISCONNECT] Koneksi terputus: {e}{RESET}")
        print(f"{YELLOW}Ketik 'restart' untuk mencoba menghubungkan kembali, atau 'exit' untuk keluar.{RESET}")
    finally:
        try:
            sock.close()
        except:
            pass

# ──────────────────────────────────────────────
# INPUT LOOP (main thread)
# ──────────────────────────────────────────────
def input_loop(sock):
    global can_answer, is_ink_blocked, ink_clicks_left, is_ice_blocked
    global in_power_phase, power_options, opponents_list, chosen_power, action_completed
    global is_shuffled, shuffled_keys, active_colors, local_index

    while True:
        try:
            user_input = input().strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{YELLOW}Sampai jumpa! 👋{RESET}")
            return False

        if not user_input:
            continue

        # ── FASE KEKUATAN INPUT ──
        if in_power_phase:
            if action_completed:
                print(f"{YELLOW}Aksi selesai. Menunggu ronde berikutnya...{RESET}")
                continue

            # Bersihkan karakter non-angka untuk pemilihan menu numerik
            cleaned_input = "".join(c for c in user_input if c.isdigit())

            available_powers_list = [p for p in ["BOM ES", "TINTA GURITA", "BADAI ACAK", "PERISAI"] if p in power_options]

            if chosen_power is None:
                if cleaned_input and 1 <= int(cleaned_input) <= len(available_powers_list):
                    choice = available_powers_list[int(cleaned_input) - 1]
                    
                    if choice == "PERISAI":
                        send(sock, {"type": "use_power", "power": "PERISAI", "target": "self"})
                        print(f"{GREEN}🛡️ Perisai Pelindung Aktif! Serangan lawan ronde berikutnya akan diblokir.{RESET}")
                        action_completed = True
                    else:
                        chosen_power = choice
                        if len(opponents_list) == 0:
                            send(sock, {"type": "use_power", "power": chosen_power, "target": ""})
                            print(f"{YELLOW}💥 Tidak ada lawan terhubung, serangan diluncurkan ke udara!{RESET}")
                            action_completed = True
                        else:
                            print(f"\n{BOLD}Pilih target lawan untuk diserang:{RESET}")
                            for idx, opp in enumerate(opponents_list):
                                print(f"  [{idx+1}] {opp}")
                            print(f"{DIM}Ketik angka target lawan...{RESET}")
                else:
                    print(f"{RED}Masukkan angka 1-{len(available_powers_list)} sesuai menu kekuatan!{RESET}")
            else:
                try:
                    if not cleaned_input:
                        raise ValueError
                    target_idx = int(cleaned_input) - 1
                    if 0 <= target_idx < len(opponents_list):
                        target_name = opponents_list[target_idx]
                        send(sock, {"type": "use_power", "power": chosen_power, "target": target_name})
                        print(f"{GREEN}💥 Mengirim serangan {chosen_power} ke {target_name}!{RESET}")
                        action_completed = True
                    else:
                        print(f"{RED}Pilihan target tidak valid!{RESET}")
                except ValueError:
                    print(f"{RED}Masukkan angka target lawan!{RESET}")
            continue

        # ── GAMEPLAY INPUT ──
        if is_ice_blocked:
            print(f"{RED}❌ Tombol beku oleh BOM ES! Tunggu es mencair!{RESET}")
            continue

        if is_ink_blocked:
            if user_input.lower() == "c":
                ink_clicks_left -= 1
                if ink_clicks_left <= 0:
                    is_ink_blocked = False
                    print(f"\n{GREEN}👾 Tinta bersih! Urutan warna terungkap!{RESET}")
                    show_sequence_panel(active_colors, local_index)
                else:
                    print(f"👾 Tinta terpukul! Klik 'c' {ink_clicks_left}x lagi!")
            else:
                print(f"{RED}👾 Urutan warna terhalang tinta! Ketik 'c' + Enter untuk membersihkan!{RESET}")
            continue

        if can_answer:
            chosen_color = None

            if is_shuffled:
                if user_input in shuffled_keys:
                    chosen_color = shuffled_keys[user_input]
            else:
                if user_input in COLOR_KEYS:
                    chosen_color = COLOR_KEYS[user_input]

            # Input nama warna langsung
            if user_input.upper() in COLOR_KEYS.values():
                chosen_color = user_input.upper()

            if chosen_color:
                expected = active_colors[local_index]
                if chosen_color == expected:
                    send(sock, {"type": "answer", "color": chosen_color})
                    local_index += 1
                    print(f"{GREEN}✓ Benar!{RESET}")

                    if local_index >= len(active_colors):
                        can_answer = False
                        print(f"\n{GREEN}{BOLD}🏆 SEQUENCE SELESAI! Menunggu pemain lain...{RESET}")
                    else:
                        show_sequence_panel(active_colors, local_index)
                else:
                    print(f"{RED}❌ SALAH! Warna target saat ini: {ANSI.get(expected,'')}{expected}{RESET} (Anda menekan {chosen_color})")
            else:
                print(f"{RED}⚠ Input tidak valid! Ketik angka 1-8 sesuai menu warna.{RESET}")
        else:
            # Chat
            if user_input.lower().startswith("chat "):
                msg = user_input[5:]
                send(sock, {"type": "chat", "message": msg})
            elif user_input.lower() in ("quit", "exit", "keluar"):
                return False
            elif user_input.lower() in ("restart", "main lagi"):
                print(f"\n{GREEN}Memulai ulang koneksi...{RESET}")
                return True
            elif user_input.lower() in ("help", "?", "bantuan"):
                show_color_menu()
            else:
                print(f"{DIM}Ketik 'chat <pesan>' untuk mengobrol, 'restart' untuk main lagi, atau 'exit'.{RESET}")

def send(sock, data: dict):
    try:
        sock.sendall((json.dumps(data) + "\n").encode())
    except:
        pass

# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────
def run_game(host, port):
    global my_name, my_score, can_answer, game_running, current_round, active_colors, local_index
    global is_ice_blocked, is_ink_blocked, ink_clicks_left, is_shuffled, shuffled_keys
    global in_power_phase, power_options, opponents_list, chosen_power, action_completed

    # Reset state
    my_score = 0
    can_answer = False
    game_running = False
    current_round = 0
    active_colors = []
    local_index = 0
    is_ice_blocked = False
    is_ink_blocked = False
    ink_clicks_left = 0
    is_shuffled = False
    shuffled_keys = {}
    in_power_phase = False
    power_options = []
    opponents_list = []
    chosen_power = None
    action_completed = False

    clear()
    banner()

    print(f"{CYAN}Menghubungkan ke server {host}:{port}...{RESET}")

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        print(f"{GREEN}[✓] Terhubung!{RESET}")
    except Exception as e:
        print(f"{RED}[✗] Gagal terhubung: {e}{RESET}")
        print(f"{YELLOW}Ketik 'restart' untuk mencoba lagi, atau 'exit' untuk keluar.{RESET}")
        while True:
            try:
                cmd = input().strip().lower()
                if cmd in ("restart", "main lagi"):
                    return True
                elif cmd in ("quit", "exit", "keluar"):
                    return False
            except (EOFError, KeyboardInterrupt):
                return False

    # Minta nama
    my_name = input(f"\n{BOLD}Masukkan nama kamu: {RESET}").strip()
    if not my_name:
        my_name = "Player"
    send(sock, {"type": "join", "name": my_name})

    print(f"\n{DIM}Menunggu pemain lain... (butuh minimal 2 pemain){RESET}")
    print(f"{DIM}Ketik 'help' untuk bantuan{RESET}\n")

    # Start receive thread
    rx = threading.Thread(target=receive_loop, args=(sock,), daemon=True)
    rx.start()

    # Input loop di main thread
    should_restart = input_loop(sock)
    try:
        sock.close()
    except:
        pass
    return should_restart


def main():
    parser = argparse.ArgumentParser(description="Color Panic — CLI Client")
    parser.add_argument("--host", default="127.0.0.1", help="Alamat server (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=5000, help="Port server (default: 5000)")
    args = parser.parse_args()

    while True:
        if not run_game(args.host, args.port):
            break


if __name__ == "__main__":
    main()
