# Favorites list shared by 02 Student Data and All Favorites

import requests
import streamlit as st

# Dropdown labels
FEE_LOW = "Annual Student Fee (low → high)"
FEE_HIGH = "Annual Student Fee (high → low)"
NAME_AZ = "Name (A to Z)"
NAME_ZA = "Name (Z to A)"
SORT_OPTIONS = [FEE_LOW, FEE_HIGH, NAME_AZ, NAME_ZA]

def format_fees(value):
    """Format a fee like €1,234.56 per year."""
    if value is None:
        return "Est. fees unavailable"
    return f"€{value:,.2f} per year"


# Sort by name
def get_name(fav):
    name = fav.get("name")
    if name is None:
        name = ""
    return name.lower()


# Sort by annual student fees
def get_fees(fav):
    fees = fav.get("per_student_fees")
    if fees is None:
        fees = 0
    return fees


def sort_favorites(favorites, sort_choice):
    """Sort the favorites for the chosen dropdown option."""
    if sort_choice == FEE_LOW:
        return sorted(favorites, key=get_fees)
    if sort_choice == FEE_HIGH:
        return sorted(favorites, key=get_fees, reverse=True)
    if sort_choice == NAME_AZ:
        return sorted(favorites, key=get_name)
    if sort_choice == NAME_ZA:
        return sorted(favorites, key=get_name, reverse=True)
    return list(favorites)


def render_favorites(api, student_id, favorites, origin_page, key_prefix, limit=None):
    """Render the favorites list with a sort dropdown.

    """
    if not favorites:
        st.write("No favorites yet — star a university from your recommendations.")
        return

    sort_choice = st.selectbox("Sort", SORT_OPTIONS, key=key_prefix + "_sort")

    display = sort_favorites(favorites, sort_choice)
    if limit is not None:
        display = display[:limit]

    for i, fav in enumerate(display):
        # Separate each favorite
        if i > 0:
            st.divider()

        info_col, btn_col = st.columns([3, 1])

        with info_col:
            st.subheader(str(i + 1) + ". " + fav["name"])
            location = fav.get("location")
            if location is None:
                location = ""
            fees = format_fees(fav.get("per_student_fees"))
            if location:
                st.write(location + " | " + fees)
            else:
                st.write(fees)

        with btn_col:
            remove_clicked = st.button(
                "⭐ Remove", key=key_prefix + "_remove_" + str(fav["id"]),
                use_container_width=True,
            )
            if remove_clicked:
                requests.post(f"{api}/favorites/student/{student_id}/university/{fav['id']}", timeout=10)
                st.rerun()

            details_clicked = st.button(
                "ℹ️ Details", key=key_prefix + "_details_" + str(fav["id"]),
                use_container_width=True,
            )
            if details_clicked:
                st.session_state['selected_university_id'] = fav["id"]
                st.session_state['university_detail_origin'] = origin_page
                st.switch_page("pages/06_Student_Data_Unique_University_Info.py")
