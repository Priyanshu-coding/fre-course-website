import streamlit as st
import pandas as pd
from PIL import Image, ImageOps
import os
import base64  # For image encoding
from io import BytesIO  # To handle image-to-bytes conversion
from fuzzywuzzy import process  # For fuzzy matching

# Load data from CSV
file_path = 'free_courses_data.csv'  # Ensure the correct CSV file path
try:
    courses_data = pd.read_csv(file_path)
except FileNotFoundError:
    st.error(f"CSV file not found at: {file_path}")

# Load the Analytics Vidhya logo from the images folder in the project
logo_path = 'Images/analytics_vidhya_logo.jpeg'  # Correct folder name with capital "I"

# Function to resize image to equal size
def resize_image(image_path, size=(300, 300)):  # Set desired size for all images
    try:
        image = Image.open(image_path)
        resized_image = ImageOps.fit(image, size, Image.LANCZOS)  # Use LANCZOS for resizing
        return resized_image
    except FileNotFoundError:
        st.error(f"Image file not found at {image_path}")
        return None

# Function to convert image to base64 for displaying
def get_image_base64(image_path):
    try:
        img = Image.open(image_path)
        buffered = BytesIO()
        img.save(buffered, format="JPEG")  # Save as JPEG instead of PNG
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return img_str
    except FileNotFoundError:
        st.error(f"File not found at {image_path}")
        return ""

# Function to display categories with images and clickable category names
def display_categories_with_clickable_names():
    categories = courses_data['Category'].unique()

    # Create a layout for displaying categories in a grid (2 columns for simplicity)
    cols = st.columns(2)  # Create a 2-column layout

    # Display categories as image with clickable text below
    for i, category in enumerate(categories):
        with cols[i % 2]:  # Alternate between two columns
            # Path to the image file (assuming images are stored in .jpeg format)
            image_path = f'Images/{category}.jpeg'  # Ensure image files are named like categories

            # Check if the image exists
            if os.path.exists(image_path):
                # Resize and display the image
                resized_image = resize_image(image_path)
                if resized_image:  # Only display the image if resizing was successful
                    st.image(resized_image, use_column_width=True)  # Display image

                # Create a clickable button for the category name
                if category not in st.session_state.get('clicked_categories', []):
                    if st.button(category):  # Create a button with the category name
                        st.session_state.clicked_categories = st.session_state.get('clicked_categories', []) + [category]
                        st.session_state.selected_category = category  # Set the selected category in session state

            else:
                st.error(f"Image for {category} not found.")  # Show error if image not found

# Function to display courses under the selected category
def display_courses_in_category(category):
    # Applying the pink background color for the category page
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #F28D8C;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Adding a clickable "Back to All Courses" link at the top to return to the main page
    if st.button("Back to All Courses"):
        # Clear the selected category from session state
        st.session_state.selected_category = None

    st.markdown(f"## {category} Courses")
    courses_in_category = courses_data[courses_data['Category'] == category]
    for _, course in courses_in_category.iterrows():
        st.markdown(f"### [{course['Course Name']}]({course['Link']})")
        st.write(course['Description'])
    st.write("---")

# Improved search function without showing relevance scores
def search_courses(query):
    st.markdown("## Search Results")

    # Normalize the search query
    query = query.lower().strip()

    # Combine course names and descriptions to search in both fields
    course_names = courses_data['Course Name'].apply(str.lower).tolist()
    course_descriptions = courses_data['Description'].apply(str.lower).tolist()

    # Perform fuzzy matching on both course names and descriptions
    search_data = course_names + course_descriptions  # Combine both for search

    # We use `process.extract` to find the best matches, but we will ignore the score
    matches = process.extract(query, search_data, limit=10)  # Limit to top 10 matches

    # Track unique course names (avoid duplicates)
    unique_course_names = set()

    # Display search results without showing the score
    for match, _ in matches:  # The `_` ignores the score
        matched_rows = courses_data[
            (courses_data['Course Name'].str.lower() == match) |
            (courses_data['Description'].str.lower() == match)
            ]

        for _, course in matched_rows.iterrows():
            if course['Course Name'] not in unique_course_names:
                unique_course_names.add(course['Course Name'])
                st.markdown(f"### [{course['Course Name']}]({course['Link']})")
                st.write(course['Description'])
                st.write("---")

# Streamlit App Interface
def main():
    # Inject custom CSS to set the purple background for the main page
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #AA7CA7;
        }
        .logo {
            float: right;
            margin-right: 30px;
            margin-top: -40px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Title and logo together
    logo_base64 = get_image_base64(logo_path)  # Get the base64 encoded string for the logo
    if logo_base64:
        st.markdown(
            f"""
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h1>Analytics Vidhya Free Courses</h1>
                <img src="data:image/jpeg;base64,{logo_base64}" class="logo" width="150">
            </div>
            """,
            unsafe_allow_html=True
        )

    # Search Section
    query = st.text_input("Search for a course:")

    # Perform search if query is provided
    if query:
        search_courses(query)

    # Get the currently selected category from the session state
    selected_category = st.session_state.get('selected_category')

    # Show categories or all courses based on whether a category has been selected
    if not selected_category:
        # All Courses Section (formerly Categories)
        st.header("All Courses")
        display_categories_with_clickable_names()
    else:
        # If in a category, show only courses from that category
        display_courses_in_category(selected_category)

if __name__ == '__main__':
    # Ensure session state for category selection exists
    if 'selected_category' not in st.session_state:
        st.session_state['selected_category'] = None
    if 'clicked_categories' not in st.session_state:
        st.session_state['clicked_categories'] = []

    main()
