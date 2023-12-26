from typing import Optional
from uuid import UUID
from sqlalchemy import insert, select

from meteor.appsettings.models import AppSettings, AppSettingsEntity
from meteor.database import DbSession

def get_app_setting_by_id(*, db_session: DbSession, setting_id: UUID) -> Optional[AppSettings]:
    return db_session.query(AppSettings).filter(AppSettings.id == setting_id).first()

def create(*, db_session: DbSession, setting_to_add: AppSettings) -> AppSettings:
    setting = AppSettingsEntity(**setting_to_add.model_dump())
    db_session.add(setting)
    db_session.commit()
    db_session.refresh(setting)
    return setting

def update_app_setting(*, db_session: DbSession, setting: AppSettings) -> AppSettings:
    return db_session.query(AppSettings).filter_by(AppSettings.id == setting.id).update(setting)