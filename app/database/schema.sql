DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS videos;
DROP TABLE IF EXISTS user_video_progress;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE videos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    filename TEXT NOT NULL,
    thumbnail TEXT,
    duration INTEGER,
    category TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    uploader_id INTEGER NOT NULL,
    FOREIGN KEY (uploader_id) REFERENCES users (id)
);

CREATE TABLE user_video_progress (
    user_id INTEGER NOT NULL,
    video_id INTEGER NOT NULL,
    current_time FLOAT NOT NULL DEFAULT 0,
    watched BOOLEAN NOT NULL DEFAULT 0,
    last_watched TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, video_id),
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (video_id) REFERENCES videos (id)
);

-- Índices para mejorar el rendimiento
CREATE INDEX idx_videos_uploader ON videos(uploader_id);
CREATE INDEX idx_progress_user ON user_video_progress(user_id);
CREATE INDEX idx_progress_video ON user_video_progress(video_id);