#!/usr/bin/env python3
# AFKAR VIDEO EDITOR PRO | TERMUX EDITION | BY AFKAR
import os
import json
import sys
import time
import shutil
import subprocess
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature
from datetime import datetime, timezone
import secrets
import platform
import hashlib
import base64

APP_NAME = "AFKAR VIDEO EDITOR PRO"
DEFAULT_USER = "ghost"
ROOT = Path(__file__).resolve().parent.parent
USER_FILE = ROOT / "user.json"
STORAGE_DIR = Path.home() / "storage" / "downloads"
PROJECT_STORAGE = STORAGE_DIR / "afkar-video-editor-pro"

def display_path(path):
    path = Path(path)
    home = Path.home()
    try:
        return "~/" + str(path.relative_to(home))
    except ValueError:
        return str(path)
INPUT_DIR = PROJECT_STORAGE / "input"
OUTPUT_DIR = PROJECT_STORAGE / "output"

INPUT_ROOT = PROJECT_STORAGE / "input"
OUTPUT_ROOT = PROJECT_STORAGE / "output"

def set_feature_dirs(folder_name):
    global INPUT_DIR, OUTPUT_DIR
    INPUT_DIR = INPUT_ROOT / folder_name
    OUTPUT_DIR = OUTPUT_ROOT / folder_name
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def reset_root_dirs():
    global INPUT_DIR, OUTPUT_DIR
    INPUT_DIR = INPUT_ROOT
    OUTPUT_DIR = OUTPUT_ROOT

VIDEO_EXTS = {".mp4", ".mkv", ".mov", ".webm", ".avi", ".m4v", ".ts", ".3gp"}
AUDIO_EXTS = {".mp3", ".m4a", ".aac", ".wav", ".flac", ".ogg"}
RESET = "\033[0m"
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
DIM = "\033[2m"
BOLD = "\033[1m"
EFFECTS = os.environ.get("NO_EFFECTS") != "1"

def run_cmd(args, capture=False):
    try:
        return subprocess.run(
            [str(x) for x in args],
            check=True,
            text=True,
            stdout=subprocess.PIPE if capture else None,
            stderr=subprocess.PIPE if capture else None,
        )
    except FileNotFoundError:
        raise RuntimeError("FFmpeg/FFprobe tidak ditemukan. Jalankan: pkg install ffmpeg")
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or "").strip()
        if len(detail) > 1200:
            detail = detail[-1200:]
        raise RuntimeError("FFmpeg gagal memproses file." + ("\n" + detail if detail else ""))

def pause():
    try:
        input(f"\n{DIM}Tekan Enter untuk kembali ke menu...{RESET}")
    except (EOFError, KeyboardInterrupt):
        pass

def clear():
    os.system("clear")

def banner():
    FONT = {
        "R": ["██████╗ ", "██╔══██╗", "██████╔╝", "██╔══██╗", "██║  ██║", "╚═╝  ╚═╝"],
        "E": ["███████╗", "██╔════╝", "█████╗  ", "██╔══╝  ", "███████╗", "╚══════╝"],
        "N": ["███╗   ██╗", "████╗  ██║", "██╔██╗ ██║", "██║╚██╗██║", "██║ ╚████║", "╚═╝  ╚═══╝"],
        "D": ["██████╗ ", "██╔══██╗", "██║  ██║", "██║  ██║", "██████╔╝", "╚═════╝ "],
        "I": ["██╗", "██║", "██║", "██║", "██║", "╚═╝"],
        "A": [" █████╗ ", "██╔══██╗", "███████║", "██╔══██║", "██║  ██║", "╚═╝  ╚═╝"],
        "F": ["███████╗", "██╔════╝", "█████╗  ", "██╔══╝  ", "██║     ", "╚═╝     "],
        "K": ["██╗  ██╗", "██║ ██╔╝", "█████╔╝ ", "██╔═██╗ ", "██║  ██╗", "╚═╝  ╚═╝"],
    }

    width = min(shutil.get_terminal_size((56, 24)).columns, 60)
    width = max(width, 30)
    inner = width - 2

    def build_word(word):
        return [
            "".join(FONT[ch][r] for ch in word)
            for r in range(6)
        ]

    rows = [" " * inner]
    for idx, word in enumerate(("RENDI", "AFKAR")):
        rows.extend(line.center(inner) for line in build_word(word))
        if idx == 0:
            rows.append(" " * inner)

    rows.extend([
        " " * inner,
        APP_NAME[:inner].center(inner),
        "TERMUX EDITION | BY AFKAR".center(inner),
        " " * inner,
    ])

    print(f"{DIM}╔{'═' * inner}╗{RESET}")

    for i, line in enumerate(rows):
        # Animasi turun: setiap baris muncul satu per satu dari atas
        if EFFECTS:
            time.sleep(0.045)

        if i == len(rows) - 2:
            styled = f"{BOLD}{CYAN}{line}{RESET}"
        elif i == len(rows) - 3:
            styled = f"{BOLD}{YELLOW}{line}{RESET}"
        elif "█" in line:
            styled = f"{BOLD}{CYAN}{line}{RESET}"
        else:
            styled = line

        print(f"{DIM}║{RESET}{styled}{DIM}║{RESET}", flush=True)

    print(f"{DIM}╚{'═' * inner}╝{RESET}")


def load_user_name():
    try:
        data = json.loads(USER_FILE.read_text(encoding="utf-8"))
        name = str(data.get("name", "")).strip()[:20]
        return name
    except (OSError, ValueError, TypeError, AttributeError):
        return ""


