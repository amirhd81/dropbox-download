import re
import requests
from typing import Optional
import json

def int_or_none(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def float_or_none(value, scale=1):
    try:
        return float(value) / scale
    except (TypeError, ValueError):
        return None


def proto_relative_url(url: Optional[str]) -> Optional[str]:
    if not url:
        return None
    if url.startswith("//"):
        return "https:" + url
    return url


def extract_streamable_id(url_or_id: str) -> str:
    """
    Accepts:
      - https://streamable.com/abcd12
      - https://www.streamable.com/abcd12
      - abcd12
    """
    m = re.search(r"streamable\.com/([a-zA-Z0-9]+)", url_or_id)
    return m.group(1) if m else url_or_id



def extract_streamable(url_or_id: str) -> dict:
    video_id = extract_streamable_id(url_or_id)

    password = "gvc277"

    payload = {}
    if password:
        payload["password"] = password


    api_url = f"https://api-f.streamable.com/api/v1/videos/{video_id}/password"
    resp = requests.post(api_url, json=payload)
    resp.raise_for_status

    
    video = resp.json()

    print(json.dumps(video, indent=4, sort_keys=True))

    # Status meanings:
    # 0 uploading, 1 processing, 2 ready, 3 error
    status = video.get("status")
    if status != 2:
        raise RuntimeError(
            "This video is unavailable (still uploading, processing, or errored)"
        )

    title = video.get("reddit_title") or video.get("title")

    formats = []
    for fmt_id, info in (video.get("files") or {}).items():
        url = info.get("url")
        if not url:
            continue

        input_meta = info.get("input_metadata") or {}

        formats.append({
            "format_id": fmt_id,
            "url": proto_relative_url(url),
            "width": int_or_none(info.get("width")),
            "height": int_or_none(info.get("height")),
            "filesize": int_or_none(info.get("size")),
            "fps": int_or_none(info.get("framerate")),
            "vbr": float_or_none(info.get("bitrate"), 1000),
            "vcodec": input_meta.get("video_codec_name"),
            "acodec": input_meta.get("audio_codec_name"),
        })

    return {
        "id": video_id,
        "title": title,
        "description": video.get("description"),
        "thumbnail": proto_relative_url(video.get("thumbnail_url")),
        "uploader": (video.get("owner") or {}).get("user_name"),
        "timestamp": float_or_none(video.get("date_added")),
        "duration": float_or_none(video.get("duration")),
        "view_count": int_or_none(video.get("plays")),
        "formats": formats,
    }


if __name__ == "__main__":
    url = input("Streamable URL or ID: ").strip()
    info = extract_streamable(url)

    print(f"\nTitle: {info['title']}")
    print(f"Duration: {info['duration']} seconds")
    print(f"Views: {info['view_count']}")
    print("\nAvailable formats:")
    for f in info["formats"]:
        print(
            f"  - {f['format_id']}: "
            f"{f['width']}x{f['height']} | "
            f"{f['fps']}fps | "
            f"{f['url']}"
        )
