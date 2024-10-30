import os
import django
import json
from pymongo import MongoClient
from django.core.management import call_command

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_guide.settings')  # your settings module path
django.setup()

# MongoDB Connection Setup
MONGO_URI = 'mongodb://localhost:27017/'  # your MongoDB URI 
MONGO_DB_NAME = 'guide'  # MongoDB database name
MONGO_COLLECTION_NAME = 'guide_data'  # Collection name where all data will be inserted

def dump_all_guide_data_to_json():
    # Define the output file
    output_file = 'guide_data.json'
    
    # Use Django's dumpdata command to export data from all models in the 'guide' app
    with open(output_file, 'w') as file:
        call_command('dumpdata', 'guide', indent=2, stdout=file)
    
    print(f"Data from all models in the 'guide' app has been dumped to {output_file}")

def insert_json_data_to_mongodb():
    # Step 1: Connect to MongoDB
    client = MongoClient(MONGO_URI)
    mongo_db = client[MONGO_DB_NAME]
    collection = mongo_db[MONGO_COLLECTION_NAME]

    # Step 2: Load the JSON data
    with open('guide_data.json', 'r') as file:
        data = json.load(file)
        
        # Step 3: Insert JSON data into MongoDB
        if data:
            collection.insert_many(data)
            print(f"Inserted {len(data)} records into MongoDB collection '{MONGO_COLLECTION_NAME}'")

    # Step 4: Close the MongoDB connection
    client.close()


if __name__ == "__main__":
    # Step 1: Dump all data from guide models to JSON
    dump_all_guide_data_to_json()
    
    # Step 2: Insert the JSON data into MongoDB
    insert_json_data_to_mongodb()










