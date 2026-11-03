"""Repository for ApplicationSettings key-value storage."""

from sqlalchemy.orm import Session
from app.models.settings import ApplicationSettings


class SettingsRepository:
    """Encapsulates database access for application settings and weights."""

    def __init__(self, db: Session):
        self.db = db

    def get(self, key: str) -> dict | None:
        """Get parsed JSON value for key."""
        setting = self.db.query(ApplicationSettings).filter(ApplicationSettings.key == key).first()
        return setting.value_json if setting else None

    def set(self, key: str, value_json: dict) -> ApplicationSettings:
        """Set or update JSON value for key."""
        setting = self.db.query(ApplicationSettings).filter(ApplicationSettings.key == key).first()
        if setting:
            setting.value_json = value_json
        else:
            setting = ApplicationSettings(key=key, value_json=value_json)
            self.db.add(setting)
        self.db.commit()
        self.db.refresh(setting)
        return setting