def save_user_name(name):
    try:
        USER_FILE.write_text(
            json.dumps({"name": name}, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        return True
    except OSError:
        return False


def type_out(text, color=YELLOW, delay=0.025):
    for ch in text:
        print(ch, end="", flush=True)
        if EFFECTS:
            time.sleep(delay)
    print(RESET, end="")


def show_welcome(name):
    message = "Selamat Datang"
    if name:
        message += ", " + name

    print()
    type_out(f"{BOLD}{YELLOW}{message}{RESET}", delay=0.035)
    print()
    if EFFECTS:
        time.sleep(0.35)


def introduce_user():
    print()
    type_out(f"{CYAN}[AFKAR SETUP]{RESET}", delay=0.02)
    print(" Perkenalkan dirimu sebelum mulai menggunakan tool ini.")
    while True:
        try:
            name = input(f"{GREEN}Nama kamu: {RESET}").strip()[:20]
        except (EOFError, KeyboardInterrupt):
            name = DEFAULT_USER
            print()
            break

        if name:
            break
        print(f"{YELLOW}[!] Nama tidak boleh kosong.{RESET}")

    if not save_user_name(name):
        print(f"{YELLOW}[!] Nama tidak dapat disimpan; sesi ini tetap berjalan.{RESET}")

    print()
    type_out(f"{GREEN}[+] Halo, {name}! Selamat datang di AFKAR VIDEO EDITOR PRO.{RESET}")
    if EFFECTS:
        time.sleep(0.6)
    return name


def change_user_name():
    current_name = load_user_name() or DEFAULT_USER
    print(f"\\n{CYAN}[GANTI NAMA PENGGUNA]{RESET}")
    print(f"Nama saat ini: {YELLOW}{current_name}{RESET}")

    while True:
        try:
            new_name = input(
                f"{GREEN}Masukkan nama baru (0 untuk batal): {RESET}"
            ).strip()[:20]
        except (EOFError, KeyboardInterrupt):
            print()
            return

        if new_name == "0":
            print(f"{YELLOW}[!] Ganti nama dibatalkan.{RESET}")
            return

        if new_name:
            break

        print(f"{YELLOW}[!] Nama tidak boleh kosong.{RESET}")

    if save_user_name(new_name):
        print(f"{GREEN}[+] Nama berhasil diubah menjadi {new_name}.{RESET}")
    else:
        print(f"{RED}[!] Nama gagal disimpan.{RESET}")


VIDEO_APP_ID = "afkar-video-editor-pro"
VIDEO_VALID_PLANS = {
    "1 Hari", "7 Hari", "1 Bulan", "1 Tahun", "Lifetime"
}
VIDEO_PRIVATE_DIR = Path.home() / ".afkar_video_editor_license"
VIDEO_LICENSE_DIR = Path.home() / "storage" / "downloads" / "AFKAR_LISENSI"
VIDEO_LICENSE_FILE = VIDEO_LICENSE_DIR / "video_editor_license.key"
VIDEO_MACHINE_FILE = VIDEO_PRIVATE_DIR / "machine.id"
VIDEO_PUBLIC_KEY_PEM = b'-----BEGIN PUBLIC KEY-----\nMCowBQYDK2VwAyEAI8COWafKSK7Jv6Vn6Ptrajn0ETOa5M5kbPnbeIH/4Vc=\n-----END PUBLIC KEY-----\n'
def video_machine_id():
    VIDEO_PRIVATE_DIR.mkdir(parents=True, exist_ok=True)
    raw_id = ""
    try:
        raw_id = VIDEO_MACHINE_FILE.read_text(encoding="utf-8").strip()
    except OSError:
        pass

    if not raw_id:
        raw_id = secrets.token_hex(16)
        VIDEO_MACHINE_FILE.write_text(raw_id, encoding="utf-8")
        try:
            VIDEO_MACHINE_FILE.chmod(0o600)
        except OSError:
            pass

    raw = f"{raw_id}|{platform.system()}|{platform.machine()}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
def video_b64url_decode(value):
    if not isinstance(value, str) or not value:
        raise ValueError("Bagian Base64 kosong.")
    if not __import__("re").fullmatch(r"[A-Za-z0-9_-]+", value):
        raise ValueError("Format Base64 tidak valid.")
    decoded = base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
    if base64.urlsafe_b64encode(decoded).decode("ascii").rstrip("=") != value:
        raise ValueError("Base64 tidak canonical.")
    return decoded
def video_parse_datetime(value):
    if not isinstance(value, str):
        raise ValueError("Tanggal tidak valid.")
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError("Zona waktu tanggal tidak ada.")
    return dt.astimezone(timezone.utc)
def verify_video_license_key(license_key):
    try:
        license_key = license_key.strip()
        if not license_key.startswith("AFKAR-"):
            return False, "Prefix lisensi tidak valid.", None

        parts = license_key[6:].split(".")
        if len(parts) != 2:
            return False, "Format lisensi tidak valid.", None

        payload_bytes = video_b64url_decode(parts[0])
        signature = video_b64url_decode(parts[1])
        if len(signature) != 64:
            return False, "Signature lisensi tidak valid.", None

        public_key = serialization.load_pem_public_key(VIDEO_PUBLIC_KEY_PEM)
        try:
            public_key.verify(signature, payload_bytes)
        except InvalidSignature:
            return False, "Signature lisensi tidak cocok.", None

        payload = json.loads(payload_bytes.decode("utf-8"))
        if not isinstance(payload, dict):
            return False, "Data lisensi tidak valid.", None

        required = (
            "app_id", "license_id", "plan",
            "machine_id", "created_at", "expires_at"
        )
        for field in required:
            if field not in payload:
                return False, f"Field lisensi hilang: {field}", None

        if payload["app_id"] != VIDEO_APP_ID:
            return False, "Lisensi bukan untuk Video Editor Pro.", None

        if payload["machine_id"] != video_machine_id():
            return False, "Machine ID tidak cocok dengan perangkat ini.", None

        plan = payload["plan"]
        if plan not in VIDEO_VALID_PLANS:
            return False, "Paket lisensi tidak valid.", None

        created_at = video_parse_datetime(payload["created_at"])
        now = datetime.now(timezone.utc)
        if now < created_at:
            return False, "Waktu perangkat lebih awal dari tanggal lisensi.", None

        expires_raw = payload["expires_at"]
        if plan == "Lifetime":
            if expires_raw is not None:
                return False, "Lisensi Lifetime tidak boleh memiliki expired.", None
            expires_at = None
        else:
            if expires_raw is None:
                return False, "Tanggal expired tidak tersedia.", None
            expires_at = video_parse_datetime(expires_raw)
            if expires_at <= created_at:
                return False, "Rentang tanggal lisensi tidak valid.", None
            if now >= expires_at:
                return False, "Lisensi sudah kedaluwarsa.", None

        return True, "Lisensi valid.", {
            "payload": payload,
            "expires_at": expires_at,
        }
    except Exception as exc:
        return False, f"Lisensi tidak valid: {exc}", None
def ensure_video_license():
    VIDEO_LICENSE_DIR.mkdir(parents=True, exist_ok=True)
    machine_id = video_machine_id()

    saved_key = ""
    try:
        saved_key = VIDEO_LICENSE_FILE.read_text(encoding="utf-8").strip()
    except OSError:
        pass

    if saved_key:
        valid, message, info = verify_video_license_key(saved_key)
        if valid:
            global VIDEO_LICENSE_INFO
            VIDEO_LICENSE_INFO = info
            payload = info["payload"]
            expires = info["expires_at"]
            expires_text = expires.strftime("%Y-%m-%d %H:%M UTC") if expires else "Tidak terbatas"
            print(f"LICENSE : AKTIF | {payload['plan']}")
            print(f"EXPIRED : {expires_text}")
            return True
        print(f"[!] Lisensi tersimpan tidak aktif: {message}")

    print()
    print(CYAN + BOLD + "╔══════════════════════════════════════╗" + RESET)
    print(CYAN + BOLD + "║" + RESET + YELLOW + RESET + BOLD + "         AKTIVASI LICENSE             " + RESET + CYAN + BOLD + "║" + RESET)
    print(CYAN + BOLD + "╚══════════════════════════════════════╝" + RESET)
    print()
    print(CYAN + BOLD + "Produk   : " + RESET + RESET + "AFKAR VIDEO EDITOR PRO" + RESET)
    print(CYAN + BOLD + "Platform : " + RESET + RESET + "TERMUX EDITION" + RESET)
    print(CYAN + BOLD + "Status   : " + RESET + YELLOW + RESET + BOLD + "BELUM AKTIF" + RESET)
    print()
    print(RED + BOLD + "Machine ID perangkat ini:" + RESET)
    print(GREEN + BOLD + machine_id + RESET)
    print()
    print(CYAN + "Pilih produk " + RESET + BOLD + "AFKAR VIDEO EDITOR PRO" + RESET + CYAN + " di generator lisensi." + RESET)
    print(CYAN + "Kirim Machine ID untuk meminta License Key." + RESET)
    print(YELLOW + RESET + BOLD + "Hubungi : " + RESET + RESET + "rendiafkar.tools@gmail.com" + RESET)
    print(DIM + "Hubungi email tersebut untuk perpanjangan lisensi." + RESET)
    print()
    print(CYAN + BOLD + "Tempel License Key " + RESET + DIM + "(kosong = batal):" + RESET)

    while True:
        try:
            key = input("License Key > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAktivasi dibatalkan.")
            return False

        if key == "0" or not key:
            print("Aplikasi ditutup karena belum diaktifkan.")
            return False

        valid, message, info = verify_video_license_key(key)
        if not valid:
            print(f"[X] {message}")
            continue

        try:
            VIDEO_LICENSE_FILE.write_text(key, encoding="utf-8")
            try:
                VIDEO_LICENSE_FILE.chmod(0o600)
            except OSError:
                pass
        except OSError as exc:
            print(f"[X] Gagal menyimpan lisensi: {exc}")
            return False

        VIDEO_LICENSE_INFO = info
        print("[OK] Lisensi berhasil diverifikasi dan disimpan.")
        return True


def boot_sequence():
    clear()
    banner()

    name = load_user_name()
    if not name:
        name = introduce_user()

    show_welcome(name)

    if not ensure_video_license():
        return False

    print()
    spinner("SYSTEM")
    try:
        check_deps()
        spinner("FFMPEG / FFPROBE")
        print(f"{GREEN}[+] Semua dependensi siap.{RESET}")
    except RuntimeError as exc:
        print(f"{RED}[!] {exc}{RESET}")

    if EFFECTS:
        time.sleep(0.5)

    return True

def spinner(label):
    print(f"{CYAN}[*]{RESET} {label}", end="", flush=True)
    if EFFECTS:
        for _ in range(3):
            time.sleep(0.15)
            print(".", end="", flush=True)
    print(f" {GREEN}OK{RESET}")

def check_deps():
    missing = [x for x in ("ffmpeg", "ffprobe") if shutil.which(x) is None]
    if missing:
        raise RuntimeError("Program belum tersedia: " + ", ".join(missing) +
                           "\nInstall dengan: pkg install ffmpeg")

def ensure_dirs():
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def list_files(folder, exts=VIDEO_EXTS):
    files = sorted(p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in exts)
    return files

def choose_files(folder=None, exts=VIDEO_EXTS, label="Pilih video"):
    if folder is None:
        folder = INPUT_DIR

    files = list_files(folder, exts)
    if not files:
        raise RuntimeError(
            f"Tidak ada file yang cocok di folder:\n"
            f"{display_path(folder)}"
        )

    print(f"\n{CYAN}{BOLD}{label}{RESET} {DIM}—{RESET} {YELLOW}{display_path(folder)}{RESET}")
    for i, p in enumerate(files, 1):
        print(f" {GREEN}{i:2}.{RESET} {CYAN}{p.name}{RESET}")

    while True:
        raw = input(f"{YELLOW}Nomor video {DIM}(contoh 1-3,5 atau 1,3,5; 0 batal){RESET}: ").strip()
        if raw == "0":
            return None

        try:
            selected = set()
            for part in raw.split(","):
                part = part.strip()
                if "-" in part:
                    a, b = map(int, part.split("-", 1))
                    if a < 1 or b < a or b > len(files):
                        raise ValueError
                    selected.update(range(a, b + 1))
                else:
                    n = int(part)
                    if n < 1 or n > len(files):
                        raise ValueError
                    selected.add(n)

            if not selected:
                raise ValueError

            return [files[n - 1] for n in sorted(selected)]

        except (ValueError, TypeError):
            print(f"{RED}Format salah. Contoh: 1-3,5 atau 1,3,5.{RESET}")


def choose_file(folder=None, exts=VIDEO_EXTS, label="Pilih file"):
    if folder is None:
        folder = INPUT_DIR
    files = list_files(folder, exts)
    if not files:
        raise RuntimeError(f"Tidak ada file yang cocok di folder:\n{display_path(folder)}\nSalin file ke folder tersebut lalu coba lagi.")
    print(f"\n{CYAN}{BOLD}{label}{RESET} {DIM}—{RESET} {YELLOW}{display_path(folder)}{RESET}")
    for i, p in enumerate(files, 1):
        print(f" {GREEN}{i:2}.{RESET} {CYAN}{p.name}{RESET}")
    while True:
        raw = input(f"{YELLOW}Nomor file (0 batal){RESET}: ").strip()
        if raw == "0":
            return None
        if raw.isdigit() and 1 <= int(raw) <= len(files):
            return files[int(raw)-1]
        print(f"{RED}Pilihan tidak valid.{RESET}")

def ask_int(prompt, minimum, maximum=None):
    while True:
        raw = input(prompt).strip()
        try:
            val = int(raw)
            if val < minimum or (maximum is not None and val > maximum):
                raise ValueError
            return val
        except ValueError:
            print(f"{RED}Masukkan angka valid (minimum {minimum}" +
                  (f", maksimum {maximum}" if maximum is not None else "") + ")." + RESET)

def ask_float(prompt, minimum=None, maximum=None):
    while True:
        raw = input(prompt).strip()
        try:
            val = float(raw)
            if minimum is not None and val < minimum: raise ValueError
            if maximum is not None and val > maximum: raise ValueError
            return val
        except ValueError:
            print(f"{RED}Nilai tidak valid." + RESET)

def output_path(src, suffix, ext=None):
    ext = ext or src.suffix
    dest = OUTPUT_DIR / f"{src.stem}_{suffix}{ext}"
    n = 2
    while dest.exists():
        dest = OUTPUT_DIR / f"{src.stem}_{suffix}_{n}{ext}"
        n += 1
    return dest

def duration_seconds(src):
    result = run_cmd(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                      "-of", "default=noprint_wrappers=1:nokey=1", src], capture=True)
    try:
        return float(result.stdout.strip())
    except (ValueError, AttributeError):
        raise RuntimeError("Durasi video tidak dapat dibaca.")

def probe(src):
    result = run_cmd(["ffprobe", "-v", "error", "-show_entries",
                      "format=duration,size:stream=codec_type,width,height",
                      "-of", "default=noprint_wrappers=1", src], capture=True)
    print(result.stdout.strip() or "Informasi file tidak tersedia.")

def run_ffmpeg(args, output):
    import subprocess
    import sys
    import tempfile

    output = str(output)
    args = [str(x) for x in args]

    # Cari durasi sumber untuk menghitung persentase progres.
    duration = 0.0
    try:
        idx = args.index("-i")
        source = args[idx + 1]
        probe = subprocess.run(
            ["ffprobe", "-v", "error",
             "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", source],
            capture_output=True, text=True, timeout=15
        )
        if probe.returncode == 0:
            duration = float(probe.stdout.strip() or 0)
    except (ValueError, IndexError, OSError, subprocess.SubprocessError):
        pass

    # Jika proses hanya menghasilkan potongan video, gunakan durasi potongan.
    try:
        t_index = args.index("-t")
        duration = float(args[t_index + 1])
    except (ValueError, IndexError):
        pass

    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error",
        "-nostats", "-progress", "pipe:1", "-y",
        *args, output
    ]

    print(f"\n{CYAN}[*] Memproses video...{RESET}")
    bar_width = 24
    last_percent = -1

    with tempfile.TemporaryFile(mode="w+t") as errfile:
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=errfile,
            text=True, bufsize=1
        )

        try:
            for line in proc.stdout:
                line = line.strip()
                if line.startswith("out_time_us="):
                    try:
                        elapsed = int(line.split("=", 1)[1]) / 1_000_000
                        if duration > 0:
                            percent = max(0, min(99, int(elapsed / duration * 100)))
                            if percent != last_percent:
                                filled = int(bar_width * percent / 100)
                                bar = "█" * filled + "░" * (bar_width - filled)
                                sys.stdout.write(
                                    f"\r\033[92m[{bar}]\033[0m {percent:3d}%\033[K"
                                )
                                sys.stdout.flush()
                                last_percent = percent
                    except ValueError:
                        pass
                elif line.startswith("out_time_ms=") and duration <= 0:
                    sys.stdout.write("\r\033[92m[*] FFmpeg sedang memproses...\033[0m\033[K")
                    sys.stdout.flush()

            proc.stdout.close()
            code = proc.wait()
        except KeyboardInterrupt:
            proc.terminate()
            proc.wait()
            print("\n[!] Proses dihentikan.")
            raise RuntimeError("Proses FFmpeg dihentikan pengguna.")

        if code != 0:
            errfile.seek(0)
            error = errfile.read().strip()
            raise RuntimeError(error or f"FFmpeg gagal dengan kode {code}.")

    if duration > 0:
        filled = bar_width
        sys.stdout.write(f"\r[{'#' * filled}] 100%\n")
        sys.stdout.flush()
    else:
        print()

    result = Path(output)
    if not result.exists() or result.stat().st_size == 0:
        raise RuntimeError("File output tidak terbentuk atau kosong.")

    print(f"{GREEN}[OK] Selesai:{RESET} {CYAN}{result}{RESET}")
    print(f"{GREEN}[OK] Ukuran:{RESET} {YELLOW}{result.stat().st_size / (1024*1024):.2f} MB{RESET}")


