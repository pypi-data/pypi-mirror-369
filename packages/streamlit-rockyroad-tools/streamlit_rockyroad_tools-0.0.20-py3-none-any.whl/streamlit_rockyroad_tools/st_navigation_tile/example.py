
import os
import sys
import streamlit as st

# Get the absolute path to the parent directory (rockyroad_tools)
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Insert the path to the rockyroad_tools directory into sys.path
sys.path.insert(0, parent_dir)


def main():
    from streamlit_rockyroad_tools import st_navigation_tile
    st.set_page_config(page_title="Navigation Tile Demo", layout="wide")
    
    st.title("Navigation Tile Component Demo")
    
    # Example 1: Basic Usage
    st.header("1. Basic Usage")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st_navigation_tile(
            title="Dashboard",
            body="View your analytics dashboard with key metrics and insights.",
            url="#dashboard",
            image_url="https://placehold.co/600x400/png?text=Dashboard"
        )
    
    with col2:
        st_navigation_tile(
            title="Reports",
            body="Generate and view detailed reports with filtering options.",
            url="#reports",
            # image_url="https://placehold.co/600x400/png?text=Reports"
        )
    
    with col3:
        st_navigation_tile(
            title="Settings",
            body="Configure application settings and preferences.",
            url="#settings",
            image_url="https://placehold.co/600x400/png?text=Settings"
        )
    
    # Example 2: With Custom Click Handler
    st.header("2. With Custom Click Handler")
    
    if 'click_count' not in st.session_state:
        st.session_state.click_count = 0
    
    def handle_click():
        st.session_state.click_count += 1
    
    col1, col2 = st.columns(2)
    
    with col1:
        clicked = st_navigation_tile(
            title="Click Counter",
            body=f"This tile has been clicked {st.session_state.click_count} times.",
            on_click=handle_click,
            image_url="https://placehold.co/600x400/png?text=Click+Counter"
        )
    
    # Example 3: Opening in New Tab
    st.header("3. Opening in New Tab")
    
    st_navigation_tile(
        title="Documentation",
        body="Click to open our documentation in a new tab.",
        url="https://docs.example.com",
        target="_blank",
        image_url="https://placehold.co/600x400/png?text=Documentation"
    )
    
    # Example 4: Full Width Tile
    st.header("4. Full Width Tile")
    
    st_navigation_tile(
        title="Full Width Feature",
        body="This tile spans the full width of the container. It's great for highlighting important features or announcements.",
        url="#full-width-feature",
        image_url="https://placehold.co/600x400/png?text=Full+Width+Feature"
    )

if __name__ == "__main__":
    main()
