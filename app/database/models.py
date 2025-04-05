import sqlite3
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.database.db import get_db
from datetime import datetime


class User(UserMixin):
    def __init__(self, id, username, email, password):
        self.id = id
        self.username = username
        self.email = email
        self.password = password

    @staticmethod
    def get_by_id(user_id):
        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE id = ?', (user_id,)
        ).fetchone()

        if user is None:
            return None

        return User(
            id=user['id'],
            username=user['username'],
            email=user['email'],
            password=user['password']
        )

    @staticmethod
    def get_by_username(username):
        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            return None

        return User(
            id=user['id'],
            username=user['username'],
            email=user['email'],
            password=user['password']
        )

    @staticmethod
    def get_by_email(email):
        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE email = ?', (email,)
        ).fetchone()

        if user is None:
            return None

        return User(
            id=user['id'],
            username=user['username'],
            email=user['email'],
            password=user['password']
        )

    @staticmethod
    def create(username, email, password):
        db = get_db()
        try:
            db.execute(
                'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                (username, email, generate_password_hash(password))
            )
            db.commit()
            return User.get_by_username(username)
        except sqlite3.IntegrityError:
            return None

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Video:
    def __init__(self, id, title, description, filename, thumbnail, duration, category, uploaded_at, uploader_id):
        self.id = id
        self.title = title
        self.description = description
        self.filename = filename
        self.thumbnail = thumbnail
        self.duration = duration
        self.category = category
        self.uploaded_at = uploaded_at
        self.uploader_id = uploader_id

    @staticmethod
    def get_by_id(video_id):
        db = get_db()
        video = db.execute(
            'SELECT * FROM videos WHERE id = ?', (video_id,)
        ).fetchone()

        if video is None:
            return None

        return Video(
            id=video['id'],
            title=video['title'],
            description=video['description'],
            filename=video['filename'],
            thumbnail=video['thumbnail'],
            duration=video['duration'],
            category=video['category'],
            uploaded_at=video['uploaded_at'],
            uploader_id=video['uploader_id']
        )

    @staticmethod
    def get_all(limit=None, offset=0, category=None):
        db = get_db()
        query = 'SELECT * FROM videos'
        params = []

        if category:
            query += ' WHERE category = ?'
            params.append(category)

        query += ' ORDER BY uploaded_at DESC'

        if limit:
            query += ' LIMIT ? OFFSET ?'
            params.extend([limit, offset])

        videos = db.execute(query, params).fetchall()

        return [Video(
            id=video['id'],
            title=video['title'],
            description=video['description'],
            filename=video['filename'],
            thumbnail=video['thumbnail'],
            duration=video['duration'],
            category=video['category'],
            uploaded_at=video['uploaded_at'],
            uploader_id=video['uploader_id']
        ) for video in videos]

    @staticmethod
    def create(title, description, filename, thumbnail, duration, category, uploader_id):
        db = get_db()
        cursor = db.execute(
            '''
            INSERT INTO videos 
            (title, description, filename, thumbnail, duration, category, uploader_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''',
            (title, description, filename, thumbnail, duration, category, uploader_id)
        )
        db.commit()

        return Video.get_by_id(cursor.lastrowid)

    def update(self):
        db = get_db()
        db.execute(
            '''
            UPDATE videos
            SET title = ?, description = ?, filename = ?, thumbnail = ?, 
                duration = ?, category = ?
            WHERE id = ?
            ''',
            (self.title, self.description, self.filename, self.thumbnail,
             self.duration, self.category, self.id)
        )
        db.commit()

    def delete(self):
        db = get_db()
        db.execute('DELETE FROM videos WHERE id = ?', (self.id,))
        db.commit()


class VideoProgress:
    def __init__(self, user_id, video_id, current_time, watched, last_watched):
        self.user_id = user_id
        self.video_id = video_id
        self.current_time = current_time
        self.watched = watched
        self.last_watched = last_watched

    @staticmethod
    def get_progress(user_id, video_id):
        db = get_db()
        progress = db.execute(
            'SELECT * FROM user_video_progress WHERE user_id = ? AND video_id = ?',
            (user_id, video_id)
        ).fetchone()

        if progress is None:
            return VideoProgress(user_id, video_id, 0, False, datetime.now())

        return VideoProgress(
            user_id=progress['user_id'],
            video_id=progress['video_id'],
            current_time=progress['current_time'],
            watched=bool(progress['watched']),
            last_watched=progress['last_watched']
        )

    @staticmethod
    def update_progress(user_id, video_id, current_time, watched=False):
        db = get_db()
        db.execute(
            '''
            INSERT INTO user_video_progress (user_id, video_id, current_time, watched, last_watched)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id, video_id) 
            DO UPDATE SET 
                current_time = ?,
                watched = ?,
                last_watched = CURRENT_TIMESTAMP
            ''',
            (user_id, video_id, current_time, watched, current_time, watched)
        )
        db.commit()

    @staticmethod
    def get_recently_watched(user_id, limit=5):
        db = get_db()
        rows = db.execute(
            '''
            SELECT v.*, p.current_time, p.watched, p.last_watched
            FROM user_video_progress p
            JOIN videos v ON p.video_id = v.id
            WHERE p.user_id = ?
            ORDER BY p.last_watched DESC
            LIMIT ?
            ''',
            (user_id, limit)
        ).fetchall()

        return rows