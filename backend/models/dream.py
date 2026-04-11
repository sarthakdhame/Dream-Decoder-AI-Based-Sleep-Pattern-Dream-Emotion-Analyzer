"""
Dream Decoder - Dream Model
Handles CRUD operations for dream entries
"""
import json
from datetime import datetime
from backend.database.db import get_db_connection


def _parse_json_field(value, default):
    if not value:
        return default
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(value)
    except (TypeError, ValueError):
        return default


class Dream:
    """Dream model for database operations."""
    
    def __init__(self, id=None, user_id=None, content=None, created_at=None, sentiment=None,
                 sentiment_score=None, primary_emotion=None, emotion_scores=None,
                 keywords=None, entities=None, interpretation=None, jungian_report=None):
        self.id = id
        self.user_id = user_id
        self.content = content
        self.created_at = created_at
        self.sentiment = sentiment
        self.sentiment_score = sentiment_score
        self.primary_emotion = primary_emotion
        self.emotion_scores = emotion_scores or {}
        self.keywords = keywords or []
        self.entities = entities or []
        self.interpretation = interpretation or {}
        self.jungian_report = jungian_report or {}
    
    def to_dict(self):
        """Convert dream to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'content': self.content,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'sentiment': self.sentiment,
            'sentiment_score': self.sentiment_score,
            'primary_emotion': self.primary_emotion,
            'emotion_scores': self.emotion_scores,
            'keywords': self.keywords,
            'entities': self.entities,
            'interpretation': self.interpretation,
            'jungian_report': self.jungian_report
        }
    
    @staticmethod
    def from_row(row):
        """Create Dream object from database row."""
        if row is None:
            return None
        
        return Dream(
            id=row['id'],
            user_id=row['user_id'],
            content=row['content'],
            created_at=row['created_at'],
            sentiment=row['sentiment'],
            sentiment_score=row['sentiment_score'],
            primary_emotion=row['primary_emotion'],
            emotion_scores=_parse_json_field(row['emotion_scores'], {}),
            keywords=_parse_json_field(row['keywords'], []),
            entities=_parse_json_field(row['entities'], []),
            interpretation=_parse_json_field(row['interpretation'], {}) if 'interpretation' in row.keys() else {},
            jungian_report=_parse_json_field(row['jungian_report'], {}) if 'jungian_report' in row.keys() else {}
        )
    
    def save(self):
        """Save dream to database (insert or update)."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            if self.id is None:
                # Insert new dream
                cursor.execute('''
                    INSERT INTO dreams (user_id, content, sentiment, sentiment_score, primary_emotion,
                                       emotion_scores, keywords, entities, interpretation, jungian_report)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    self.user_id,
                    self.content,
                    self.sentiment,
                    self.sentiment_score,
                    self.primary_emotion,
                    json.dumps(self.emotion_scores),
                    json.dumps(self.keywords),
                    json.dumps(self.entities),
                    json.dumps(self.interpretation),
                    json.dumps(self.jungian_report) if self.jungian_report is not None else None
                ))
                self.id = cursor.lastrowid
            else:
                # Update existing dream
                cursor.execute('''
                    UPDATE dreams SET content=?, sentiment=?, sentiment_score=?,
                           primary_emotion=?, emotion_scores=?, keywords=?, entities=?, interpretation=?, jungian_report=?
                    WHERE id=?
                ''', (
                    self.content,
                    self.sentiment,
                    self.sentiment_score,
                    self.primary_emotion,
                    json.dumps(self.emotion_scores),
                    json.dumps(self.keywords),
                    json.dumps(self.entities),
                    json.dumps(self.interpretation),
                    json.dumps(self.jungian_report) if self.jungian_report is not None else None,
                    self.id
                ))
            
            conn.commit()
            
            # Get the created_at timestamp
            if self.created_at is None:
                cursor.execute('SELECT created_at FROM dreams WHERE id=?', (self.id,))
                row = cursor.fetchone()
                if row:
                    self.created_at = row['created_at']
        
        return self
    
    @staticmethod
    def get_all(user_id, limit=100, offset=0):
        """Get all dreams for a user, ordered by most recent first."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM dreams WHERE user_id=? ORDER BY created_at DESC LIMIT ? OFFSET ?
            ''', (user_id, limit, offset))
            
            rows = cursor.fetchall()
            return [Dream.from_row(row) for row in rows]
    
    @staticmethod
    def get_by_id(dream_id):
        """Get a dream by ID."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM dreams WHERE id=?', (dream_id,))
            row = cursor.fetchone()
            return Dream.from_row(row)
    
    @staticmethod
    def delete(dream_id):
        """Delete a dream by ID."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM dreams WHERE id=?', (dream_id,))
            deleted = cursor.rowcount > 0
            
            conn.commit()
            return deleted

    @staticmethod
    def clear_jungian_report(dream_id, user_id):
        """Remove the Jungian report from a dream owned by the given user."""
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE dreams
                SET jungian_report=?
                WHERE id=? AND user_id=?
            ''', (json.dumps({}), dream_id, user_id))

            updated = cursor.rowcount > 0
            conn.commit()
            return updated
    
    @staticmethod
    def get_recent(user_id, days=7):
        """Get dreams from the last N days for a user."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM dreams 
                WHERE user_id=? AND created_at >= datetime('now', '-' || ? || ' days')
                ORDER BY created_at DESC
            ''', (user_id, days))
            
            rows = cursor.fetchall()
            return [Dream.from_row(row) for row in rows]
    
    @staticmethod
    def count(user_id):
        """Get total count of dreams for a user."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) as count FROM dreams WHERE user_id=?', (user_id,))
            row = cursor.fetchone()
            return row['count'] if row else 0
