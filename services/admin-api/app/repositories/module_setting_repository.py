"""
Repository for Module Settings data access
"""

from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.module_setting import ModuleSetting, SystemModule, ModuleStatus


class ModuleSettingRepository:
    """Repository for module settings operations"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, setting_id: int) -> Optional[ModuleSetting]:
        """Get setting by ID"""
        return (
            self.db.query(ModuleSetting).filter(ModuleSetting.id == setting_id).first()
        )

    def get_by_key(self, module_name: str, setting_key: str) -> Optional[ModuleSetting]:
        """Get setting by module name and key"""
        return (
            self.db.query(ModuleSetting)
            .filter(
                and_(
                    ModuleSetting.module_name == module_name,
                    ModuleSetting.setting_key == setting_key,
                )
            )
            .first()
        )

    def get_module_settings(
        self,
        module_name: str,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
        is_public: Optional[bool] = None,
    ) -> Tuple[List[ModuleSetting], int]:
        """Get all settings for a specific module with optional filters"""
        query = self.db.query(ModuleSetting).filter(
            ModuleSetting.module_name == module_name
        )

        if category:
            query = query.filter(ModuleSetting.category == category)

        if is_public is not None:
            query = query.filter(ModuleSetting.is_public == is_public)

        total = query.count()
        settings = query.offset(skip).limit(limit).all()

        return settings, total

    def get_all_settings(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
    ) -> Tuple[List[ModuleSetting], int]:
        """Get all settings across all modules"""
        query = self.db.query(ModuleSetting)

        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    ModuleSetting.module_name.ilike(search_pattern),
                    ModuleSetting.setting_key.ilike(search_pattern),
                    ModuleSetting.display_name.ilike(search_pattern),
                )
            )

        total = query.count()
        settings = query.offset(skip).limit(limit).all()

        return settings, total

    def create(self, setting: ModuleSetting) -> ModuleSetting:
        """Create a new module setting"""
        self.db.add(setting)
        self.db.commit()
        self.db.refresh(setting)
        return setting

    def update(self, setting: ModuleSetting) -> ModuleSetting:
        """Update an existing module setting"""
        self.db.commit()
        self.db.refresh(setting)
        return setting

    def delete(self, setting: ModuleSetting) -> None:
        """Delete a module setting"""
        self.db.delete(setting)
        self.db.commit()


class SystemModuleRepository:
    """Repository for system modules operations"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, module_id: int) -> Optional[SystemModule]:
        """Get module by ID"""
        return self.db.query(SystemModule).filter(SystemModule.id == module_id).first()

    def get_by_name(self, module_name: str) -> Optional[SystemModule]:
        """Get module by name"""
        return (
            self.db.query(SystemModule)
            .filter(SystemModule.module_name == module_name)
            .first()
        )

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[ModuleStatus] = None,
    ) -> Tuple[List[SystemModule], int]:
        """Get all system modules"""
        query = self.db.query(SystemModule)

        if status:
            query = query.filter(SystemModule.status == status)

        # Order by sort_order and then by display_name
        query = query.order_by(SystemModule.sort_order, SystemModule.display_name)

        total = query.count()
        modules = query.offset(skip).limit(limit).all()

        return modules, total

    def create(self, module: SystemModule) -> SystemModule:
        """Create a new system module"""
        self.db.add(module)
        self.db.commit()
        self.db.refresh(module)
        return module

    def update(self, module: SystemModule) -> SystemModule:
        """Update an existing system module"""
        self.db.commit()
        self.db.refresh(module)
        return module

    def delete(self, module: SystemModule) -> None:
        """Delete a system module"""
        self.db.delete(module)
        self.db.commit()
