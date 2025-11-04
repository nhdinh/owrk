"""
Simple Sample Data Seeding Script
Populates with minimal sample data that works with current API
"""

import requests
import json
from datetime import datetime, timedelta

# API Base URLs
AUTH_API = "http://localhost:8000/api/v1/auth"
ASSET_API = "http://localhost:8000/api/v1/assets"

# Admin credentials
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin123"

# Global token storage
access_token = None
current_user_id = None


def login_admin():
    """Login as admin and get access token"""
    global access_token, current_user_id

    # Step 1: Login
    response = requests.post(
        f"{AUTH_API}/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )

    if response.status_code != 200:
        print(f"[FAIL] Login failed: {response.text}")
        return False

    temp_token = response.json().get("temp_token")
    print(f"[OK] Login successful")

    # Step 2: Verify OTP
    response = requests.post(
        f"{AUTH_API}/verify-otp", json={"temp_token": temp_token, "otp_code": "000000"}
    )

    if response.status_code != 200:
        print(f"[FAIL] OTP verification failed: {response.text}")
        return False

    data = response.json()
    access_token = data.get("access_token")
    current_user_id = data.get("user", {}).get("id", 1)
    print(f"[OK] OTP verified (User ID: {current_user_id})")
    return True


def get_headers():
    """Get headers with authorization token"""
    return {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }


def create_categories():
    """Create sample asset categories"""
    print("\n=== Creating Categories ===")

    categories = [
        {"code": "IT-HW", "name": "IT Hardware", "description": "Computer equipment"},
        {"code": "FURN", "name": "Furniture", "description": "Office furniture"},
        {"code": "VEH", "name": "Vehicles", "description": "Company vehicles"},
    ]

    created = []

    # First, try to get existing categories
    response = requests.get(f"{ASSET_API}/categories/", headers=get_headers())
    if response.status_code == 200:
        existing_cats = response.json()
        for cat_data in categories:
            existing = next(
                (c for c in existing_cats if c["code"] == cat_data["code"]), None
            )
            if existing:
                created.append(existing)
                print(f"[EXISTS] {existing['name']} (ID: {existing['id']})")
                continue

            # Create new
            cat_data["is_active"] = True
            response = requests.post(
                f"{ASSET_API}/categories/", headers=get_headers(), json=cat_data
            )
            if response.status_code == 201:
                category = response.json()
                created.append(category)
                print(f"[OK] {category['name']} (ID: {category['id']})")
            else:
                print(f"[WARN] {cat_data['code']}: {response.status_code}")

    return created


def create_assets(categories):
    """Create sample assets"""
    print("\n=== Creating Assets ===")

    if not categories:
        print("[FAIL] No categories")
        return []

    it_cat = next((c for c in categories if c["code"] == "IT-HW"), categories[0])
    furn_cat = next((c for c in categories if c["code"] == "FURN"), categories[0])

    assets = [
        {
            "asset_code": "LAP-001",
            "name": "Dell Laptop",
            "category_id": it_cat["id"],
            "asset_type": "FIXED_ASSET",
            "description": "Dell Latitude 5520",
            "serial_number": "DL001",
            "purchase_price": "1299.99",
            "purchase_date": "2023-01-15",
            "depreciation_method": "STRAIGHT_LINE",
            "useful_life_months": 48,
            "location": "IT Storage",
            "created_by": current_user_id,
        },
        {
            "asset_code": "LAP-002",
            "name": "HP Laptop",
            "category_id": it_cat["id"],
            "asset_type": "FIXED_ASSET",
            "description": "HP EliteBook 840",
            "serial_number": "HP001",
            "purchase_price": "1199.99",
            "purchase_date": "2023-02-10",
            "depreciation_method": "STRAIGHT_LINE",
            "useful_life_months": 48,
            "location": "IT Dept",
            "created_by": current_user_id,
        },
        {
            "asset_code": "CHR-001",
            "name": "Office Chair",
            "category_id": furn_cat["id"],
            "asset_type": "FIXED_ASSET",
            "description": "Ergonomic Chair",
            "serial_number": "CHR001",
            "purchase_price": "495.00",
            "purchase_date": "2022-11-15",
            "depreciation_method": "STRAIGHT_LINE",
            "useful_life_months": 120,
            "location": "Office",
            "created_by": current_user_id,
        },
        {
            "asset_code": "DSK-001",
            "name": "Standing Desk",
            "category_id": furn_cat["id"],
            "asset_type": "FIXED_ASSET",
            "description": "Electric Desk",
            "serial_number": "DSK001",
            "purchase_price": "599.99",
            "purchase_date": "2023-01-20",
            "depreciation_method": "STRAIGHT_LINE",
            "useful_life_months": 120,
            "location": "IT Dept",
            "created_by": current_user_id,
        },
        {
            "asset_code": "TOOL-001",
            "name": "Cordless Drill",
            "category_id": it_cat["id"],
            "asset_type": "TOOL",
            "description": "DeWalt 20V Drill",
            "serial_number": "DW001",
            "purchase_price": "249.99",
            "purchase_date": "2023-05-10",
            "location": "Maintenance",
            "created_by": current_user_id,
        },
    ]

    created = []
    for asset_data in assets:
        response = requests.post(
            f"{ASSET_API}/", headers=get_headers(), json=asset_data
        )

        if response.status_code == 201:
            asset = response.json()
            created.append(asset)
            print(f"[OK] {asset['asset_code']}: {asset['name']} (ID: {asset['id']})")
        else:
            print(f"[WARN] {asset_data['asset_code']}: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"      Error: {error_detail}")
            except:
                print(f"      Text: {response.text}")

    return created


def main():
    print("=" * 60)
    print("  Sample Data Seeding Script (Simple Version)")
    print("=" * 60)

    if not login_admin():
        print("\n[FAIL] Authentication failed")
        return

    categories = create_categories()
    assets = create_assets(categories)

    print("\n" + "=" * 60)
    print("  Summary")
    print("=" * 60)
    print(f"Categories: {len(categories)}")
    print(f"Assets: {len(assets)}")
    print("\n[SUCCESS] Sample data created!")
    print("\nAccess URLs:")
    print(f"  Assets: http://localhost:8000/assets/")
    print(f"  Categories: http://localhost:8000/assets/categories")
    print(f"  Assignments: http://localhost:8000/assets/assignments")


if __name__ == "__main__":
    main()
