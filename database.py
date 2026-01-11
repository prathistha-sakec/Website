from pymongo import MongoClient
from datetime import datetime
import os
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import json

class StudentDatabase:
    def __init__(self):
        # MongoDB connection string - matches your existing setup
        self.connection_string = os.getenv('MONGODB_URL',)
        self.database_name = os.getenv('DATABASE_NAME')
        self.collection_name = os.getenv('COLLECTION_NAME')
        self.scan_logs_collection = 'scan_logs'
        
        # Google Sheets configuration
        self.sheet_id = os.getenv('GOOGLE_SHEET_ID')
        self.sheet_range = os.getenv('GOOGLE_SHEET_RANGE', 'Sheet1!A:F')  # Default range for student data
        self.google_credentials = None
        self.sheets_service = None
        
        # Initialize Google Sheets if credentials are available
        self._init_google_sheets()
        
        try:
            # Set connection timeout for production
            self.client = MongoClient(
                self.connection_string,
                serverSelectionTimeoutMS=5000,  # 5 second timeout
                connectTimeoutMS=10000,         # 10 second connection timeout
                socketTimeoutMS=10000           # 10 second socket timeout
            )
            self.db = self.client[self.database_name]
            self.students_collection = self.db[self.collection_name]
            self.scan_logs_collection = self.db[self.scan_logs_collection]
            
            # Test connection
            self.client.admin.command('ping')
            print("✅ Connected to MongoDB successfully!")
            
            # Create sample data if collection is empty (only in development)
            if os.getenv('DEBUG', 'false').lower() == 'true':
                self.create_sample_data()
            
        except Exception as e:
            print(f"❌ Error connecting to MongoDB: {e}")
            self.client = None
    
    def _init_google_sheets(self):
        """Initialize Google Sheets API connection"""
        try:
            # Try to load credentials from environment variable (JSON string)
            credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
            if credentials_json:
                credentials_dict = json.loads(credentials_json)
                self.google_credentials = Credentials.from_service_account_info(
                    credentials_dict,
                    scopes=['https://www.googleapis.com/auth/spreadsheets']
                )
                self.sheets_service = build('sheets', 'v4', credentials=self.google_credentials)
                print("✅ Connected to Google Sheets successfully!")
                return
            
            # Try to load from file (for local development)
            credentials_file = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
            if os.path.exists(credentials_file):
                self.google_credentials = Credentials.from_service_account_file(
                    credentials_file,
                    scopes=['https://www.googleapis.com/auth/spreadsheets']
                )
                self.sheets_service = build('sheets', 'v4', credentials=self.google_credentials)
                print("✅ Connected to Google Sheets successfully!")
                return
            
            print("⚠️ Google Sheets credentials not found. Sheet sync disabled.")
            
        except Exception as e:
            print(f"❌ Error connecting to Google Sheets: {e}")
            self.sheets_service = None
    
    def sync_from_google_sheet(self):
        """Sync student data from Google Sheet to MongoDB"""
        if not self.sheets_service or not self.sheet_id:
            print("⚠️ Google Sheets not configured. Skipping sync.")
            return False
        
        try:
            # Read data from sheet
            result = self.sheets_service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id,
                range=self.sheet_range
            ).execute()
            
            values = result.get('values', [])
            if not values:
                print("No data found in sheet.")
                return False
            
            # Assume first row contains headers
            headers = values[0]
            students_data = []
            
            for row in values[1:]:
                if len(row) >= len(headers):
                    student = {}
                    for i, header in enumerate(headers):
                        value = row[i] if i < len(row) else ""
                        
                        # Map common header names to our schema
                        if header.lower() in ['student_id', 'id', 'student id']:
                            student['student_id'] = value
                        elif header.lower() in ['name', 'student_name', 'full_name']:
                            student['name'] = value
                        elif header.lower() in ['email', 'email_address']:
                            student['email'] = value
                        elif header.lower() in ['age']:
                            student['age'] = int(value) if value.isdigit() else 0
                        elif header.lower() in ['competition', 'in_competition']:
                            student['competition'] = value.lower() in ['true', 'yes', '1', 'y']
                        elif header.lower() in ['registration_status', 'registered', 'status']:
                            student['registration_status'] = value.lower() in ['true', 'yes', '1', 'y', 'registered']
                    
                    if 'student_id' in student and student['student_id']:
                        students_data.append(student)
            
            # Update MongoDB with sheet data
            updated_count = 0
            for student in students_data:
                result = self.students_collection.update_one(
                    {'student_id': student['student_id']},
                    {'$set': student},
                    upsert=True
                )
                if result.modified_count > 0 or result.upserted_id:
                    updated_count += 1
            
            print(f"✅ Synced {updated_count} students from Google Sheet")
            return True
            
        except Exception as e:
            print(f"❌ Error syncing from Google Sheet: {e}")
            return False
    
    def sync_to_google_sheet(self, student_data):
        """Sync a single student update to Google Sheet"""
        if not self.sheets_service or not self.sheet_id:
            return False
        
        try:
            # First, get current sheet data to find the row
            result = self.sheets_service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id,
                range=self.sheet_range
            ).execute()
            
            values = result.get('values', [])
            if not values:
                return False
            
            headers = values[0]
            student_id = student_data.get('student_id')
            
            # Find the row with this student_id
            row_index = None
            for i, row in enumerate(values[1:], start=2):  # Start from row 2 (skip header)
                if len(row) > 0 and row[0] == student_id:
                    row_index = i
                    break
            
            # Prepare the row data based on headers
            row_data = []
            for header in headers:
                if header.lower() in ['student_id', 'id', 'student id']:
                    row_data.append(student_data.get('student_id', ''))
                elif header.lower() in ['name', 'student_name', 'full_name']:
                    row_data.append(student_data.get('name', ''))
                elif header.lower() in ['email', 'email_address']:
                    row_data.append(student_data.get('email', ''))
                elif header.lower() in ['age']:
                    row_data.append(str(student_data.get('age', '')))
                elif header.lower() in ['competition', 'in_competition']:
                    row_data.append('TRUE' if student_data.get('competition', False) else 'FALSE')
                elif header.lower() in ['registration_status', 'registered', 'status']:
                    row_data.append('TRUE' if student_data.get('registration_status', False) else 'FALSE')
                else:
                    row_data.append('')
            
            if row_index:
                # Update existing row
                range_name = f'Sheet1!A{row_index}:{chr(65 + len(headers) - 1)}{row_index}'
                body = {'values': [row_data]}
                
                self.sheets_service.spreadsheets().values().update(
                    spreadsheetId=self.sheet_id,
                    range=range_name,
                    valueInputOption='RAW',
                    body=body
                ).execute()
                
                print(f"✅ Updated student {student_id} in Google Sheet")
            else:
                # Append new row
                body = {'values': [row_data]}
                
                self.sheets_service.spreadsheets().values().append(
                    spreadsheetId=self.sheet_id,
                    range='Sheet1!A:A',
                    valueInputOption='RAW',
                    body=body
                ).execute()
                
                print(f"✅ Added new student {student_id} to Google Sheet")
            
            return True
            
        except Exception as e:
            print(f"❌ Error syncing to Google Sheet: {e}")
            return False

    def create_sample_data(self):
        """Create sample student data if collection is empty"""
        if self.students_collection.count_documents({}) == 0:
            sample_students = [
                {
                    "student_id": "124BTEX2008",
                    "name": "John Doe",
                    "age": 25,
                    "email": "john.doe@example.com",
                    "registration_status": True,
                    "competition": True
                },
                {
                    "student_id": "22UF17309EC077",
                    "name": "Sid",
                    "age": 25,
                    "email": "sid@example.com",
                    "registration_status": False,
                    "competition": False
                },
                {
                    "student_id": "23UF12345678EC076",
                    "name": "Jane Smith",
                    "age": 22,
                    "email": "jane.smith@example.com",
                    "registration_status": False,
                    "competition": True
                },
                {
                    "student_id": "123456789",
                    "name": "Bob Johnson",
                    "age": 21,
                    "email": "bob.johnson@example.com",
                    "registration_status": False,
                    "competition": False
                },
                {
                    "student_id": "987654321",
                    "name": "Alice Brown",
                    "age": 24,
                    "email": "alice.brown@example.com",
                    "registration_status": True,
                    "competition": True
                }
            ]
            
            self.students_collection.insert_many(sample_students)
            print(f"Created {len(sample_students)} sample student records")
    
    def verify_student(self, student_id, scan_type="barcode"):
        """Verify if student exists in database and update registration status"""
        if not self.client:
            return {"error": "Database connection not available"}
        
        try:
            # First, try to sync from Google Sheet to get latest data
            self.sync_from_google_sheet()
            
            student = self.students_collection.find_one({"student_id": student_id})
            
            if student:
                # Remove MongoDB ObjectId for JSON serialization
                student['_id'] = str(student['_id'])
                
                current_status = student.get('registration_status', False)
                
                if not current_status:
                    # Update registration status to True
                    updated_student = {**student, "registration_status": True}
                    
                    self.students_collection.update_one(
                        {"student_id": student_id},
                        {"$set": {"registration_status": True}}
                    )
                    
                    # Sync the update to Google Sheet
                    self.sync_to_google_sheet(updated_student)
                    
                    # Log the successful registration
                    self.log_scan(student_id, "registered", student.get('name'), scan_type)
                    
                    return {
                        "verified": True,
                        "student": updated_student,
                        "message": f"Registration completed for {student.get('name')}!",
                        "action": "registered",
                        "popup_message": f"✅ {student.get('name')} has been successfully registered!"
                    }
                else:
                    # Student already registered
                    self.log_scan(student_id, "already_registered", student.get('name'), scan_type)
                    
                    return {
                        "verified": True,
                        "student": student,
                        "message": f"{student.get('name')} is already registered",
                        "action": "already_registered",
                        "popup_message": f"ℹ️ {student.get('name')} is already registered!"
                    }
                
            else:
                # Log failed verification
                self.log_scan(student_id, "not_found", None, scan_type)
                
                return {
                    "verified": False,
                    "message": f"Student ID {student_id} not found in database",
                    "action": "not_found",
                    "popup_message": f"❌ Student ID {student_id} not found in database!"
                }
                
        except Exception as e:
            return {"error": f"Database error: {str(e)}"}
    
    def log_scan(self, student_id, status, student_name=None, scan_type="barcode"):
        """Log scan attempts to database"""
        if not self.client:
            return
        
        try:
            log_entry = {
                "student_id": student_id,
                "student_name": student_name,
                "status": status,  # "registered", "already_registered", "not_found", "error"
                "timestamp": datetime.now(),
                "scan_type": scan_type  # "barcode" or "manual"
            }
            
            self.scan_logs_collection.insert_one(log_entry)
            
        except Exception as e:
            print(f"Error logging scan: {e}")
    
    def get_scan_logs(self, limit=50):
        """Get recent scan logs"""
        if not self.client:
            return []
        
        try:
            logs = list(self.scan_logs_collection.find()
                       .sort("timestamp", -1)
                       .limit(limit))
            
            # Convert ObjectId to string for JSON serialization
            for log in logs:
                log['_id'] = str(log['_id'])
                
            return logs
            
        except Exception as e:
            print(f"Error getting scan logs: {e}")
            return []
    
    def get_all_students(self):
        """Get all students from database"""
        if not self.client:
            return []
        
        try:
            students = list(self.students_collection.find().sort("name", 1))
            
            # Convert ObjectId to string for JSON serialization
            for student in students:
                student['_id'] = str(student['_id'])
                
            return students
            
        except Exception as e:
            print(f"Error getting students: {e}")
            return []
    
    def add_student(self, student_data):
        """Add new student to database"""
        if not self.client:
            return {"error": "Database connection not available"}
        
        try:
            # Check if student ID already exists
            existing = self.students_collection.find_one({"student_id": student_data['student_id']})
            if existing:
                return {"error": f"Student ID {student_data['student_id']} already exists"}
            
            # Add timestamp
            student_data['created_at'] = datetime.now()
            
            result = self.students_collection.insert_one(student_data)
            return {"success": True, "id": str(result.inserted_id)}
            
        except Exception as e:
            return {"error": f"Error adding student: {str(e)}"}
    
    def close_connection(self):
        """Close database connection"""
        if self.client:
            self.client.close()
