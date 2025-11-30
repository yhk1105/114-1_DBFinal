import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:8000"

def get_item_detail(token):
    print("\n=== Get Item Detail ===")
    try:
        i_id = input("Item ID: ").strip()
        if not i_id:
            print("Item ID is required.")
            return

        print(f"\nSending request to {BASE_URL}/item/{i_id}...")
        response = requests.get(f"{BASE_URL}/item/{i_id}", json={"token": token})

        print(f"Status Code: {response.status_code}")
        try:
            print("Response Body:")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        except:
            print(response.text)
    except Exception as e:
        print(f"Error: {e}")

def get_category_items():
    print("\n=== Get Category Items ===")
    try:
        c_id = input("Category ID: ").strip()
        if not c_id:
            print("Category ID is required.")
            return

        print(f"\nSending request to {BASE_URL}/item/category/{c_id}...")
        response = requests.get(f"{BASE_URL}/item/category/{c_id}", json={"c_id": c_id})

        print(f"Status Code: {response.status_code}")
        try:
            print("Response Body:")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        except:
            print(response.text)
    except Exception as e:
        print(f"Error: {e}")

def upload_item(token):
    print("\n=== Upload Item ===")
    try:
        name = input("Item Name: ").strip()
        description = input("Description: ").strip()
        out_duration = input("Out Duration (days): ").strip()
        c_id = input("Category ID: ").strip()
        
        if not name or not out_duration or not c_id:
            print("Name, Out Duration, and Category ID are required.")
            return

        payload = {
            "token": token,
            "i_name": name,
            "description": description,
            "out_duration": int(out_duration),
            "c_id": int(c_id),
            "status": "Not verified" # Default?
        }

        print(f"\nSending request to {BASE_URL}/item/upload...")
        response = requests.post(f"{BASE_URL}/item/upload", json=payload)

        print(f"Status Code: {response.status_code}")
        try:
            print("Response Body:")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        except:
            print(response.text)
    except Exception as e:
        print(f"Error: {e}")

def update_item(token):
    print("\n=== Update Item ===")
    try:
        i_id = input("Item ID: ").strip()
        if not i_id:
            print("Item ID is required.")
            return
            
        print("Leave fields empty to keep current value.")
        name = input("New Name: ").strip()
        description = input("New Description: ").strip()
        out_duration = input("New Out Duration: ").strip()
        status = input("New Status (Reservable/Not reservable): ").strip()
        c_id = input("New Category ID: ").strip()

        payload = {"token": token}
        if name: payload["i_name"] = name
        if description: payload["description"] = description
        if out_duration: payload["out_duration"] = int(out_duration)
        if status: payload["status"] = status
        if c_id: payload["c_id"] = int(c_id)

        print(f"\nSending request to {BASE_URL}/item/{i_id}...")
        response = requests.put(f"{BASE_URL}/item/{i_id}", json=payload)

        print(f"Status Code: {response.status_code}")
        try:
            print("Response Body:")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        except:
            print(response.text)
    except Exception as e:
        print(f"Error: {e}")

def main():
    token = input("Enter your JWT Token (from login): ").strip()
    if not token:
        print("Token is required.")
        return

    while True:
        print("\n=== Item CLI Menu ===")
        print("1. Get Item Detail")
        print("2. Get Category Items")
        print("3. Upload Item")
        print("4. Update Item")
        print("5. Exit")
        
        choice = input("Select an option: ").strip()
        
        if choice == "1":
            get_item_detail(token)
        elif choice == "2":
            get_category_items()
        elif choice == "3":
            upload_item(token)
        elif choice == "4":
            update_item(token)
        elif choice == "5":
            print("Exiting...")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
