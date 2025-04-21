import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "business_config.json")

def load_config():
    if not os.path.exists(CONFIG_PATH):
        print("Config file not found.")
        return {}
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def save_config(data):
    with open(CONFIG_PATH, "w") as f:
        json.dump(data, f, indent=2)
    print("Config updated and saved.")

def create_new_business(data):
    new_id = input("Enter new business ID (e.g., b_404): ").strip()
    if new_id in data:
        print("Business ID already exists!")
        return

    name = input("Enter business name: ").strip()
    btype = input("Enter business type (e.g., bakery, clinic, service): ").strip()

    DEFAULT_SUGGESTED = [
        "new_order", "order_status", "general_inquiry", "complaint",
        "return_refund", "follow_up", "feedback", "others"
    ]
    print("\nSelect suggested categories to include (type numbers separated by commas):")
    for idx, cat in enumerate(DEFAULT_SUGGESTED, start=1):
        print(f"  {idx}. {cat}")

    selection = input(" Your choices (e.g., 1,3,4,8): ")
    indices = [int(i.strip()) for i in selection.split(",") if i.strip().isdigit()]
    suggested = [DEFAULT_SUGGESTED[i - 1] for i in indices if 1 <= i <= len(DEFAULT_SUGGESTED)]

    if not suggested:
        print("No categories selected. Defaulting to all.")
        suggested = DEFAULT_SUGGESTED[:]

    custom_categories = []
    priorities = {cat: "moderate" for cat in suggested}  # init suggested with moderate

    print("\n🧩 Add any custom categories for this business (optional):")
    while True:
        new_cat = input(" Enter custom category (or press Enter to finish): ").strip()
        if not new_cat:
            break
        if new_cat in suggested or new_cat in custom_categories:
            print("Already added, skipping.")
            continue
        custom_categories.append(new_cat)
        priority = input(f"Set priority for '{new_cat}' [high/moderate/low]: ").lower().strip()
        if priority not in ["high", "moderate", "low"]:
            priority = "low"
        priorities[new_cat] = priority

    data[new_id] = {
        "name": name,
        "type": btype,
        "suggested_categories": suggested,
        "custom_categories": custom_categories,
        "priorities": {cat: "moderate" for cat in suggested}
    }

    print(f"\nBusiness '{name}' created.")
    save_config(data)

def add_custom_categories():
    data = load_config()
    if not data:
        return

    choice = input("\nDo you want to (1) update existing business or (2) create a new one? [1/2]: ").strip()

    if choice == "2":
        create_new_business(data)
        return

    print("\nAvailable businesses:")
    for bid, info in data.items():
        print(f"- {bid} → {info['name']} ({info['type']})")

    business_id = input("\nEnter Business ID: ").strip()
    if business_id not in data:
        print("Business ID not found.")
        return

    business = data[business_id]
    print(f"\nCurrent custom categories: {business.get('custom_categories', [])}")
    custom_categories = business.get("custom_categories", [])

    while True:
        new_cat = input("Enter new custom category (or press Enter to stop): ").strip()
        if not new_cat:
            break
        if new_cat in custom_categories:
            print("Already exists, skipping.")
            continue
        custom_categories.append(new_cat)

        # Set priority
        priority = input(f"Set priority for '{new_cat}' [high/moderate/low]: ").lower().strip()
        if priority not in ["high", "moderate", "low"]:
            priority = "low"
        if "priorities" not in business:
            business["priorities"] = {}
        business["priorities"][new_cat] = priority

    business["custom_categories"] = custom_categories
    save_config(data)

if __name__ == "__main__":
    add_custom_categories()
