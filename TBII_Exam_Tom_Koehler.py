import streamlit as st
import random
import math

# === Session State Initialization ===
if "reroll_limit" not in st.session_state:
    st.session_state.reroll_limit = 3
if "reroll_count" not in st.session_state:
    st.session_state.reroll_count = 0
if "results" not in st.session_state:
    st.session_state.results = [None] * 8
if "luck" not in st.session_state:
    st.session_state.luck = ""
if "career_skill_points" not in st.session_state:
    st.session_state.career_skill_points = ""
if "free_skill_points" not in st.session_state:
    st.session_state.free_skill_points = ""
if "special_trait_results" not in st.session_state:
    st.session_state.special_trait_results = []
if "special_trait_text" not in st.session_state:
    st.session_state.special_trait_text = ""
if "monthly_wage" not in st.session_state:
    st.session_state.monthly_wage = ""

# --- Global Headline ---
st.title("Space Gothic Character Generator")
st.subheader("Mercenary Class")

# === Calculation Functions ===
def calculate_attributes():
    """Calculate the base attributes and reset rerolls & special traits."""
    st.session_state.reroll_count = 0
    st.session_state.special_trait_results = []
    st.session_state.special_trait_text = ""
    # Define attribute equations as lambdas for clarity.
    equations = [
        lambda: random.randint(4, 40) + 50,   # Strength
        lambda: random.randint(5, 50) + 40,   # Agility
        lambda: random.randint(5, 50) + 30,   # Willpower
        lambda: random.randint(3, 30) + 60,   # Endurance
        lambda: random.randint(6, 60) + 20,   # Luck (placeholder; will be recalculated)
        lambda: random.randint(3, 30) + 70,   # Experience
        lambda: random.randint(8, 80) + 40,   # Weight
        lambda: random.randint(5, 50) + 30    # Intelligence
    ]
    # Calculate and store the results.
    st.session_state.results = [eq() for eq in equations]
    # Recalculate Luck based on Willpower (index 2):
    st.session_state.luck = math.ceil(st.session_state.results[2] / 2 + 20 + random.randint(3, 30))
    # Calculate Career Skill Points and Free Skill Points:
    st.session_state.career_skill_points = math.ceil(3 * st.session_state.results[5])
    st.session_state.free_skill_points = math.ceil(st.session_state.results[5] + st.session_state.results[7])

def reroll_attribute(index):
    """Reroll a specific attribute (if within reroll limit) and update dependents."""
    if st.session_state.reroll_count < st.session_state.reroll_limit:
        equations = [
            lambda: random.randint(4, 40) + 50,
            lambda: random.randint(5, 50) + 40,
            lambda: random.randint(5, 50) + 30,
            lambda: random.randint(3, 30) + 60,
            lambda: random.randint(6, 60) + 20,
            lambda: random.randint(3, 30) + 70,
            lambda: random.randint(8, 80) + 40,
            lambda: random.randint(5, 50) + 30
        ]
        new_val = equations[index]()
        st.session_state.results[index] = new_val
        st.session_state.reroll_count += 1

        # If rerolling Willpower (index 2), update Luck.
        if index == 2:
            st.session_state.luck = math.ceil(st.session_state.results[2] / 2 + 20 + random.randint(3, 30))
        # If Experience (index 5) or Intelligence (index 7) change, update skill points.
        if index in [5, 7]:
            st.session_state.career_skill_points = math.ceil(3 * st.session_state.results[5])
            st.session_state.free_skill_points = math.ceil(st.session_state.results[5] + st.session_state.results[7])
    else:
        st.warning("Reroll limit reached!")

def roll_special_trait():
    """Roll and record a random special trait (if within reroll limit)."""
    if st.session_state.reroll_count < st.session_state.reroll_limit:
        traits = [
            "Greater Endurance", "Plasma Gunner", "Sharpshooter", "Sniper",
            "Sixth Sense", "Cyborg", "Combat Fatigue", "Greed",
            "Khirf Addiction", "Bully"
        ]
        trait = random.choice(traits)
        st.session_state.special_trait_results.append(trait)
        st.session_state.special_trait_text = "\n".join(st.session_state.special_trait_results)
        st.session_state.reroll_count += 1
    else:
        st.warning("Reroll limit reached!")

def roll_monthly_wage():
    """Calculate a random monthly wage."""
    st.session_state.monthly_wage = random.randint(3, 30) + 20

