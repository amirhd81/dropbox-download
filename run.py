import yt_dlp
import subprocess
import os
import argparse

# -------- SETTINGS --------
SPLIT_SIZE = "90m"
WORK_DIR = "video_job"
# --------------------------


def list_formats(url, extra_ytdlp_opts):
    print("🔎 Fetching available formats...\n")

    opts = {
        "skip_download": True,
        "quiet": False
    }

    opts.update(extra_ytdlp_opts)

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)

    formats = info.get("formats", [])

    print("\nID   EXT   RESOLUTION   FPS   VCODEC        ACODEC")
    print("-"*55)

    for f in formats:
        fid = f.get("format_id")
        ext = f.get("ext")
        height = f.get("height")
        width = f.get("width")
        res = f"{width}x{height}" if width and height else "audio"
        fps = f.get("fps") or "-"

        print(f"{fid:4} {ext:5} {res:11} {fps:4}")

def run(cmd):
    subprocess.run(cmd, shell=True, check=True)


def parse_ytdlp_opts(opt_list):
    """
    --ytdlp-opt key=value   -> {"key": "value"}
    --ytdlp-opt flag        -> {"flag": True}
    """
    opts = {}

    if not opt_list:
        return opts

    for item in opt_list:
        if "=" in item:
            key, value = item.split("=", 1)
            opts[key.strip()] = value.strip()
        else:
            opts[item.strip()] = True

    return opts


def download_video(url, extra_ytdlp_opts):
    print("🚀 Downloading video (480p + audio)...")

    if "dropbox.com" in url and "?dl=0" in url:
        url = url.replace("?dl=0", "?dl=1")

    opts = {
        "format": "bestvideo[height=480]+bestaudio/best[height=480]",
        "merge_output_format": "mp4",
        "outtmpl": "video.%(ext)s",

        # SPEED BOOST
        "external_downloader": "aria2c",
        "external_downloader_args": [
            "-x", "16",
            "-k", "1M"
        ],

        "quiet": False
    }

    # ✅ Merge user-provided yt-dlp options (override defaults)
    opts.update(extra_ytdlp_opts)

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)

    print(f"✅ Downloaded: {filename}")
    return filename


def split_rar(file):
    print("📦 Splitting into 90MB parts...")

    base = os.path.basename(file)
    archive_name = "video_archive"

    run(f"rar a -v{SPLIT_SIZE} -m0 {archive_name}.rar '{base}'")

    parts = [f for f in os.listdir() if f.startswith("video_archive")]
    run(f"rm -rf {base}")
    return parts


def git_push(files):
    print("📤 Uploading to GitHub...")

    # Reduce memory usage for VPS
    run("git config pack.windowMemory 10m")
    run("git config pack.packSizeLimit 20m")
    run("git config pack.threads 1")

    for f in files:
        run(f"git add '{f}'")

    run('git commit -m "upload video parts"')


def main(dropbox_url, ytdlp_opt_list):
    os.makedirs(WORK_DIR, exist_ok=True)
    os.chdir(WORK_DIR)

    extra_ytdlp_opts = parse_ytdlp_opts(ytdlp_opt_list)

    video_file = download_video(dropbox_url, extra_ytdlp_opts)
    rar_parts = split_rar(video_file)
    git_push(rar_parts)

    print("✅ Done")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download video, split into parts, and upload to GitHub"
    )
    parser.add_argument(
        "url",
        help="The URL of the video to download (e.g., Dropbox or YouTube link)"
    )

    parser.add_argument(
        "--list-formats",
        action="store_true",
        help="List available formats and exit"
    )
    
    parser.add_argument(
        "--ytdlp-opt",
        action="append",
        help="Extra yt-dlp option (key=value or flag). Can be used multiple times."
    )

    args = parser.parse_args()

    extra_opts = parse_ytdlp_opts(args.ytdlp_opt or [])

    if args.list_formats:
        list_formats(args.url, extra_opts)
    else:
        main(args.url, args.ytdlp_opt or []) 

