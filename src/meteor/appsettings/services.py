from typing import Optional
from uuid import UUID
from fastapi import HTTPException

from meteor.database.core import DbSession
from sqlalchemy import select, insert, update

from .schema import AppSetting

from .models import MeteorAppSetting


async def get_by_id(*, db_session: DbSession, setting_id: UUID) -> Optional[MeteorAppSetting]:
    # return db_session.query(AppSettings).filter(AppSettings.id == setting_id).first()
    return await db_session.scalar(select(AppSetting).where(AppSetting.id == setting_id))


async def create_setting(*, db_session: DbSession, setting_to_add: AppSetting) -> MeteorAppSetting:
    # setting = AppSettingsEntity(**setting_to_add.model_dump())
    # db_session.add(setting)
    # db_session.commit()
    # db_session.refresh(setting)
    # return setting
    setting_to_add = MeteorAppSetting(**setting_to_add.model_dump())

    # db_session.add(setting)
    # await db_session.flush()
    return await db_session.scalar(insert(MeteorAppSetting).values(setting_to_add).returning(MeteorAppSetting))


async def update_setting(*, db_session: DbSession, setting: AppSetting) -> MeteorAppSetting:
    # return db_session.query(AppSettings).filter_by(AppSettings.id == setting.id).update(setting)
    settings_to_update = MeteorAppSetting(**setting.model_dump())
    setting = await db_session.scalar(
        update(MeteorAppSetting)
        .where(MeteorAppSetting.id == settings_to_update.id)
        .values(settings_to_update)
        .returning(MeteorAppSetting)
    )
