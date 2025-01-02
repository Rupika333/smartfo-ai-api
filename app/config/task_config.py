task_config = {
    'Create New Job': {
        "description": "This task is used to initiate and set up a new job for an account. This is typically the first step in establishing a new service or project.",
        "required_fields": ['account_number', 'department', 'phone', 'pid'],
        "additional_fields": ['email'],
        "validation_fields": ['account_number'],
        "field_options": {
            'region': ['Great Lakes', 'Mid-South', 'Midwest', 'New York City', 'Northeast', 'Northwest', 'Southeast', 'Texas-Louisiana', 'West'],
            'management_area': ['Alabama-Georgia', 'Brooklyn-Queens', 'Central NY', 'Central TX-Louisiana', 'East Florida', 'Eastern NC', 'Eastern NY', 'Greenville-Tennessee', 'Hawaii', 'Kentucky', 'Manhattan', 'Michigan', 'Midwest Central', 'Midwest South', 'Minnesota-Wisconsin', 'Missouri', 'Mountain States', 'New England', 'North Texas', 'Northern Ohio', 'Pacific Northwest', 'Sierra Nevada', 'So Cal Central', 'So Cal North', 'So Cal South', 'South Carolina', 'South Texas', 'West Florida', 'Western NC', 'Western NY'],
            'department': ['RSC','ENTERPRISE'],
        }
    },
    'priority job create task': {
        "description": "This task is designed for creating high-priority jobs that need immediate attention or faster processing.",
        "required_fields": ['account_number', 'region', 'management_area', 'department', 'pid'],
        "additional_fields": ['phone', 'email'],
        "validation_fields": ['account_number', 'pid'],
        "field_options": {
            'region': ['Great Lakes', 'Mid-South', 'Midwest', 'New York City', 'Northeast', 'Northwest', 'Southeast', 'Texas-Louisiana', 'West'],
            'management_area': ['Alabama-Georgia', 'Brooklyn-Queens', 'Central NY', 'Central TX-Louisiana', 'East Florida', 'Eastern NC', 'Eastern NY', 'Greenville-Tennessee', 'Hawaii', 'Kentucky', 'Manhattan', 'Michigan', 'Midwest Central', 'Midwest South', 'Minnesota-Wisconsin', 'Missouri', 'Mountain States', 'New England', 'North Texas', 'Northern Ohio', 'Pacific Northwest', 'Sierra Nevada', 'So Cal Central', 'So Cal North', 'So Cal South', 'South Carolina', 'South Texas', 'West Florida', 'Western NC', 'Western NY'],
            'department': ['RSC','ENTERPRISE'],
        }
    },
    'priority job reassign': {
        "description": "This task allows for the reassignment of an existing priority job to a different team or individual.",
        "required_fields": ['account_number', 'region', 'management_area', 'phone', 'department', 'pid'],
        "additional_fields": ['email', 'pid'],
        "validation_fields": ['account_number', 'pid'],
        "field_options": {
            'region': ['Great Lakes', 'Mid-South', 'Midwest', 'New York City', 'Northeast', 'Northwest', 'Southeast', 'Texas-Louisiana', 'West'],
            'management_area': ['Alabama-Georgia', 'Brooklyn-Queens', 'Central NY', 'Central TX-Louisiana', 'East Florida', 'Eastern NC', 'Eastern NY', 'Greenville-Tennessee', 'Hawaii', 'Kentucky', 'Manhattan', 'Michigan', 'Midwest Central', 'Midwest South', 'Minnesota-Wisconsin', 'Missouri', 'Mountain States', 'New England', 'North Texas', 'Northern Ohio', 'Pacific Northwest', 'Sierra Nevada', 'So Cal Central', 'So Cal North', 'So Cal South', 'South Carolina', 'South Texas', 'West Florida', 'Western NC', 'Western NY'],
            'department': ['RSC','ENTERPRISE'],
        }
    }
}