import csv
import pymongo
from sys import argv
from models import Dataset, DatasetStatus
from datetime import datetime

# Connect to MongoDB
client = pymongo.MongoClient('localhost', 27017)
db = client.dashboard
collection = db.datasets

collection.delete_many({})

# Open the CSV file
with open(argv[1], 'r') as csvfile:
    reader = csv.DictReader(csvfile)

    # Iterate over the CSV file and insert the data into MongoDB
    for row in reader:
        row['title'] = row['title'].replace('/', '|')
        dataset = Dataset(
            title=row['title'],
            description=row.get('description', ''),
            doi=row.get('doi', None),
            origins_doi=[row.get('origins_doi')],
            requester_name=row.get('requester_name', 'admin'),
            requester_email=row.get('requester_email', 'admin'),
            date=datetime.strptime(row.get('date', datetime.now().strftime('%d/%M/%Y')), '%d/%M/%Y'),
            status=DatasetStatus.DONE,
            report={
                'classes': row.get('classes'),
                'original_samples': {
                    'class_1': row.get('class_1'),
                    'class_2': row.get('class_2'),
                    'class_n': row.get('class_n')
                },
                'sampling_limit': row.get('sampling_limit'),
                'analyzed_samples': row.get('analyzed_samples'),
                'features': row.get('features'),
                'duplicated_feature_vectors': row.get('duplicated_feature_vectors'),
                'na_values': row.get('na_values'),
                'redundancy': row.get('redundancy'),
                'association': row.get('association'),
                'similarity': row.get('similarity'),
            },
            metadata="This dataset was tested locally."
        )

        # Check if the document already exists in MongoDB
        document = collection.find_one({'title': row['title']})

        # If the document exists, update it
        if document:
            collection.update_one(document, {'$set': dataset.to_dict()})

        # Otherwise, insert the document
        else:
            collection.insert_one(dataset.to_dict())

print('Data imported successfully!')