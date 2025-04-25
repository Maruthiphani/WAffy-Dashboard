import streamlit as st
import json
import os

# === Paths ===
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "backend", "data", "business_config.json")

# === Constants ===
from configs.category_config import (
    DEFAULT_CATEGORIES,
    SUGGESTED_BY_TYPE,
    DEFAULT_PRIORITY_MAP
)

BUSINESS_TYPES = list(SUGGESTED_BY_TYPE.keys()) + ["Other"]
PRIORITY_LEVELS = ["high", "moderate", "low"]

# === Helpers ===
def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    return {}

def save_config(data):
    with open(CONFIG_PATH, "w") as f:
        json.dump(data, f, indent=2)
    st.success("Config saved successfully!")

# === Unified Form Renderer ===
def render_business_form(mode="create", business_id=None, config=None):
    is_edit = mode == "edit"
    existing = config.get(business_id, {}) if is_edit else {}

    st.subheader("Edit Business" if is_edit else "Create New Business")

    # --- Business ID / Name / Type ---
    if is_edit:
        st.text_input("Business ID", value=business_id, disabled=True)
    else:
        business_id = st.text_input("Business ID (e.g., b_404)").strip()
    
    name = st.text_input("Business Name", value=existing.get("name", ""))
    btype = st.selectbox("Business Type", BUSINESS_TYPES, index=BUSINESS_TYPES.index(existing.get("type", "Other")) if existing.get("type") in BUSINESS_TYPES else len(BUSINESS_TYPES)-1)
    
    if btype == "Other":
        btype = st.text_input("Enter custom business type", value=existing.get("type", ""))

    # --- Suggested Categories ---
    st.markdown("### Suggested Categories")
    default_suggested = DEFAULT_CATEGORIES + SUGGESTED_BY_TYPE.get(btype, [])
    selected_suggested = st.multiselect(
        "Select from Waffy + Type-based Suggestions",
        options=list(set(default_suggested)),
        default=existing.get("suggested_categories", [])
    )

    # --- Custom Categories ---
    st.markdown("### Custom Categories")

    if mode == "create":
        if "new_custom" not in st.session_state:
            st.session_state.new_custom = []

        new_cat = st.text_input("Add a custom category", placeholder="e.g. delivery_window").strip()
        if new_cat and new_cat not in st.session_state.new_custom:
            st.session_state.new_custom.append(new_cat)
            st.rerun()  # so it's reflected immediately

        custom_categories = st.session_state.new_custom
        if custom_categories:
            st.write("Added:")
            for cat in custom_categories:
                st.write(f"• {cat}")
        else:
            st.write("_No custom categories added yet._")

    else:
        # Edit mode – allow multiselect of existing
        custom_categories = st.multiselect(
            "Custom Categories",
            options=existing.get("custom_categories", []),
            default=existing.get("custom_categories", [])
        )

    # --- Priorities ---
    st.markdown("### Priorities")
    priorities = {}
    all_categories = selected_suggested + custom_categories
    for cat in all_categories:
        default_priority = (
            existing.get("priorities", {}).get(cat)
            or DEFAULT_PRIORITY_MAP.get(cat)
            or "moderate"
        )
        priorities[cat] = st.selectbox(
            f"Priority for '{cat}'",
            PRIORITY_LEVELS,
            index=PRIORITY_LEVELS.index(default_priority),
            key=f"priority_{cat}_{mode}"
        )

    # --- Save ---
    if st.button(" Save Business" if not is_edit else "💾 Update Business"):
        if not business_id or not name:
            st.warning(" Business ID and Name are required.")
            return

        if not is_edit and business_id in config:
            st.error(" Business ID already exists.")
            return

        config[business_id] = {
            "name": name,
            "type": btype,
            "suggested_categories": selected_suggested,
            "custom_categories": custom_categories,
            "priorities": priorities
        }
        save_config(config)

# === Main App ===
st.title("🏪 WAffy Business Category Manager")

config = load_config()

# Create label → ID mapping
business_labels = [" Create New"] + [f"{v['name']} ({k})" for k, v in config.items()]
business_id_lookup = {f"{v['name']} ({k})": k for k, v in config.items()}

selected_label = st.sidebar.selectbox("📋 Select a business", business_labels)

if selected_label == " Create New":
    render_business_form(mode="create", config=config)
else:
    selected_id = business_id_lookup[selected_label]
    render_business_form(mode="edit", business_id=selected_id, config=config)
