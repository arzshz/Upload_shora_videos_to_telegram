import sqlite3


class Database:
    def __init__(self, db_path):
        self.db = sqlite3.connect(db_path)
        self.cursor = self.db.cursor()
        self.create_table()

    def create_table(self, table_name="videos"):
        command = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            name TEXT DEFAULT "",
            upload BOOLEAN DEFAULT FALSE,
            upload_date DATE DEFAULT CURRENT_DATE
        );
        """
        self.cursor.execute(command)
        self.db.commit()

    def insert_video(self, video_name, table_name="videos"):
        command = f"INSERT INTO {table_name} (name) VALUES (?);"
        self.cursor.execute(command, (video_name,))
        self.db.commit()

    def upload_video(self, video_name, table_name="videos"):
        command = f"""
        UPDATE {table_name}
        SET upload = TRUE, upload_date = CURRENT_DATE
        WHERE name = ?;
        """
        self.cursor.execute(command, (video_name,))
        self.db.commit()

    def check_video(self, video_name, table_name="videos"):
        command = f"SELECT 1 FROM {table_name} WHERE name = ?;"
        return self.cursor.execute(command, (video_name,)).fetchone() is None

    def list_unload_videos(self, table_name="videos"):
        command = f"SELECT name FROM {table_name} WHERE upload = FALSE;"
        unload_videos = self.cursor.execute(command).fetchall()
        return [video[0] for video in unload_videos]
