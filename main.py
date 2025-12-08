import os
import subprocess
import time

from pyrogram import Client, utils
from pyrogram.errors import FloodWait

from config import API_ID, API_HASH, BOT_TOKEN, DB_PATH, VIDEOS_DIR, CHAT_IDS, PROXY
from db_management import Database
from thumbnail_utils import thumbnail_creator

app = Client(
    "video_uploader", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, proxy=PROXY
)
db = Database(DB_PATH)


def get_peer_type_new(peer_id: int) -> str:
    peer_id_str = str(peer_id)
    if not peer_id_str.startswith("-"):
        return "user"
    elif peer_id_str.startswith("-100"):
        return "channel"
    else:
        return "chat"


utils.get_peer_type = get_peer_type_new


def scan_videos_directory():
    print("Scanning videos directory for new files...")
    list_of_videos = [v for v in os.listdir(VIDEOS_DIR) if v.endswith(".mp4")]
    for video_name in list_of_videos:
        video_path = os.path.join(VIDEOS_DIR, video_name)
        if os.path.isfile(video_path) and db.check_video(video_name):
            print(f"New video found: {video_name}")
            db.insert_video(video_name)


def get_video_duration(file_path):
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                file_path,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        duration = float(result.stdout.strip())
        return duration
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return None


def format_duration(duration):
    hours, remainder = divmod(int(duration), 3600)
    minutes, seconds = divmod(remainder, 60)
    formatted = []
    if hours > 0:
        formatted.append(f"0{hours}:")
    else:
        formatted.append("00:")
    if minutes > 0:
        if minutes < 10:
            formatted.append(f"0{minutes}:")
        else:
            formatted.append(f"{minutes}:")
    elif minutes >= 10:
        formatted.append(f"{minutes}:")
    else:
        formatted.append(f"{minutes}:")
    if seconds > 0 or not formatted:
        if seconds < 10:
            formatted.append(f"0{seconds}")
        else:
            formatted.append(f"{seconds}")
    else:
        formatted.append("00:")
    return "".join(formatted)


def video_durations(file_name):
    directory = VIDEOS_DIR
    file_path = os.path.join(directory, file_name)
    duration = get_video_duration(file_path)
    formatted_duration = format_duration(duration)
    return formatted_duration, int(duration)


def made_caption(video_name):
    """Create caption for video"""
    base_name = video_name.split(".")[1]
    date_part, time_part = base_name.split("-")
    formatted_date = date_part.replace("_", "/").replace("shiraz", "")
    formatted_time = time_part.replace("_", ":")
    caption = f"{formatted_date}   {formatted_time}"
    formatted_duration, duration = video_durations(video_name)
    return (
        "\n".join(["شروع:", caption, "مدت:", formatted_duration]),
        duration,
        formatted_date,
        formatted_time,
    )


def upload_videos():
    print("Starting video upload...")
    unuploaded_videos = db.list_unload_videos()
    if not unuploaded_videos:
        print("No videos to upload.")
        return

    with app:
        for video_name in unuploaded_videos:
            video_path = os.path.join(VIDEOS_DIR, video_name)
            if not os.path.exists(video_path):
                print(f"Video not found: {video_path}. Skipping.")
                continue

            try:
                print(f"Uploading video: {video_name}")
                caption, duration, formatted_date, formatted_time = made_caption(
                    video_name
                )
                formatted_time = ":".join(formatted_time.split(":")[:-1])
                thumbnail_text = f"جلسه شورای شهر شیراز\nتاریخ {formatted_date}\nساعت {formatted_time}"

                # Create thumbnail
                thumbnail_path = thumbnail_creator(
                    title=thumbnail_text, name=video_name[:-4]
                )
                for chat_id in CHAT_IDS:
                    app.send_video(
                        chat_id=chat_id,
                        video=video_path,
                        caption=caption,
                        duration=duration,
                        thumb=thumbnail_path,
                    )
                db.upload_video(video_name)
                print(f"Successfully uploaded: {video_name}")
            except FloodWait as e:
                print(f"FloodWait: Sleeping for {e.x} seconds before retrying...")
                time.sleep(e.x)
            except Exception as e:
                print(f"Failed to upload {video_name}: {e}")


scan_videos_directory()
upload_videos()
