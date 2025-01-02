from pymongo import MongoClient
from loguru import logger as log

# MongoDB connection string and initialization
connection_string = "mongodb://localhost:27017"
mclient = MongoClient(connection_string)

db = mclient['Charter']

collection_1 = db['accounts']
collection_2 = db['pid']

validation_fields = ['account_number', 'region', 'pid']

# Helper validation functions
def validate_account_number(field_value):
    # Validate account number in collection_1 (e.g., lookup in MongoDB)
    result = collection_1.find_one({"Account Number": int(field_value)})
    if result:
        return {
            "valid": True, 
            "message": f"Account number {field_value} validated successfully.", 
            "account_number": field_value
        }
    else:
        return {
            "valid": False, 
            "message": f"Invalid account number {field_value}.", 
            "account_number": field_value
        }

def validate_pid(field_value):
    # Validate PID in collection_2 (e.g., lookup in MongoDB)
    result = collection_2.find_one({"Pid": field_value})
    if result:
        return {
            "valid": True, 
            "message": f"PID {field_value} validated successfully.", 
            "pid": field_value
        }
    else:
        return {
            "valid": False, 
            "message": f"Invalid PID {field_value}.", 
            "pid": field_value
        }

# Initialize validation status as a dictionary
validation_status = {}

fields_one = {'account_number': '8245112850020695', 'department': 'RSC', 'phone': '1234567890', 'pid': 'P3206192', 'email': 'No Context'}

# Perform validation for the specified fields
for field in validation_fields:
    if field in fields_one:  # Ensure the field is present in the extracted fields
        field_value = fields_one[field]

    if field == "account_number":
                field_value = int(field_value)
                validation_status[field] = validate_account_number(field_value)
    elif field == "pid":
                validation_status[field] = validate_pid(field_value)

# Output the validation status
print(validation_status)
