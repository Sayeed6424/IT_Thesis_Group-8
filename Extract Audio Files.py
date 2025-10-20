# Extract Audio Files (denoise for nature/birds)
# Uses high/low-pass, 50/100 Hz hum notch (equalizer), and afftdn if available.
# Quiet ffmpeg logs + hard-coded paths.

import subprocess
import shutil
from pathlib import Path

# ========= EDIT THESE (paths) =========
INPUT_PATH = r"C:\Users\tshib\OneDrive\Desktop\IT Thesis\Video Directory"   # folder OR single video file
OUT_DIR    = r"C:\Users\tshib\OneDrive\Desktop\IT Thesis\Audio Output Directory"
# Point directly to ffmpeg.exe (adjust if different)
FFMPEG_BIN = r"C:\Users\tshib\AppData\Local\Microsoft\WinGet\Links\ffmpeg.exe"
# =====================================

# Output/processing settings
FORMAT       = "wav"     # 'wav', 'mp3', or 'flac'
SAMPLE_RATE  = None      # None => 48000 for wav, 44100 for mp3/flac
CHANNELS     = 1         # 1=mono, 2=stereo
BITRATE      = "192k"    # for mp3 only
RECURSIVE    = True
QUIET        = True      # hide ffmpeg banners/verbosity
PAUSE_ON_EXIT = True

# Noise-reduction defaults
BIRD_LO_HZ   = 400       # 300–500 typical
BIRD_HI_HZ   = 7000      # 6–8 kHz
HUM_HZ       = 50        # 60 in some regions

VIDEO_EXTS = {
    ".mp4",".mov",".mkv",".avi",".m4v",".webm",".wmv",".flv",".mts",".m2ts",".3gp",".mpeg",".mpg",".ts"
}

def ffbin() -> str:
    if FFMPEG_BIN:
        p = Path(FFMPEG_BIN)
        if not p.exists() or p.is_dir():
            raise RuntimeError(f"FFmpeg not found or not an .exe: {p}")
        return str(p)
    path = shutil.which("ffmpeg")
    if path is None:
        raise RuntimeError("FFmpeg not found. Install it or set FFMPEG_BIN.")
    return path

def ff_has_filter(name: str) -> bool:
    try:
        out = subprocess.run([ffbin(), "-hide_banner", "-filters"],
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        return name in out.stdout
    except Exception:
        return False

def collect_videos(p: Path, recursive: bool):
    if p.is_file() and p.suffix.lower() in VIDEO_EXTS:
        return [p]
    if not p.is_dir():
        return []
    it = p.rglob("*") if recursive else p.glob("*")
    return [x for x in it if x.is_file() and x.suffix.lower() in VIDEO_EXTS]

def build_filter_chain() -> str:
    chain = []
    # Band-pass
    chain.append(f"highpass=f={BIRD_LO_HZ}")
    chain.append(f"lowpass=f={BIRD_HI_HZ}")
    # Hum notch (use 'equalizer', not 'anequalizer')
    if HUM_HZ and ff_has_filter("equalizer"):
        chain.append(f"equalizer=f={HUM_HZ}:t=q:w=1.0:g=-25")
        chain.append(f"equalizer=f={2*HUM_HZ}:t=q:w=1.0:g=-18")
    # Denoise (afftdn if present)
    if ff_has_filter("afftdn"):
        chain.append("afftdn=nr=12")
    return ",".join(chain)

def build_ffmpeg_cmd(in_path: Path, out_path: Path, fmt: str, sr: int, ch: int, br: str | None):
    af = build_filter_chain()
    cmd = [ffbin()]
    if QUIET:
        cmd += ["-hide_banner", "-nostats", "-loglevel", "error"]
    cmd += ["-y", "-i", str(in_path), "-vn", "-af", af]
    if fmt == "wav":
        cmd += ["-acodec", "pcm_s16le", "-ar", str(sr), "-ac", str(ch), str(out_path)]
    elif fmt == "mp3":
        if br is None:
            br = "192k"
        cmd += ["-acodec", "libmp3lame", "-b:a", br, "-ar", str(sr), "-ac", str(ch), str(out_path)]
    elif fmt == "flac":
        cmd += ["-acodec", "flac", "-ar", str(sr), "-ac", str(ch), str(out_path)]
    else:
        raise ValueError("Unsupported format.")
    return cmd

def extract_one(in_path: Path, out_dir: Path, fmt: str, sr: int | None, ch: int, br: str | None):
    out_dir.mkdir(parents=True, exist_ok=True)
    if sr is None:
        sr = 48000 if fmt == "wav" else 44100
    out_path = out_dir / (in_path.stem + f".{fmt}")

    cmd = build_ffmpeg_cmd(in_path, out_path, fmt, sr, ch, br)
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print("[FAIL]", in_path)
        print("[FFMPEG CMD]", " ".join(cmd))
        print(result.stderr.strip())
        # no-audio case
        if "matches no streams" in result.stderr or "does not contain any stream" in result.stderr:
            print(f"[SKIP] {in_path} — no audio stream.")
            return False
        return False

    print(f"[OK]   {in_path} -> {out_path}")
    return True

def main():
    in_path = Path(INPUT_PATH).expanduser().resolve()
    out_dir = Path(OUT_DIR).expanduser().resolve()

    try:
        used_ff = ffbin()
        print(f"Using ffmpeg: {used_ff}")
    except Exception as e:
        print(e)
        if PAUSE_ON_EXIT: input("\nPress Enter to exit...")
        return

    vids = collect_videos(in_path, RECURSIVE)
    if not vids:
        print("No video files found. Supported:", ", ".join(sorted(VIDEO_EXTS)))
        if PAUSE_ON_EXIT: input("\nPress Enter to exit...")
        return

    print(f"Found {len(vids)} file(s). Output -> {out_dir}")
    ok = 0
    for i, v in enumerate(vids, 1):
        print(f"({i}/{len(vids)}) {v}")
        ok += extract_one(v, out_dir, FORMAT, SAMPLE_RATE, CHANNELS, BITRATE) or 0
    print(f"\nDone. {ok}/{len(vids)} files extracted.")

    if PAUSE_ON_EXIT:
        input("\nAll done. Press Enter to close...")

if __name__ == "__main__":
    main()
