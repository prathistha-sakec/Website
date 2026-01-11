# 📱 Barcode Scanner Web Application with Login System

A Flask-based web application for student registration using barcode scanning technology with MongoDB integration, featuring secure login authentication and manual entry options.

## 🌟 Features

- **🔐 Secure Login System**: Authentication required to access the application
- **📱 Real-time Barcode Scanning**: Uses device camera for instant barcode detection
- **✋ Manual Student ID Entry**: Alternative entry method when scanning isn't possible
- **👥 Student Registration Management**: Automatic registration status updates
- **🗄️ MongoDB Integration**: Connects to MongoDB Atlas for data persistence
- **🔔 Pop-up Notifications**: Clear feedback for registration status
- **📱 Mobile-Friendly**: Responsive design for mobile devices
- **📊 Scan Logging**: Tracks all registration attempts (barcode and manual)
- **👤 Student Management**: View and manage student database
- **🔒 Session Management**: Secure user sessions with logout functionality

## � Default Login Credentials

**Username:** `admin`  
**Password:** `password123`

> ⚠️ **Security Note**: Change these credentials in production by setting the `ADMIN_USERNAME` and `ADMIN_PASSWORD` environment variables.

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **Database**: MongoDB Atlas
- **Frontend**: HTML5, CSS3, JavaScript
- **Computer Vision**: OpenCV, pyzbar
- **Deployment**: Render

## 📋 Prerequisites

- Python 3.11+
- MongoDB Atlas account
- Camera-enabled device for barcode scanning

## 🏗️ Local Development

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd Website
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file based on `.env.example`:
```bash
MONGODB_URL=your_mongodb_connection_string
DATABASE_NAME=Council
COLLECTION_NAME=students
SECRET_KEY=your-secret-key-here
ADMIN_USERNAME=admin
ADMIN_PASSWORD=password123
DEBUG=true
```

### 4. Run the Application
```bash
python app.py
```

Visit `http://localhost:5000` to access the application.

## 🌐 Deployment on Render

### Quick Deploy
1. Fork this repository
2. Connect to Render
3. Set environment variables
4. Deploy!

For detailed instructions, see [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md)

### Environment Variables for Production
```
ADMIN_USERNAME=admin
ADMIN_PASSWORD=password123
DEBUG=false
```

## 📱 Usage

### 🔐 Login Process
1. Navigate to the application URL
2. Enter login credentials:
   - **Username:** `admin`
   - **Password:** `password123`
3. Click "Login to Dashboard"

### 📱 For Students (Barcode Scanning)
1. After login, access the scanner page
2. Click "Start Auto Scan"
3. Point camera at student ID barcode
4. Registration status will be automatically updated

### ✋ Manual Entry Process
1. After login, click "Manual Entry" in navigation
2. Enter student ID in the text field
3. Click "Register Student"
4. View registration confirmation

### 👨‍💼 For Administrators
- **🏠 Scanner**: Main barcode scanning interface
- **✋ Manual Entry**: Manual student ID registration
- **👥 Students**: View all students and registration status
- **📊 Scan Logs**: Monitor all registration activity (barcode + manual)
- **🔒 API Access**: RESTful endpoints for integration
- **🚪 Logout**: Secure session termination

## 🔧 API Endpoints

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/login` | GET/POST | ❌ | Login page and authentication |
| `/logout` | GET | ✅ | Logout and clear session |
| `/` | GET | ✅ | Main scanning interface |
| `/manual_entry` | GET | ✅ | Manual student ID entry page |
| `/manual_register` | POST | ✅ | Process manual registration |
| `/students` | GET | ✅ | Student management page |
| `/scan_logs` | GET | ✅ | Scan history page |
| `/api/students` | GET | ✅ | Get all students (JSON) |
| `/api/scan_logs` | GET | ✅ | Get scan logs (JSON) |
| `/health` | GET | ❌ | Health check endpoint |

## 📊 Database Schema

### Students Collection
```json
{
  "_id": "ObjectId",
  "student_id": "124BTEX2008",
  "name": "John Doe",
  "email": "john.doe@example.com",
  "age": 25,
  "registration_status": false
}
```

### Scan Logs Collection
```json
{
  "_id": "ObjectId",
  "student_id": "124BTEX2008",
  "student_name": "John Doe",
  "status": "registered",
  "timestamp": "2025-08-17T10:30:00Z",
  "scan_type": "barcode" // or "manual"
}
```

### Users/Sessions Collection
```json
{
  "_id": "ObjectId",
  "username": "admin",
  "login_timestamp": "2025-08-17T09:00:00Z",
  "session_id": "flask_session_id"
}
```

## 🔒 Security Features

- **🔐 Login Authentication**: Required access control
- **🛡️ Session Management**: Secure Flask sessions
- **🔑 Environment Variable Configuration**: Secure credential storage
- **✅ Input Validation**: Form and API input sanitization
- **⚠️ Error Handling**: Graceful error management
- **🔒 HTTPS Enforced**: SSL/TLS in production
- **⏱️ MongoDB Connection Timeouts**: Prevents hanging connections
- **🎭 User Role Management**: Admin-only access control

## 🧪 Testing

Test the deployment:
```bash
python test_deployment.py https://your-app.onrender.com
```

## 🐛 Troubleshooting

### Common Issues

1. **Camera not working**
   - Ensure HTTPS is enabled
   - Grant camera permissions
   - Use supported browser (Chrome recommended)

2. **Database connection fails**
   - Check MongoDB URL and credentials
   - Verify network connectivity
   - Check MongoDB Atlas IP whitelist

3. **Barcode not detected**
   - Ensure good lighting
   - Keep barcode flat and clear
   - Try different angles

### Logs
- Check Render dashboard for application logs
- Monitor MongoDB Atlas for database activity
- Use `/health` endpoint for status checks

## 📈 Monitoring

- **Health Check**: `/health` endpoint
- **Performance**: Render dashboard metrics
- **Database**: MongoDB Atlas monitoring
- **Scan Activity**: Built-in scan logs

## 🔄 Updates

To update the deployed application:
1. Push changes to your repository
2. Render will automatically redeploy
3. Monitor deployment in Render dashboard

## 📞 Support

- **Issues**: Create GitHub issue
- **Documentation**: See RENDER_DEPLOYMENT.md
- **MongoDB**: [Atlas Documentation](https://docs.atlas.mongodb.com/)
- **Render**: [Render Documentation](https://render.com/docs)

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 🙏 Acknowledgments

- OpenCV for computer vision capabilities
- pyzbar for barcode decoding
- MongoDB Atlas for database hosting
- Render for deployment platform