def split_video():
    set_feature_dirs("split-video")
    src = choose_file()
    if src is None: return
    dur = duration_seconds(src)
    print(f"Durasi: {dur:.2f} detik")
    print("1. Potong berdasarkan durasi per bagian\n2. Bagi menjadi jumlah bagian")
    mode = ask_int("Pilih mode: ", 1, 2)
    if mode == 1:
        part_len = ask_float("Durasi tiap bagian (detik): ", 0.1)
        count = int((dur + part_len - 0.000001) // part_len)
        if dur % part_len > 0.000001: count += 1
    else:
        count = ask_int("Jumlah bagian: ", 2, 1000)
        part_len = dur / count
    if count > 1000:
        raise RuntimeError("Jumlah bagian terlalu banyak (maksimum 1000).")
    print("Mode cepat (-c copy) tanpa re-encode. Potongan bisa sedikit meleset mengikuti keyframe.")
    for i in range(count):
        start = i * part_len
        length = min(part_len, dur - start)
        if length <= 0: continue
        dest = output_path(src, f"part{i+1:03d}")
        run_ffmpeg(["-ss", f"{start:.3f}", "-i", src, "-t", f"{length:.3f}",
                    "-map", "0", "-c", "copy", "-avoid_negative_ts", "make_zero"], dest)
    print(f"{GREEN}[OK]{RESET} Split selesai. Hasil ada di {display_path(OUTPUT_DIR)}")

def flip_video():
    set_feature_dirs("flip-video")
    files = choose_files(label="Pilih video untuk Flip")
    if not files:
        return

    print(f"{GREEN}1.{RESET} {CYAN}Flip horizontal{RESET}")
    print(f"{GREEN}2.{RESET} {CYAN}Flip vertical{RESET}")
    mode = ask_int("Pilih: ", 1, 2)
    filt = "hflip" if mode == 1 else "vflip"
    suffix = "flip_h" if mode == 1 else "flip_v"

    for i, src in enumerate(files, 1):
        print(f"\n{GREEN}[{i}/{len(files)}]{RESET} {CYAN}{src.name}{RESET}")
        dest = output_path(src, suffix)
        try:
            run_ffmpeg([
                "-i", str(src), "-vf", filt,
                "-c:v", "libx264", "-preset", "veryfast",
                "-crf", "20", "-c:a", "copy"
            ], dest)
        except (RuntimeError, OSError, ValueError) as exc:
            print(f"{RED}[GAGAL]{RESET} {CYAN}{src.name}{RESET}: {YELLOW}{exc}{RESET}")


def rotate_video():
    set_feature_dirs("rotate-video")
    files = choose_files(label="Pilih video untuk Rotate")
    if not files:
        return

    print(f"{GREEN}1.{RESET} {CYAN}90 derajat searah jarum jam{RESET}")
    print(f"{GREEN}2.{RESET} {CYAN}90 derajat berlawanan jarum jam{RESET}")
    print(f"{GREEN}3.{RESET} {CYAN}180 derajat{RESET}")
    mode = ask_int("Pilih: ", 1, 3)
    filt = {1: "transpose=1", 2: "transpose=2", 3: "hflip,vflip"}[mode]

    for i, src in enumerate(files, 1):
        print(f"\n{GREEN}[{i}/{len(files)}]{RESET} {CYAN}{src.name}{RESET}")
        dest = output_path(src, f"rotate{mode}")
        try:
            run_ffmpeg([
                "-i", str(src), "-vf", filt,
                "-metadata:s:v:0", "rotate=0",
                "-c:v", "libx264", "-preset", "veryfast",
                "-crf", "20", "-c:a", "copy"
            ], dest)
        except (RuntimeError, OSError, ValueError) as exc:
            print(f"{RED}[GAGAL]{RESET} {CYAN}{src.name}{RESET}: {YELLOW}{exc}{RESET}")


def crop_video():
    set_feature_dirs("crop-resize")
    src = choose_file()
    if src is None: return
    print("1. 9:16 portrait\n2. 16:9 landscape\n3. 1:1 square\n4. Custom crop")
    mode = ask_int("Pilih rasio: ", 1, 4)
    if mode == 1: filt = "crop='min(iw,ih*9/16)':'min(ih,iw*16/9)',scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2"
    elif mode == 2: filt = "crop='min(iw,ih*16/9)':'min(ih,iw*9/16)',scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2"
    elif mode == 3: filt = "crop='min(iw,ih)':'min(iw,ih)',scale=720:720"
    else:
        x = ask_int("X mulai (pixel): ", 0)
        y = ask_int("Y mulai (pixel): ", 0)
        w = ask_int("Lebar crop (pixel): ", 2)
        h = ask_int("Tinggi crop (pixel): ", 2)
        filt = f"crop={w}:{h}:{x}:{y}"
    dest = output_path(src, "crop")
    run_ffmpeg(["-i", src, "-vf", filt, "-c:v", "libx264", "-preset", "veryfast",
                "-crf", "20", "-c:a", "copy"], dest)

def speed_video():
    set_feature_dirs("change-speed")
    src = choose_file()
    if src is None: return
    speed = ask_float("Kecepatan (0.25 sampai 4.0, contoh 2 = 2x): ", 0.25, 4.0)
    pts = 1.0 / speed
    filters = f"setpts={pts:.6f}*PTS"
    args = ["-i", src, "-vf", filters, "-c:v", "libx264", "-preset", "veryfast", "-crf", "20"]
    # atempo supports 0.5..2.0 per filter; chain for full supported speed range
    remaining = speed
    atempo = []
    while remaining > 2.0:
        atempo.append("atempo=2.0")
        remaining /= 2.0
    while remaining < 0.5:
        atempo.append("atempo=0.5")
        remaining /= 0.5
    atempo.append(f"atempo={remaining:.6f}")
    args += ["-af", ",".join(atempo), "-c:a", "aac", "-b:a", "192k"]
    dest = output_path(src, f"speed{str(speed).replace('.', '_')}x")
    run_ffmpeg(args, dest)

def reverse_video():
    set_feature_dirs("reverse-video")
    src = choose_file()
    if src is None: return
    print(f"{YELLOW}Reverse dapat memakai RAM/penyimpanan lebih besar untuk video panjang.{RESET}")
    if input(f"{YELLOW}Lanjutkan? (y/n): {RESET}").strip().lower() not in ("y", "ya"): return
    dest = output_path(src, "reverse")
    run_ffmpeg(["-i", src, "-vf", "reverse", "-af", "areverse", "-c:v", "libx264",
                "-preset", "veryfast", "-crf", "22", "-c:a", "aac", "-b:a", "160k"], dest)

def merge_video():
    set_feature_dirs("merge-videos")
    files = list_files(INPUT_DIR)
    if len(files) < 2:
        raise RuntimeError(f"Perlu minimal 2 video di {display_path(INPUT_DIR)}")
    print(f"{CYAN}Video yang ditemukan di {display_path(INPUT_DIR)}:{RESET}")
    for i, p in enumerate(files, 1): print(f" {GREEN}{i}.{RESET} {CYAN}{p.name}{RESET}")
    raw = input("Nomor video urut gabung (contoh 1,2,3): ").strip()
    try:
        nums = [int(x.strip()) for x in raw.split(",")]
        if len(nums) < 2 or len(set(nums)) != len(nums) or any(n < 1 or n > len(files) for n in nums):
            raise ValueError
    except ValueError:
        raise RuntimeError("Daftar nomor tidak valid.")
    selected = [files[n-1] for n in nums]
    # Normalize codec, dimensions and audio layout so heterogeneous clips can merge.
    dest = output_path(selected[0], "merged", ".mp4")
    list_file = OUTPUT_DIR / "merge_list_temp.txt"
    temp_files = []
    try:
        normalized = []
        for i, src in enumerate(selected, 1):
            tmp = OUTPUT_DIR / f".afkar_merge_{os.getpid()}_{i}.mp4"
            temp_files.append(tmp)
            run_cmd(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", src,
                     "-vf", "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,setsar=1",
                     "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
                     "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-ac", "2",
                     "-movflags", "+faststart", tmp])
            normalized.append(tmp)
        with list_file.open("w", encoding="utf-8") as f:
            for item in normalized:
                f.write("file '" + str(item).replace("'", r"'\''") + "'\n")
        run_ffmpeg(["-f", "concat", "-safe", "0", "-i", list_file, "-c", "copy",
                    "-movflags", "+faststart"], dest)
    finally:
        if list_file.exists(): list_file.unlink()
        for tmp in temp_files:
            if tmp.exists(): tmp.unlink()

