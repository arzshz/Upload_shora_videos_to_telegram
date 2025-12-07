import asyncio
import os
import subprocess
from pathlib import Path

from telethon import TelegramClient
from telethon.tl.types import InputMediaUploadedDocument, DocumentAttributeVideo

from config import (
    API_ID,
    API_HASH,
    DB_PATH,
    VIDEOS_DIR,
    CHAT_IDS,
    PROXY_HOST,
    PROXY_PORT,
)
from db_management import Database
from thumbnail_utils import thumbnail_creator

BASE_DIR = Path(__file__).resolve().parent

# Initialize Telethon client (for user account, not bot)
client = TelegramClient(
    "video_uploader",
    api_id=API_ID,
    api_hash=API_HASH,
    proxy=("socks5", PROXY_HOST, PROXY_PORT),
)

db = Database(DB_PATH)


def scan_videos_directory():
    """Scan videos directory for new files"""
    print("Scanning videos directory for new files...")
    list_of_videos = [v for v in os.listdir(VIDEOS_DIR) if v.endswith(".mp4")]
    for video_name in list_of_videos:
        video_path = os.path.join(VIDEOS_DIR, video_name)
        if os.path.isfile(video_path) and db.check_video(video_name):
            print(f"New video found: {video_name}")
            db.insert_video(video_name)


def get_video_duration(file_path):
    """Get video duration using ffprobe"""
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
    """Format duration as HH:MM:SS"""
    hours, remainder = divmod(int(duration), 3600)
    minutes, seconds = divmod(remainder, 60)
    formatted = []

    if 0 <= hours < 10:
        formatted.append(f"0{hours}:")
    elif 10 <= hours:
        formatted.append(f"{hours}:")

    if 0 <= minutes < 10:
        formatted.append(f"0{minutes}:")
    elif minutes >= 10:
        formatted.append(f"{minutes}:")

    if 0 <= seconds < 10 or not formatted:
        formatted.append(f"0{seconds}")
    elif 10 <= seconds or not formatted:
        formatted.append(f"{seconds}")

    return "".join(formatted)


def video_durations(file_name):
    """Get video duration and formatted duration"""
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


async def upload_videos():
    """Upload videos to Telegram channels/groups"""
    print("Starting video upload...")
    unuploaded_videos = db.list_unload_videos()

    if not unuploaded_videos:
        print("No videos to upload.")
        return

    for video_name in unuploaded_videos:
        video_path = os.path.join(VIDEOS_DIR, video_name)
        if not os.path.exists(video_path):
            print(f"Video not found: {video_path}. Skipping.")
            continue

        try:
            print(f"Uploading video: {video_name}")
            caption, duration, formatted_date, formatted_time = made_caption(video_name)
            formatted_time = ":".join(formatted_time.split(":")[:-1])
            thumbnail_text = f"شورا\n{formatted_date}\n{formatted_time}"

            # Create thumbnail
            thumbnail_path = thumbnail_creator(
                title=thumbnail_text, name=video_name[:-4]
            )
            # Prepare thumbnail if exists
            thumb = None
            if os.path.exists(thumbnail_path):
                thumb = await client.upload_file(thumbnail_path)

            uploaded = await client.upload_file(video_path)

            upload_success = False

            # Upload video to each chat
            for chat_id in CHAT_IDS:
                try:
                    attributes = [
                        DocumentAttributeVideo(
                            duration=duration, w=1280, h=960, supports_streaming=True
                        )
                    ]

                    media = InputMediaUploadedDocument(
                        file=uploaded,
                        mime_type="video/mp4",
                        attributes=attributes,
                        thumb=thumb,
                    )

                    await client.send_message(chat_id, message=caption, file=media)
                    upload_success = True
                    print(f"Uploaded to {chat_id}")

                except Exception as e:
                    print(f"Failed to upload to {chat_id}: {e}")

            # Clean up and update database
            if os.path.exists(thumbnail_path):
                os.remove(thumbnail_path)

            if upload_success:
                db.upload_video(video_name)
                print(f"Successfully uploaded: {video_name}")
            else:
                print(f"Failed to upload {video_name} to any destination")

        except Exception as e:
            print(f"Failed to upload {video_name}: {e}")


async def main():
    """Main async function"""
    await client.start()
    print("Client connected")

    scan_videos_directory()
    await upload_videos()

    await client.disconnect()
    print("Done")


if __name__ == "__main__":
    asyncio.run(main())
