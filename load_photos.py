
import os
import sys
import random

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def set_photo(photo):
    """ Sets the photo to be displayed based on the given photo name. """
    if os.path.exists(resource_path(os.path.join("photos", f"{photo}.png"))):
        return resource_path(os.path.join("photos", f"{photo}.png"))
    else:
        photos = os.listdir(resource_path(os.path.join("photos", "fallbacks")))
        return resource_path(os.path.join(os.path.join("photos", "fallbacks"), f"{random.choice(photos)}"))

def set_bg_photo():
    """ Sets the background photo to be displayed. """
    photos = os.listdir(resource_path(os.path.join("photos", "background")))
    return resource_path(os.path.join(os.path.join("photos", "background"), f"{random.choice(photos)}"))