def extract_audio():
    set_feature_dirs("extract-audio")
    src = choose_file()
    if src is None: return
    dest = output_path(src, "audio", ".mp3")
    run_ffmpeg(["-i", src, "-vn", "-c:a", "libmp3lame", "-q:a", "2"], dest)

def color_video():
    set_feature_dirs("color-adjustment")
    src = choose_file()
    if src is None: return
    brightness = ask_float("Brightness (-1.0 sampai 1.0, 0 normal): ", -1.0, 1.0)
    contrast = ask_float("Contrast (0.0 sampai 3.0, 1 normal): ", 0.0, 3.0)
    saturation = ask_float("Saturation (0.0 sampai 3.0, 1 normal): ", 0.0, 3.0)
    filt = f"eq=brightness={brightness}:contrast={contrast}:saturation={saturation}"
    dest = output_path(src, "color")
    run_ffmpeg(["-i", src, "-vf", filt, "-c:v", "libx264", "-preset", "veryfast",
                "-crf", "20", "-c:a", "copy"], dest)

def compress_video():
    set_feature_dirs("compress-video")
    src = choose_file()
    if src is None: return
    print("Preset kualitas:\n1. High quality (CRF 20)\n2. Balanced (CRF 25)\n3. Smaller file (CRF 29)")
    mode = ask_int("Pilih preset: ", 1, 3)
    crf = {1: "20", 2: "25", 3: "29"}[mode]
    print("Resolusi:\n1. Original\n2. 1080p maksimum\n3. 720p maksimum\n4. 480p maksimum")
    resmode = ask_int("Pilih resolusi: ", 1, 4)
    vf = []
    if resmode > 1:
        h = {2: 1080, 3: 720, 4: 480}[resmode]
        vf = ["-vf", f"scale=-2:'min({h},ih)'"]
    dest = output_path(src, "compressed")
    run_ffmpeg(["-i", src, *vf, "-c:v", "libx264", "-preset", "veryfast", "-crf", crf,
                "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart"], dest)

