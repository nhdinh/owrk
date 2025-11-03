"""
Seed Sample Data Script
Populates the database with sample data for Auth and Asset modules
"""

import requests
import json
from datetime import datetime, timedelta
import random

# API Base URLs
AUTH_API = "http://localhost:8000/api/v1/auth"
ASSET_API = "http://localhost:8000/api/v1/assets"

# Admin credentials
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin123"

# Global token storage
access_token = None


def print_section(title):
    """Print a section header"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")


def login_admin():
    """Login as admin and get access token"""
    global access_token
    print_section("Logging in as Admin")

    # Step 1: Login
    response = requests.post(f"{AUTH_API}/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })

    if response.status_code != 200:
        print(f"[FAIL] Login failed: {response.text}")
        return False

    temp_token = response.json().get("temp_token")
    print(f"[OK] Login successful, temp_token received")

    # Step 2: Verify OTP (using default OTP for testing)
    response = requests.post(f"{AUTH_API}/verify-otp", json={
        "temp_token": temp_token,
        "otp_code": "000000"
    })

    if response.status_code != 200:
        print(f"[FAIL] OTP verification failed: {response.text}")
        return False

    access_token = response.json().get("access_token")
    print(f"[OK] OTP verified, access_token received")
    return True


def get_headers():
    """Get headers with authorization token"""
    return {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }


def create_roles():
    """Create sample roles"""
    print_section("Creating Sample Roles")

    roles = [
        {
            "name": "asset_manager",
            "display_name": "Asset Manager",
            "description": "Can manage all assets and assignments",
            "permissions": ["asset:read", "asset:create", "asset:update", "asset:delete", "assignment:manage"]
        },
        {
            "name": "department_head",
            "display_name": "Department Head",
            "description": "Can view and manage department assets",
            "permissions": ["asset:read", "assignment:read"]
        },
        {
            "name": "employee",
            "display_name": "Employee",
            "description": "Can view own assigned assets",
            "permissions": ["asset:read"]
        }
    ]

    created_roles = []
    for role_data in roles:
        response = requests.post(
            f"{AUTH_API}/roles",
            headers=get_headers(),
            json=role_data
        )

        if response.status_code == 201:
            role = response.json()
            created_roles.append(role)
            print(f"[OK] Created role: {role['display_name']} (ID: {role['id']})")
        else:
            print(f"[WARN]  Role '{role_data['display_name']}' may already exist or failed: {response.status_code}")

    return created_roles


def create_users():
    """Create sample users"""
    print_section("Creating Sample Users")

    users = [
        {
            "email": "john.doe@example.com",
            "password": "password123",
            "full_name": "John Doe",
            "phone_number": "+1234567890",
            "department": "IT",
            "role_id": 2  # Will be updated with actual role ID
        },
        {
            "email": "jane.smith@example.com",
            "password": "password123",
            "full_name": "Jane Smith",
            "phone_number": "+1234567891",
            "department": "HR",
            "role_id": 3
        },
        {
            "email": "bob.johnson@example.com",
            "password": "password123",
            "full_name": "Bob Johnson",
            "phone_number": "+1234567892",
            "department": "Finance",
            "role_id": 3
        },
        {
            "email": "alice.williams@example.com",
            "password": "password123",
            "full_name": "Alice Williams",
            "phone_number": "+1234567893",
            "department": "IT",
            "role_id": 2
        },
        {
            "email": "charlie.brown@example.com",
            "password": "password123",
            "full_name": "Charlie Brown",
            "phone_number": "+1234567894",
            "department": "Operations",
            "role_id": 3
        }
    ]

    created_users = []
    for user_data in users:
        response = requests.post(
            f"{AUTH_API}/users",
            headers=get_headers(),
            json=user_data
        )

        if response.status_code == 201:
            user = response.json()
            created_users.append(user)
            print(f"[OK] Created user: {user['full_name']} ({user['email']}) - ID: {user['id']}")
        else:
            print(f"[WARN]  User '{user_data['email']}' may already exist: {response.status_code}")
            # Try to fetch existing user
            response = requests.get(f"{AUTH_API}/users", headers=get_headers())
            if response.status_code == 200:
                all_users = response.json()
                existing = next((u for u in all_users if u['email'] == user_data['email']), None)
                if existing:
                    created_users.append(existing)
                    print(f"   Using existing user ID: {existing['id']}")

    return created_users


def create_categories():
    """Create sample asset categories"""
    print_section("Creating Sample Asset Categories")

    categories = [
        {
            "code": "IT-HW",
            "name": "IT Hardware",
            "description": "Computer equipment and IT hardware",
            "is_active": True
        },
        {
            "code": "IT-SW",
            "name": "IT Software",
            "description": "Software licenses and subscriptions",
            "is_active": True
        },
        {
            "code": "FURN",
            "name": "Furniture",
            "description": "Office furniture and fixtures",
            "is_active": True
        },
        {
            "code": "VEH",
            "name": "Vehicles",
            "description": "Company vehicles",
            "is_active": True
        },
        {
            "code": "TOOLS",
            "name": "Tools & Equipment",
            "description": "Tools and specialized equipment",
            "is_active": True
        }
    ]

    created_categories = []
    for cat_data in categories:
        response = requests.post(
            f"{ASSET_API}/categories/",
            headers=get_headers(),
            json=cat_data
        )

        if response.status_code == 201:
            category = response.json()
            created_categories.append(category)
            print(f"[OK] Created category: {category['name']} ({category['code']}) - ID: {category['id']}")
        else:
            print(f"[WARN]  Category '{cat_data['code']}' may already exist: {response.status_code}")

    return created_categories


def create_assets(categories):
    """Create sample assets"""
    print_section("Creating Sample Assets")

    if not categories:
        print("[FAIL] No categories available. Skipping asset creation.")
        return []

    # Get category IDs
    it_hw_cat = next((c for c in categories if c['code'] == 'IT-HW'), categories[0])
    it_sw_cat = next((c for c in categories if c['code'] == 'IT-SW'), categories[0])
    furn_cat = next((c for c in categories if c['code'] == 'FURN'), categories[0])
    veh_cat = next((c for c in categories if c['code'] == 'VEH'), categories[0])
    tools_cat = next((c for c in categories if c['code'] == 'TOOLS'), categories[0])

    assets = [
        # IT Hardware
        {
            "name": "Dell Latitude 5520 Laptop",
            "asset_code": "LAP-001",
            "category_id": it_hw_cat['id'],
            "asset_type": "it_equipment",
            "description": "15.6\" FHD, i7-1165G7, 16GB RAM, 512GB SSD",
            "serial_number": "DL5520001",
            "purchase_date": "2023-01-15",
            "purchase_cost": 1299.99,
            "status": "available",
            "location": "IT Storage Room A",
            "depreciation_method": "straight_line",
            "useful_life_years": 4
        },
        {
            "name": "Dell Latitude 5520 Laptop",
            "asset_code": "LAP-002",
            "category_id": it_hw_cat['id'],
            "asset_type": "it_equipment",
            "description": "15.6\" FHD, i7-1165G7, 16GB RAM, 512GB SSD",
            "serial_number": "DL5520002",
            "purchase_date": "2023-01-15",
            "purchase_cost": 1299.99,
            "status": "in_use",
            "location": "IT Department",
            "depreciation_method": "straight_line",
            "useful_life_years": 4
        },
        {
            "name": "HP ProDesk 600 Desktop",
            "asset_code": "DT-001",
            "category_id": it_hw_cat['id'],
            "asset_type": "it_equipment",
            "description": "i5-10500, 8GB RAM, 256GB SSD",
            "serial_number": "HP600001",
            "purchase_date": "2023-03-20",
            "purchase_cost": 899.99,
            "status": "available",
            "location": "IT Storage Room B",
            "depreciation_method": "straight_line",
            "useful_life_years": 5
        },
        {
            "name": "LG 27\" Monitor",
            "asset_code": "MON-001",
            "category_id": it_hw_cat['id'],
            "asset_type": "it_equipment",
            "description": "27\" 4K UHD IPS Monitor",
            "serial_number": "LG27UHD001",
            "purchase_date": "2023-02-10",
            "purchase_cost": 399.99,
            "status": "in_use",
            "location": "Finance Department",
            "depreciation_method": "straight_line",
            "useful_life_years": 5
        },
        {
            "name": "Logitech Wireless Keyboard & Mouse",
            "asset_code": "ACC-001",
            "category_id": it_hw_cat['id'],
            "asset_type": "tool_equipment",
            "description": "MK850 Performance Wireless Keyboard and Mouse Combo",
            "serial_number": "LG-MK850-001",
            "purchase_date": "2023-04-05",
            "purchase_cost": 99.99,
            "status": "available",
            "location": "IT Storage",
            "depreciation_method": "straight_line",
            "useful_life_years": 3
        },
        # Furniture
        {
            "name": "Ergonomic Office Chair",
            "asset_code": "CHR-001",
            "category_id": furn_cat['id'],
            "asset_type": "furniture",
            "description": "Herman Miller Aeron Chair, Size B",
            "serial_number": "HM-AERON-001",
            "purchase_date": "2022-11-15",
            "purchase_cost": 1495.00,
            "status": "in_use",
            "location": "Executive Office",
            "depreciation_method": "straight_line",
            "useful_life_years": 10
        },
        {
            "name": "Standing Desk",
            "asset_code": "DSK-001",
            "category_id": furn_cat['id'],
            "asset_type": "furniture",
            "description": "Electric Height Adjustable Desk 60x30",
            "serial_number": "SD-E60-001",
            "purchase_date": "2023-01-20",
            "purchase_cost": 599.99,
            "status": "in_use",
            "location": "IT Department",
            "depreciation_method": "straight_line",
            "useful_life_years": 10
        },
        {
            "name": "Conference Table",
            "asset_code": "TBL-001",
            "category_id": furn_cat['id'],
            "asset_type": "furniture",
            "description": "8-Person Conference Table with Cable Management",
            "serial_number": "CT-8P-001",
            "purchase_date": "2022-09-01",
            "purchase_cost": 1299.00,
            "status": "available",
            "location": "Meeting Room A",
            "depreciation_method": "straight_line",
            "useful_life_years": 15
        },
        # Vehicles
        {
            "name": "Toyota Camry",
            "asset_code": "VEH-001",
            "category_id": veh_cat['id'],
            "asset_type": "vehicle",
            "description": "2022 Toyota Camry SE, Silver",
            "serial_number": "4T1B11HK5NU123456",
            "purchase_date": "2022-06-15",
            "purchase_cost": 28500.00,
            "status": "in_use",
            "location": "Parking Lot",
            "depreciation_method": "declining_balance",
            "useful_life_years": 8
        },
        # Tools
        {
            "name": "Cordless Drill Set",
            "asset_code": "TOOL-001",
            "category_id": tools_cat['id'],
            "asset_type": "tool_equipment",
            "description": "DeWalt 20V MAX Cordless Drill Combo Kit",
            "serial_number": "DW-20V-001",
            "purchase_date": "2023-05-10",
            "purchase_cost": 249.99,
            "status": "available",
            "location": "Maintenance Room",
            "depreciation_method": "straight_line",
            "useful_life_years": 5
        }
    ]

    created_assets = []
    for asset_data in assets:
        response = requests.post(
            f"{ASSET_API}/",
            headers=get_headers(),
            json=asset_data
        )

        if response.status_code == 201:
            asset = response.json()
            created_assets.append(asset)
            print(f"[OK] Created asset: {asset['name']} ({asset['asset_code']}) - ID: {asset['id']}")
        else:
            print(f"[WARN]  Asset '{asset_data['asset_code']}' may already exist: {response.status_code}")
            print(f"   Response: {response.text}")

    return created_assets


def create_assignments(assets, users):
    """Create sample asset assignments"""
    print_section("Creating Sample Assignments")

    if not assets or not users:
        print("[FAIL] No assets or users available. Skipping assignment creation.")
        return []

    # Filter assets that are marked as "in_use"
    in_use_assets = [a for a in assets if a.get('status') == 'in_use']

    if not in_use_assets:
        print("[WARN]  No 'in_use' assets found. Skipping assignments.")
        return []

    assignments = []
    today = datetime.now()

    # Assign some assets to users
    assignment_data = [
        {
            "asset_code": "LAP-002",
            "user_email": "john.doe@example.com",
            "days_ago": 30,
            "notes": "Primary work laptop for software development"
        },
        {
            "asset_code": "MON-001",
            "user_email": "jane.smith@example.com",
            "days_ago": 45,
            "notes": "Monitor for HR workstation"
        },
        {
            "asset_code": "CHR-001",
            "user_email": "admin@example.com",
            "days_ago": 60,
            "notes": "Executive office chair"
        },
        {
            "asset_code": "DSK-001",
            "user_email": "john.doe@example.com",
            "days_ago": 30,
            "notes": "Standing desk for IT department"
        },
        {
            "asset_code": "VEH-001",
            "user_email": "bob.johnson@example.com",
            "days_ago": 15,
            "notes": "Company vehicle for field work"
        }
    ]

    for assign_data in assignment_data:
        # Find asset and user
        asset = next((a for a in assets if a.get('asset_code') == assign_data['asset_code']), None)
        user = next((u for u in users if u.get('email') == assign_data['user_email']), None)

        if not asset:
            print(f"[WARN]  Asset {assign_data['asset_code']} not found")
            continue

        if not user:
            print(f"[WARN]  User {assign_data['user_email']} not found")
            continue

        assigned_date = (today - timedelta(days=assign_data['days_ago'])).strftime('%Y-%m-%d')

        assignment_payload = {
            "user_id": user['id'],
            "department_id": 1,  # Default department
            "assigned_date": assigned_date,
            "notes": assign_data['notes']
        }

        response = requests.post(
            f"{ASSET_API}/{asset['id']}/assign",
            headers=get_headers(),
            json=assignment_payload
        )

        if response.status_code == 201:
            assignment = response.json()
            assignments.append(assignment)
            print(f"[OK] Assigned {asset['asset_code']} to {user['full_name']} (ID: {assignment['id']})")
        else:
            print(f"[WARN]  Assignment failed for {asset['asset_code']}: {response.status_code}")
            print(f"   Response: {response.text}")

    return assignments


def main():
    """Main execution"""
    print_section("Sample Data Seeding Script")
    print("This script will populate the database with sample data")
    print("for Auth and Asset modules.\n")

    # Step 1: Login as admin
    if not login_admin():
        print("\n[FAIL] Failed to login. Exiting.")
        return

    # Step 2: Create roles
    roles = create_roles()

    # Step 3: Create users
    users = create_users()

    # Step 4: Create categories
    categories = create_categories()

    # Step 5: Create assets
    assets = create_assets(categories)

    # Step 6: Create assignments
    assignments = create_assignments(assets, users)

    # Summary
    print_section("Summary")
    print(f"[OK] Roles created: {len(roles)}")
    print(f"[OK] Users created: {len(users)}")
    print(f"[OK] Categories created: {len(categories)}")
    print(f"[OK] Assets created: {len(assets)}")
    print(f"[OK] Assignments created: {len(assignments)}")
    print("\n[SUCCESS] Sample data seeding completed!\n")
    print("You can now access the application with the following credentials:")
    print(f"  Admin: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
    print(f"  Users: john.doe@example.com / password123")
    print(f"         jane.smith@example.com / password123")
    print(f"         bob.johnson@example.com / password123")
    print(f"         alice.williams@example.com / password123")
    print(f"         charlie.brown@example.com / password123")
    print("\nAccess URLs:")
    print(f"  Auth Frontend: http://localhost:8000/auth/")
    print(f"  Asset Frontend: http://localhost:8000/assets/")
    print(f"  Categories: http://localhost:8000/assets/categories")
    print(f"  Assignments: http://localhost:8000/assets/assignments")


if __name__ == "__main__":
    main()