# === Page Functions ===
def attributes_page():
    st.title("Attributes & Rolls")
    # Button to (re)calculate all attributes
    if st.button("Calculate Attributes"):
        calculate_attributes()

    # Only display attributes if they have been calculated.
    if st.session_state.results and None not in st.session_state.results:
        attribute_names = ["Strength", "Agility", "Willpower", "Endurance",
                           "Luck (base)", "Experience", "Weight", "Intelligence"]
        for i, name in enumerate(attribute_names):
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                st.write(name)
            with col2:
                st.write(st.session_state.results[i])
            with col3:
                # Each attribute gets its own reroll button.
                if st.button(f"Reroll", key=f"reroll_{i}"):
                    reroll_attribute(i)
        st.markdown("---")
        st.write("**Computed Luck:**", st.session_state.luck)
        st.write("**Career Skill Points:**", st.session_state.career_skill_points)
        st.write("**Free Skill Points:**", st.session_state.free_skill_points)
        st.write(f"**Rerolls used:** {st.session_state.reroll_count} / {st.session_state.reroll_limit}")
    else:
        st.info("Click 'Calculate Attributes' to begin.")

    st.markdown("## Special Traits")
    if st.button("Roll Special Trait"):
        roll_special_trait()
    if st.session_state.special_trait_text:
        st.text(st.session_state.special_trait_text)

    st.markdown("## Monthly Wage")
    if st.button("Roll Monthly Wage"):
        roll_monthly_wage()
    if st.session_state.monthly_wage:
        st.write("Monthly Wage:", st.session_state.monthly_wage)

def inventory_page():
    st.title("Inventory & Attacking")
    st.write("Placeholder for Inventory and Attacking Script.")

# Initialize magazine bullet count in session_state if not already set
if "magazine" not in st.session_state:
    st.session_state.magazine = 15

# --- Weapon Stat Block ---
st.header("Weapon Stat Block: Luger .357 Automagnum")
st.write("**Damage:** 1d10+2")
st.write("**Range:** Short 20m / Medium 40m / Long 60m")
st.write("**Firerate:** 3")
st.write("**Burst:** 5")
st.write("**Magazine Size:** 15")

# --- Function to Display Magazine Graphically ---
def display_magazine():
    """
    Display a graphic strip representing the magazine:
    A filled block for each bullet left and an empty block for spent bullets.
    """
    bullets_left = st.session_state.magazine
    total_bullets = 15
    # Using emoji blocks: green square for a bullet and white square for an empty slot.
    filled = "🟩"
    empty = "⬜"
    magazine_display = filled * bullets_left + empty * (total_bullets - bullets_left)
    st.markdown("**Magazine:** " + magazine_display)

# Display the current magazine
display_magazine()

# --- Firing Mode Buttons ---
# Layout four buttons in a row
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("Single Fire"):
        # Single fire removes 1 bullet if available.
        if st.session_state.magazine >= 1:
            st.session_state.magazine -= 1
        else:
            st.warning("Out of bullets!")

with col2:
    if st.button("Normal Fire"):
        # Normal fire removes 3 bullets if available.
        if st.session_state.magazine >= 3:
            st.session_state.magazine -= 3
        else:
            st.warning("Not enough bullets for normal fire!")

with col3:
    if st.button("Burst Fire"):
        # Burst fire removes 5 bullets if available.
        if st.session_state.magazine >= 5:
            st.session_state.magazine -= 5
        else:
            st.warning("Not enough bullets for burst fire!")

with col4:
    if st.button("Reload"):
        # Reload resets the magazine to full.
        st.session_state.magazine = 15

# Display the updated magazine strip
display_magazine()

def personal_dossier_page():
    st.title("Personal Dossier of the Terran Security Archive")
    fields = [
        "Name", "Surname", "Gender", "Date of birth", "Place of birth",
        "Home Planet", "Hair Color", "Eye Color", "Height", "Weight",
        "Body Type", "Marital Status", "Age", "Handedness", "Religion",
        "Monthly Wage (Energy Units)", "Savings (Energy Units)", "Skillpoints",
        "Usual Whereabouts", "Educational Level", "Military Service", "Rank",
        "Unit", "Criminal Record", "Hobbies", "Miscellaneous Information"
    ]
    dossier = {}
    for field in fields:
        dossier[field] = st.text_input(field)
    st.markdown("### Your Entered Dossier")
    st.json(dossier)

# === Navigation via Sidebar ===
page = st.sidebar.radio("Navigate", ("Attributes", "Inventory/Attacking", "Personal Dossier"))

if page == "Attributes":
    attributes_page()
elif page == "Inventory/Attacking":
    inventory_page()
elif page == "Personal Dossier":
    personal_dossier_page()