def show_files():
    print(f"\nINPUT : {display_path(INPUT_DIR)}")
    files = list_files(INPUT_DIR)
    if files:
        for p in files: print(f" - {p.name} ({p.stat().st_size/(1024*1024):.2f} MB)")
    else: print(f" {DIM}(kosong){RESET}")
    print(f"\nOUTPUT: {display_path(OUTPUT_DIR)}")
    outputs = sorted(p for p in OUTPUT_DIR.iterdir() if p.is_file() and not p.name.startswith("."))
    if outputs:
        for p in outputs: print(f" - {p.name} ({p.stat().st_size/(1024*1024):.2f} MB)")
    else: print(f" {DIM}(kosong){RESET}")




def auto_batch_edit():
    """Batch edit dengan folder input dan output khusus."""
    ensure_dirs()

    batch_input = INPUT_ROOT / "auto-edit-batch"
    batch_output = OUTPUT_ROOT / "auto-edit-batch"
    batch_input.mkdir(parents=True, exist_ok=True)
    batch_output.mkdir(parents=True, exist_ok=True)
    batch_input.mkdir(parents=True, exist_ok=True)
    batch_output.mkdir(parents=True, exist_ok=True)

    videos = sorted(
        (f for f in batch_input.rglob("*")
         if f.is_file() and f.suffix.lower() in VIDEO_EXTS),
        key=lambda f: str(f).lower()
    )

    print(f"\n{CYAN}{BOLD}[AUTO EDIT VIDEO BATCH]{RESET}")
    print(f"INPUT : {display_path(batch_input)}")
    print(f"OUTPUT: {display_path(batch_output)}")

    if not videos:
        print(f"\n{YELLOW}[!] Folder input batch belum berisi video.{RESET}")
        print("Salin video ke folder input/auto-edit-batch lalu pilih menu 14 lagi.")
        return

    for i, video in enumerate(videos, 1):
        print(f" {GREEN}{i:2}.{RESET} {video.relative_to(batch_input)}")

    raw = input(
        f"{YELLOW}Nomor video (1-3,5 atau all; 0 batal): {RESET}"
    ).strip().lower()

    if raw == "0" or not raw:
        return

    if raw == "all":
        selected = videos
    else:
        chosen = set()
        try:
            for part in raw.split(","):
                part = part.strip()
                if "-" in part:
                    a, b = map(int, part.split("-", 1))
                    if a < 1 or b < a or b > len(videos):
                        raise ValueError
                    chosen.update(range(a, b + 1))
                else:
                    n = int(part)
                    if n < 1 or n > len(videos):
                        raise ValueError
                    chosen.add(n)
            selected = [videos[n - 1] for n in sorted(chosen)]
        except ValueError:
            print(f"{RED}[!] Format nomor tidak valid.{RESET}")
            return

    print(f"\n{BOLD}{CYAN}FORMAT OUTPUT{RESET}")
    print(f"{GREEN}1.{RESET} {BOLD}TikTok / Shorts (1080x1920){RESET}")
    print(f"{GREEN}2.{RESET} {BOLD}Landscape (1920x1080){RESET}")
    print(f"{GREEN}3.{RESET} {BOLD}Square (1080x1080){RESET}")
    print(f"{GREEN}4.{RESET} {BOLD}Custom{RESET}")
    mode = ask_int(f"{YELLOW}Pilih format [1-4]: {RESET}", 1, 4)

    if mode == 1:
        width, height = 1080, 1920
    elif mode == 2:
        width, height = 1920, 1080
    elif mode == 3:
        width, height = 1080, 1080
    else:
        width = ask_int(f"{YELLOW}Lebar [240-3840]: {RESET}", 240, 3840)
        height = ask_int(f"{YELLOW}Tinggi [240-3840]: {RESET}", 240, 3840)
        width -= width % 2
        height -= height % 2

    fps = ask_int(f"{YELLOW}FPS [24-60]: {RESET}", 24, 60)
    zoom_choice = ask_int(f"{YELLOW}Zoom [1=Normal, 2=5%, 3=10%]: {RESET}", 1, 3)
    zoom = {1: 1.0, 2: 1.05, 3: 1.10}[zoom_choice]

    print(f"{BOLD}{CYAN}Warna{RESET} {YELLOW}[1=Asli, 2=Cerah, 3=Kontras lembut]{RESET}")
    color_choice = ask_int(f"{YELLOW}Pilih warna [1-3]: {RESET}", 1, 3)
    color_filter = {
        1: "",
        2: "eq=brightness=0.04:saturation=1.12",
        3: "eq=contrast=1.04:saturation=0.92:brightness=0.01",
    }[color_choice]

    print(f"{BOLD}{CYAN}Flip{RESET} {YELLOW}[1=Normal, 2=Horizontal, 3=Vertikal]{RESET}")
    flip = ask_int(f"{YELLOW}Pilih flip [1-3]: {RESET}", 1, 3)
    overlay = input(f"{YELLOW}Teks overlay (kosong = tanpa teks): {RESET}").strip()[:120]

    try:
        duration_limit = float(
            input(f"{YELLOW}Durasi maksimal detik (0 = asli): {RESET}").strip() or "0"
        )
        if duration_limit < 0:
            raise ValueError
    except ValueError:
        print(f"{RED}[!] Durasi tidak valid.{RESET}")
        return

    success = 0
    failed = 0
    for index, source in enumerate(selected, 1):
        destination = batch_output / f"{source.stem}_AUTO_EDIT.mp4"
        suffix = 2
        while destination.exists():
            destination = batch_output / f"{source.stem}_AUTO_EDIT_{suffix}.mp4"
            suffix += 1

        filters = [
            f"scale={width}:{height}:force_original_aspect_ratio=increase",
            f"crop={width}:{height}",
        ]
        zw, zh = int(width * zoom), int(height * zoom)
        zw += zw % 2
        zh += zh % 2
        filters.extend([f"scale={zw}:{zh}", f"crop={width}:{height}", f"fps={fps}"])

        if flip == 2:
            filters.append("hflip")
        elif flip == 3:
            filters.append("vflip")
        if color_filter:
            filters.append(color_filter)

        overlay_file = None
        try:
            if overlay:
                logs = ROOT / "logs"
                logs.mkdir(parents=True, exist_ok=True)
                overlay_file = logs / "_afkar_batch_overlay.txt"
                overlay_file.write_text(overlay.replace("\x00", ""), encoding="utf-8")
                safe = str(overlay_file).replace("\\", "\\\\").replace(":", "\\:")
                filters.append(
                    f"drawtext=textfile='{safe}':expansion=none:"
                    "fontcolor=white:fontsize=48:"
                    "x=(w-text_w)/2:y=h*0.80:"
                    "box=1:boxcolor=black@0.55:boxborderw=18"
                )

            cmd = [
                "-i", str(source),
                "-map", "0:v:0", "-map", "0:a?",
                "-vf", ",".join(filters),
                "-c:v", "libx264", "-preset", "veryfast",
                "-crf", "23", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "128k",
                "-movflags", "+faststart",
            ]
            if duration_limit > 0:
                cmd.extend(["-t", str(duration_limit)])

            print(f"\n{CYAN}[{index}/{len(selected)}] {source.name}{RESET}")
            run_ffmpeg(cmd, destination)

            if not destination.is_file() or destination.stat().st_size == 0:
                raise RuntimeError("Output kosong atau tidak ditemukan.")
            success += 1
            print(f"{GREEN}[OK] {destination.name}{RESET}")
        except (RuntimeError, OSError, ValueError) as exc:
            failed += 1
            print(f"{RED}[GAGAL] {source.name}: {exc}{RESET}")
            try:
                if destination.exists() and destination.stat().st_size == 0:
                    destination.unlink()
            except OSError:
                pass
        finally:
            if overlay_file:
                overlay_file.unlink(missing_ok=True)

    print(f"\n{BOLD}===== RINGKASAN BATCH EDIT ====={RESET}")
    print(f"{GREEN}Berhasil: {success}{RESET}")
    print(f"{RED}Gagal: {failed}{RESET}")
    print(f"Output: {display_path(batch_output)}")

