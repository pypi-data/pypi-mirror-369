import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scholr import get_scholar_profile, get_publication_details

profile_id = "your_profile_id"
profile_url = "your_profile_url"

def test_get_scholar_profile():
    profile = get_scholar_profile(profile_url)

    print("Profile basic information:")
    print(profile)

    return profile

def test_get_publication_details(publication_url):
    publication = get_publication_details(publication_url)
    print("Publication details:")
    print(publication)

if __name__ == "__main__":
    profile = test_get_scholar_profile()

    for pub in profile.get("publications", []):
        test_get_publication_details(pub.get("link"))
