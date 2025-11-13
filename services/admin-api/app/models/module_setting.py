"""
Module Settings model for managing module configurations
"""

from sqlalchemy import (
    Column,
    String,
    Text,
    Boolean,
    Enum as SQLEnum,
    Integer,
    event,
)
from app.models.base import BaseModel
from app.core.utils import generate_slug
import enum


class SettingType(str, enum.Enum):
    """Setting value type enumeration"""

    STRING = "STRING"
    INTEGER = "INTEGER"
    BOOLEAN = "BOOLEAN"
    JSON = "JSON"


class ModuleStatus(str, enum.Enum):
    """Module status enumeration"""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    MAINTENANCE = "MAINTENANCE"


class ModuleSetting(BaseModel):
    """
    Module Settings model for storing module-specific configurations

    Attributes:
        id: Primary key (UUID)
        slug: URL-friendly identifier
        module_name: Name of the module (auth, asset, procurement, etc.)
        setting_key: Unique setting key within the module
        setting_value: Setting value (stored as text, type indicates how to parse)
        setting_type: Type of the setting value
        display_name: Human-readable setting name
        description: Setting description
        is_public: Whether setting is publicly accessible (non-sensitive)
        is_editable: Whether setting can be edited via UI
        default_value: Default value for the setting
        validation_rules: JSON validation rules
        created_at: Creation timestamp
        updated_at: Last update timestamp
        updated_by: User UUID who last updated the setting
    """

    __tablename__ = "module_settings"
    __table_args__ = {"schema": "admin_db"}

    module_name = Column(String(50), nullable=False, index=True)
    setting_key = Column(String(100), nullable=False, index=True)
    setting_value = Column(Text, nullable=True)
    setting_type = Column(
        SQLEnum(SettingType), nullable=False, default=SettingType.STRING
    )

    # Display and documentation
    display_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)  # e.g., "General", "Security", "Email"

    # Access control
    is_public = Column(Boolean, default=False)  # Can be read by non-admins
    is_editable = Column(Boolean, default=True)  # Can be edited via UI

    # Validation
    default_value = Column(Text, nullable=True)
    validation_rules = Column(Text, nullable=True)  # JSON string with validation rules

    # Audit field (UUID reference)
    updated_by = Column(String(32), nullable=True)  # User UUID

    def __repr__(self):
        return f"<ModuleSetting(module='{self.module_name}', key='{self.setting_key}')>"


# Event listener to auto-generate slug from module_name and setting_key
@event.listens_for(ModuleSetting, "before_insert")
def generate_module_setting_slug(mapper, connection, target):
    """Auto-generate slug from module name and key if not provided"""
    if not target.slug:
        target.slug = generate_slug(f"{target.module_name}-{target.setting_key}")


class SystemModule(BaseModel):
    """
    System Modules model for managing installed modules

    Attributes:
        id: Primary key (UUID)
        slug: URL-friendly identifier
        module_name: Unique module identifier
        display_name: Human-readable module name
        description: Module description
        version: Current module version
        status: Module status (active, inactive, maintenance)
        api_endpoint: Module API base URL
        frontend_endpoint: Module frontend base URL
        icon: Module icon name (for UI)
        sort_order: Display order in navigation
        requires_auth: Whether module requires authentication
        allowed_roles: Comma-separated role names allowed to access
        is_system_module: Whether module is a core system module (cannot be disabled)
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "system_modules"
    __table_args__ = {"schema": "admin_db"}

    module_name = Column(String(50), unique=True, nullable=False, index=True)
    display_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    version = Column(String(20), nullable=True)

    # Status and configuration
    status = Column(SQLEnum(ModuleStatus), nullable=False, default=ModuleStatus.ACTIVE)
    api_endpoint = Column(String(500), nullable=True)
    frontend_endpoint = Column(String(500), nullable=True)
    icon = Column(String(50), nullable=True)  # Lucide icon name
    sort_order = Column(Integer, default=0)

    # Access control
    requires_auth = Column(Boolean, default=True)
    allowed_roles = Column(Text, nullable=True)  # Comma-separated role names
    is_system_module = Column(Boolean, default=False)  # Cannot be disabled

    def __repr__(self):
        return f"<SystemModule(name='{self.module_name}', status='{self.status}')>"


# Event listener to auto-generate slug from module_name
@event.listens_for(SystemModule, "before_insert")
def generate_system_module_slug(mapper, connection, target):
    """Auto-generate slug from module name if not provided"""
    if not target.slug:
        target.slug = generate_slug(target.module_name)