def main():
    ensure_dirs()

    while True:
        reset_root_dirs()
        if not boot_sequence():
            return
        print()
        print(f"\n{DIM}INPUT : {display_path(INPUT_DIR)}{RESET}")
        print(f"{DIM}OUTPUT: {display_path(OUTPUT_DIR)}{RESET}\n")
        menu = [
            ("1", "SPLIT VIDEO"),
            ("2", "FLIP HORIZONTAL / VERTICAL"),
            ("3", "ROTATE VIDEO"),
            ("4", "CROP & RESIZE"),
            ("5", "CHANGE SPEED"),
            ("6", "REVERSE VIDEO"),
            ("7", "MERGE VIDEOS"),
            ("8", "EXTRACT AUDIO / MP3"),
            ("9", "COLOR ADJUSTMENT"),
            ("10", "COMPRESS VIDEO"),
            ("11", "LIHAT FILE INPUT / OUTPUT"),
            ("12", "CEK FFMPEG"),
            ("13", "GANTI NAMA PENGGUNA"),
            ("14", "AUTO EDIT VIDEO BATCH"),
            ("0", "EXIT"),
        ]
        for n, title in menu:
            print(f" {CYAN}[{n:>2}]{RESET} {BOLD}{title}{RESET}")
        choice = input(
            f"\n{GREEN}{load_user_name() or DEFAULT_USER} > {RESET}"
        ).strip().lower()
        actions = {
            "1": split_video, "2": flip_video, "3": rotate_video,
            "4": crop_video, "5": speed_video, "6": reverse_video,
            "7": merge_video, "8": extract_audio, "9": color_video,
            "10": compress_video, "11": show_files, "12": check_deps,
            "13": change_user_name,
            "14": auto_batch_edit,
        }
        if choice in ("0", "q", "exit", "keluar"):
            print(f"\n{GREEN}[+] Sesi ditutup. BY AFKAR.{RESET}")
            return
        action = actions.get(choice)
        if not action:
            print(f"{RED}[!] Pilihan tidak valid.{RESET}")
            pause()
            continue
        try:
            action()
        except KeyboardInterrupt:
            print(f"\n{YELLOW}[!] Proses dibatalkan pengguna.{RESET}")
        except (RuntimeError, OSError, ValueError) as exc:
            print(f"\n{RED}[ERROR]{RESET} {exc}")
        except Exception as exc:
            print(f"\n{RED}[ERROR]{RESET} Kesalahan tidak terduga: {exc}")
        pause()

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nDibatalkan.")
