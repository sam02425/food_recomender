from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship, Session
from backend.app.db import Base

class UserPreference(Base):
    __tablename__ = 'user_preferences'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    preferred_cuisines = Column(String)  # Comma-separated list
    dietary_restrictions = Column(String)  # Comma-separated list
    favorite_dishes = Column(String)  # Comma-separated list
    preference_score = Column(Float, default=0.0)
    extra_data = Column(JSON, default={})

    user = relationship('User', back_populates='preferences')

    def __repr__(self):
        return f"<UserPreference(user_id={self.user_id}, cuisines={self.preferred_cuisines}, restrictions={self.dietary_restrictions})>"

    def update_preferences(self, cuisines=None, restrictions=None, favorites=None, score=None, extra=None):
        if cuisines is not None:
            self.preferred_cuisines = ','.join(cuisines) if isinstance(cuisines, list) else cuisines
        if restrictions is not None:
            self.dietary_restrictions = ','.join(restrictions) if isinstance(restrictions, list) else restrictions
        if favorites is not None:
            self.favorite_dishes = ','.join(favorites) if isinstance(favorites, list) else favorites
        if score is not None:
            self.preference_score = score
        if extra is not None:
            self.extra_data = extra

    def get_preferences_dict(self):
        """Return preferences as a dictionary with lists."""
        return {
            'preferred_cuisines': self.parse_list(self.preferred_cuisines),
            'dietary_restrictions': self.parse_list(self.dietary_restrictions),
            'favorite_dishes': self.parse_list(self.favorite_dishes),
            'preference_score': self.preference_score,
            'extra_data': self.extra_data or {}
        }

    @staticmethod
    def parse_list(value):
        if not value:
            return []
        if isinstance(value, list):
            return value
        return [v.strip() for v in value.split(',') if v.strip()]

    @classmethod
    def get_or_create(cls, db: Session, user_id: int):
        """Fetch or create a UserPreference for a user."""
        instance = db.query(cls).filter_by(user_id=user_id).first()
        if instance:
            return instance
        instance = cls(user_id=user_id)
        db.add(instance)
        db.commit()
        db.refresh(instance)
        return instance