#!/usr/bin/env python3
"""
Script to batch update all remaining models with UUID foreign keys
This script provides the SQL-like replacements needed for all models
"""

import re
from pathlib import Path

# Model files and their FK updates
MODEL_UPDATES = {
    # Asset Service
    "services/asset-api/app/models/category.py": [
        ("Integer, ForeignKey", "String(32), ForeignKey"),
        ("Column(Integer, nullable", "Column(String(32), nullable"),
    ],
    "services/asset-api/app/models/assignment.py": [
        ("asset_id = Column(Integer,", "asset_id = Column(String(32),"),
        ("user_id = Column(Integer,", "user_id = Column(String(32),"),
        ("assigned_by = Column(Integer,", "assigned_by = Column(String(32),"),
        ("returned_by = Column(Integer,", "returned_by = Column(String(32),"),
    ],
    "services/asset-api/app/models/attachment.py": [
        ("asset_id = Column(Integer,", "asset_id = Column(String(32),"),
        ("uploaded_by = Column(Integer,", "uploaded_by = Column(String(32),"),
    ],
    "services/asset-api/app/models/depreciation.py": [
        ("asset_id = Column(Integer,", "asset_id = Column(String(32),"),
        ("calculated_by = Column(Integer,", "calculated_by = Column(String(32),"),
    ],
    "services/asset-api/app/models/maintenance.py": [
        ("asset_id = Column(Integer,", "asset_id = Column(String(32),"),
        ("performed_by = Column(Integer,", "performed_by = Column(String(32),"),
        ("created_by = Column(Integer,", "created_by = Column(String(32),"),
    ],
    # Admin Service
    "services/admin-api/app/models/module_settings.py": [
        ("module_id = Column(Integer,", "module_id = Column(String(32),"),
        ("updated_by = Column(Integer,", "updated_by = Column(String(32),"),
    ],
    "services/admin-api/app/models/audit_logs.py": [
        ("user_id = Column(Integer,", "user_id = Column(String(32),"),
        ("entity_id = Column(String(100),", "entity_id = Column(String(32),"),  # Now UUID
    ],
    "services/admin-api/app/models/trash_items.py": [
        ("deleted_by = Column(Integer,", "deleted_by = Column(String(32),"),
        ("restored_by = Column(Integer,", "restored_by = Column(String(32),"),
        ("permanently_deleted_by = Column(Integer,", "permanently_deleted_by = Column(String(32),"),
    ],
}

# Slug generation event listeners to add
SLUG_GENERATORS = {
    "services/asset-api/app/models/category.py": '''

# Event listener to auto-generate slug from name
@event.listens_for(AssetCategory, "before_insert")
def generate_category_slug(mapper, connection, target):
    """Auto-generate slug from name if not provided"""
    if not target.slug:
        target.slug = generate_slug(target.name)
''',
    "services/asset-api/app/models/assignment.py": '''

# Event listener to auto-generate slug
@event.listens_for(AssetAssignment, "before_insert")
def generate_assignment_slug(mapper, connection, target):
    """Auto-generate slug from asset_id and user_id if not provided"""
    if not target.slug:
        target.slug = generate_slug(f"assignment-{target.asset_id[:8]}-{target.user_id[:8]}")
''',
    "services/admin-api/app/models/module_settings.py": '''

# Event listener to auto-generate slug
@event.listens_for(ModuleSetting, "before_insert")
def generate_module_setting_slug(mapper, connection, target):
    """Auto-generate slug from module name and key if not provided"""
    if not target.slug:
        target.slug = generate_slug(f"{target.module_name}-{target.key}")
''',
    "services/admin-api/app/models/system_modules.py": '''

# Event listener to auto-generate slug
@event.listens_for(SystemModule, "before_insert")
def generate_system_module_slug(mapper, connection, target):
    """Auto-generate slug from module name if not provided"""
    if not target.slug:
        target.slug = generate_slug(target.name)
''',
}

# Import statements to add
IMPORT_ADDITIONS = {
    "event": "from sqlalchemy import event",
    "generate_slug": "from app.core.utils import generate_slug",
}


def update_model_file(file_path: str, replacements: list, slug_generator: str = None):
    """Update a model file with UUID foreign keys and slug generation"""
    path = Path(file_path)

    if not path.exists():
        print(f"❌ File not found: {file_path}")
        return False

    content = path.read_text(encoding='utf-8')

    # Add imports if not present
    if "from sqlalchemy import" in content and "event" not in content:
        content = content.replace(
            "from sqlalchemy import",
            "from sqlalchemy import event,"
        )

    if "from app.core.utils import" not in content and "app.models.base import" in content:
        # Add import after base import
        content = content.replace(
            "from app.models.base import",
            "from app.models.base import"
        ) + "\nfrom app.core.utils import generate_slug\n"

    # Apply replacements
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
            print(f"  ✓ Replaced: {old[:50]}... → {new[:50]}...")

    # Add slug generator at end if provided
    if slug_generator and "def generate_" not in content:
        content += slug_generator
        print(f"  ✓ Added slug generation event listener")

    # Write back
    path.write_text(content, encoding='utf-8')
    return True


def main():
    """Main function to update all models"""
    print("=" * 60)
    print("UUID Migration - Model Update Script")
    print("=" * 60)

    success_count = 0
    fail_count = 0

    for file_path, replacements in MODEL_UPDATES.items():
        print(f"\n📝 Updating: {file_path}")
        slug_gen = SLUG_GENERATORS.get(file_path)

        if update_model_file(file_path, replacements, slug_gen):
            success_count += 1
        else:
            fail_count += 1

    print("\n" + "=" * 60)
    print(f"✅ Successfully updated: {success_count} files")
    print(f"❌ Failed: {fail_count} files")
    print("=" * 60)

    print("\n📋 Next Steps:")
    print("1. Review the changes in each file")
    print("2. Install dependencies: pip install unidecode")
    print("3. Drop and recreate databases")
    print("4. Generate new Alembic migrations")
    print("5. Run migrations: alembic upgrade head")


if __name__ == "__main__":
    main()
