import os
import streamlit.components.v1 as components
from typing import Optional, Callable, Any

# Create a _RELEASE constant to switch between development and production modes
_RELEASE = False

if not _RELEASE:
    _component_func = components.declare_component(
        "st_navigation_tile",
        url="http://localhost:3000",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend", "build")
    _component_func = components.declare_component("st_navigation_tile", path=build_dir)

def st_navigation_tile(
    title: str,
    body: str,
    url: Optional[str] = None,
    target: str = "_self",
    image_url: Optional[str] = None,
    key: Optional[str] = None,
    on_click: Optional[Callable[..., Any]] = None,
    *args,
    **kwargs,
) -> Optional[dict]:
    """
    A Streamlit component that displays a clickable navigation tile with a title, body, and optional image.
    
    Parameters
    ----------
    title : str
        The title text to display in the tile.
    body : str
        The body text to display in the tile. Supports HTML content.
    url : str, optional
        The URL to navigate to when the tile is clicked (if on_click is not provided).
    target : str, optional
        The target attribute for the URL ('_self', '_blank', '_parent', or '_top').
        Default is '_self'.
    image_url : str, optional
        The URL of an image to display at the top of the tile.
    key : str, optional
        An optional key that uniquely identifies this component.
    on_click : callable, optional
        A callback function that will be called when the tile is clicked.
        If provided, this will override the URL navigation.
    *args, **kwargs
        Additional arguments to pass to the on_click callback function.
        
    Returns
    -------
    dict or None
        Returns a dictionary with 'clicked': True when the tile is clicked,
        otherwise returns None.
    """
    # Handle the on_click callback
    click_callback = None
    if callable(on_click):
        def callback_wrapper(*args, **kwargs):
            def callback():
                return on_click(*args, **kwargs)
            return callback
        click_callback = callback_wrapper(*args, **kwargs)
    
    # Call the component function
    component_value = _component_func(
        title=title,
        body=body,
        url=url,
        target=target,
        image_url=image_url,
        key=key,
        on_click=click_callback is not None,
    )
    
    # Handle the click event
    if component_value and component_value.get('clicked') and click_callback:
        click_callback()
    
    return component_value
