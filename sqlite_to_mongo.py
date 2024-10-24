import os
import django
from pymongo import MongoClient

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_guide.settings')  # Adjust the path to your settings.py
django.setup()

from guide.models import District, Place, PlaceImage, Review, UserProfile

# MongoDB Connection Setup
MONGO_URI = 'mongodb://localhost:27017/'  # Replace with your MongoDB URI if different
MONGO_DB_NAME = 'guide'
MONGO_DISTRICT_COLLECTION = 'districts'
MONGO_PLACE_COLLECTION = 'places'
MONGO_PLACE_IMAGE_COLLECTION = 'place_images'
MONGO_REVIEW_COLLECTION = 'reviews'
MONGO_USER_PROFILE_COLLECTION = 'user_profiles'

def export_data_to_mongo():
    # Step 1: Connect to MongoDB
    client = MongoClient(MONGO_URI)
    mongo_db = client[MONGO_DB_NAME]

    # Get the collections
    district_collection = mongo_db[MONGO_DISTRICT_COLLECTION]
    place_collection = mongo_db[MONGO_PLACE_COLLECTION]
    place_image_collection = mongo_db[MONGO_PLACE_IMAGE_COLLECTION]
    review_collection = mongo_db[MONGO_REVIEW_COLLECTION]
    user_profile_collection = mongo_db[MONGO_USER_PROFILE_COLLECTION]

    # Step 2: Query Data from Django (SQLite) and export District data
    districts = District.objects.all()
    district_data = []
    for district in districts:
        data = {
            "name": district.name,
            "image": str(district.image),
            "slug": district.slug,
        }
        district_data.append(data)

    # Insert District data into MongoDB
    if district_data:
        district_collection.insert_many(district_data)
        print(f"Inserted {len(district_data)} districts into MongoDB")

    # Step 3: Query and export related `Place` data based on district
    for district in districts:
        places = Place.objects.filter(district=district)
        place_data = []
        for place in places:
            place_info = {
                "district": district.name,  # Include district name for reference
                "name": place.name,
                "description": place.description,
                "distance": place.distance,
                "best_time_to_visit": place.best_time_to_visit,
                "things_to_do": place.things_to_do,
                "entry_fee": place.entry_fee,
                "timings": place.timings,
                "how_to_reach": place.how_to_reach,
                "slug": place.slug
            }
            place_data.append(place_info)

        # Insert Place data into MongoDB
        if place_data:
            place_collection.insert_many(place_data)
            print(f"Inserted {len(place_data)} places for district {district.name}")

    # Step 4: Export PlaceImage data
    place_images = PlaceImage.objects.all()
    place_image_data = []
    for image in place_images:
        image_data = {
            "place": image.place.name,  # Assuming there's a ForeignKey to Place
            "image": str(image.image),
        }
        place_image_data.append(image_data)

    # Insert PlaceImage data into MongoDB
    if place_image_data:
        place_image_collection.insert_many(place_image_data)
        print(f"Inserted {len(place_image_data)} place images into MongoDB")

    # Step 5: Export Review data
    reviews = Review.objects.all()
    review_data = []
    for review in reviews:
        review_info = {
            "place": review.place.name,  # Assuming there's a ForeignKey to Place
            "user": review.user.username,  # Assuming there's a ForeignKey to UserProfile
            "rating": review.rating,
            "comments": review.comments,
            "created_at": review.created_at,
        }
        review_data.append(review_info)

    # Insert Review data into MongoDB
    if review_data:
        review_collection.insert_many(review_data)
        print(f"Inserted {len(review_data)} reviews into MongoDB")

    # Step 6: Export UserProfile data
    user_profiles = UserProfile.objects.all()
    user_profile_data = []
    for profile in user_profiles:
        profile_data = {
            "user": profile.user.username,          # Link to the user
            "profile_picture": str(profile.profile_picture),  # Profile picture (if any)
            "gender": profile.gender,                # User's gender
            "date_of_birth": profile.date_of_birth,  # User's date of birth
            "phone_number": profile.phone_number,    # User's phone number
        }
        user_profile_data.append(profile_data)

    # Insert UserProfile data into MongoDB
    if user_profile_data:
        user_profile_collection.insert_many(user_profile_data)
        print(f"Inserted {len(user_profile_data)} user profiles into MongoDB")


    # Close the MongoDB connection
    client.close()

# Run the export
if __name__ == "__main__":
    export_data_to_mongo()
