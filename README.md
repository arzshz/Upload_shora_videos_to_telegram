## Upload Shora Videos to Telegram
A small Python project that watches the VIDEOS_DIR folder for new videos and automatically uploads them to Telegram.

### ⚙️ How It Works
• Scans VIDEOS_DIR for new video files.

• Tracks uploaded videos in an SQLite database.

• Uploads new files for defined CHAT_IDS.

• Designed to run continuously (systemd recommended)

### 📁 Setup
1. Create and activate a virtual environment
```
python3 -m venv .venv
source .venv/bin/activate
```
2. Install dependencies
```
pip install -r requirements.txt
```
3. Create and configure config.py

Copy the contents of config.example.py into config.py, then edit the values as needed.

### ▶️ Run
```
python3 main.py
```

### 🔧 Run as a systemd Service (Recommended)

• Create the systemd service:
```
sudo vim /etc/systemd/system/shora-video-uploader.service
```
Sample contents for it:
```
[Unit]
Description=Upload Shora Videos to Telegram
After=network.target

[Service]
User=YOUR_USER
WorkingDirectory=/upload-shora-telegram
Environment="PATH=/upload-shora-telegram/.venv/bin:/usr/bin:/bin"
ExecStart=/upload-shora-telegram/.venv/bin/python3 main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```
Then, enable it:
```
sudo systemctl daemon-reload
sudo systemctl enable shora-video-uploader.service
sudo systemctl start shora-video-uploader.service
```
• Adding a timer for the systemd service is recommeneded:
```
sudo vim /etc/systemd/system/shora-video-uploader.timer
```
Sample contents for it:
```
[Unit]
Description=Timer for Upload Shora Videos to Telegram

[Timer]
OnCalendar=*-*-* 01:00:00
Persistent=true

[Install]
WantedBy=timers.target
```
Then, enable it:
```
sudo systemctl daemon-reload
sudo systemctl enable shora-video-uploader.timer
sudo systemctl start shora-video-uploader.timer
```
