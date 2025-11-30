import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:8000/auth"

def register():
    print("\n=== Register CLI ===")
    try:
        name = input("Name: ").strip()
        email = input("Email: ").strip()
        password = input("Password: ").strip()
        
        if not name or not email or not password:
            print("All fields are required.")
            return

        payload = {
            "name": name,
            "email": email,
            "password": password
        }

        print(f"\nSending request to {BASE_URL}/register...")
        response = requests.post(f"{BASE_URL}/register", json=payload)

        print(f"Status Code: {response.status_code}")
        
        try:
            data = response.json()
            print("Response Body:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            if response.status_code == 200:
                print("\nRegistration Successful!")
            else:
                print("\nRegistration Failed.")
                
        except json.JSONDecodeError:
            print("Response is not JSON:")
            print(response.text)

    except Exception as e:
        print(f"\nAn error occurred: {e}")

def login():
    print("\n=== Login CLI ===")
    try:
        email = input("Email: ").strip()
        password = input("Password: ").strip()
        login_as = input("Login as (member/staff) [default: member]: ").strip() or "member"
        
        if login_as not in ["member", "staff"]:
            print("Invalid login_as value. Must be 'member' or 'staff'.")
            return

        payload = {
            "email": email,
            "password": password,
            "login_as": login_as
        }

        print(f"\nSending request to {BASE_URL}/login...")
        response = requests.post(f"{BASE_URL}/login", json=payload)

        print(f"Status Code: {response.status_code}")
        
        try:
            data = response.json()
            print("Response Body:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            if response.status_code == 200:
                print("\nLogin Successful!")
                if "token" in data:
                    print(f"Token: {data['token']}")
            else:
                print("\nLogin Failed.")
                
        except json.JSONDecodeError:
            print("Response is not JSON:")
            print(response.text)

    except Exception as e:
        print(f"\nAn error occurred: {e}")

def main():
    while True:
        print("\n=== Auth CLI Menu ===")
        print("1. Login")
        print("2. Register")
        print("3. Exit")
        
        choice = input("Select an option: ").strip()
        
        if choice == "1":
            login()
        elif choice == "2":
            register()
        elif choice == "3":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled.")