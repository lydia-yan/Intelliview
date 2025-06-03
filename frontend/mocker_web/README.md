# Mocker - AI Mock Interview Platform (Frontend)

A Flutter Web application that provides AI-powered mock interview experiences for job seekers.

## Quick Start

### Prerequisites
- Flutter SDK (>=3.0.0)
- Chrome/Edge browser
- Firebase account
- Google Cloud Console access

### Installation
```bash
# Clone the repository
git clone https://github.com/lydia-yan/Mocker
cd frontend/mocker_web

# Install dependencies
flutter pub get

# Run the application
flutter run -d chrome --web-port=3000
```

## 🏗️ Architecture Overview

### **Design Pattern**
- **Provider Pattern**: State management using `provider` package
- **Service Layer**: Separation of business logic and UI
- **Repository Pattern**: Data access through service classes
- **Component-Based**: Reusable widgets and modular design

### **Project Structure**
```
lib/
├── config/          # API endpoints and configuration
├── data/            # Mock data and constants
├── models/          # Data models and entities
├── pages/           # UI screens and pages
├── services/        # Business logic and API calls
├── theme/           # App theme and styling
├── widgets/         # Reusable UI components
└── main.dart        # Application entry point
```

### **Key Technologies**
- **Flutter Web**: Cross-platform web framework
- **Firebase Auth**: User authentication
- **Google Sign-In**: OAuth integration
- **WebSocket**: Real-time interview communication
- **Provider**: State management
- **HTTP**: REST API communication

## 🎨 UI/UX Design

### **Design System**
- **Color Scheme**: Professional blue-gray palette
- **Typography**: Google Fonts with consistent hierarchy
- **Layout**: Responsive grid system with sidebar navigation
- **Components**: Material Design 3 with custom styling

### **Color Palette**
```dart
// Primary Colors
primaryBlue: #2563EB      // Main action color
lightBlue: #E6F0FF        // Selection backgrounds
darkGray: #1F2937         // Text and buttons
mediumGray: #6B7280       // Secondary text
lightGray: #F9FAFB        // Page backgrounds
surfaceWhite: #FFFFFF     // Card backgrounds
borderGray: #E5E7EB       // Borders and dividers
```

## 📱 Core Features

### **1. Authentication System**
- Google OAuth integration
- Firebase authentication
- Automatic user initialization
- Session management

### **2. Interview Preparation**
- Resume upload (PDF)
- Professional links management
- Job description analysis
- AI-powered preparation tips

### **3. Mock Interview Engine**
- Real-time WebSocket communication
- AI interviewer conversations
- Session management
- Interview recording

### **4. Q&A Management**
- Workflow-based questions
- Tag-based filtering
- Review/Quiz modes
- Interactive answer display

### **5. Feedback System**
- Comprehensive interview analysis
- Performance metrics
- Improvement suggestions
- Resource recommendations

### **6. User Profile**
- Profile management
- Avatar upload
- Social links integration
- Personal information

## Testing Guide

### **Development Testing**

#### **1. Local Development**
```bash
# Run with hot reload
flutter run -d chrome --web-port=3000
```

#### **2. Authentication Testing**
```bash
# Test Google Sign-In flow
1. Navigate to localhost:3000
2. Click "Sign in with Google"
3. Complete OAuth flow
4. Verify user profile data
5. Test logout functionality
```

#### **3. API Integration Testing**
- **Mock Fallback**: Automatic fallback to mock data when APIs fail
- **Error Handling**: Test network failures and API errors
- **Token Management**: Verify JWT token refresh and validation

### **Feature Testing**

#### **1. Interview Preparation**
```
Test Cases:
✓ Resume upload (PDF validation)
✓ Success/error message display
```

#### **2. Mock Interview**
```
Test Cases:
✓ Workflow selection
✓ WebSocket connection establishment
✓ Real-time message exchange
✓ Interview termination
✓ Feedback generation
```

#### **3. Q&A System**
```
Test Cases:
✓ Workflow filtering
✓ Tag-based search
✓ Mode switching (Review/Quiz)
✓ Answer expansion/collapse
✓ Content loading states
```

## Future Deployment

### **Build for Production**
```bash
# Build web application
flutter build web --release

# Build with custom base href
flutter build web --base-href="/app/"
```

### **Environment Configuration**
```dart
// Environment-specific settings
const bool isProduction = bool.fromEnvironment('PRODUCTION');
const String apiBaseUrl = String.fromEnvironment('API_BASE_URL');
```

### **Firebase Deployment**
```bash
# Install Firebase CLI
npm install -g firebase-tools

# Deploy to Firebase Hosting
firebase deploy --only hosting
```

## 🔒 Security Considerations

### **Authentication**
- JWT token validation
- Secure OAuth flow
- Session timeout handling
- Cross-site scripting prevention

### **Data Protection**
- Client-side input validation
- Sensitive data encryption
- Secure API communication
- User privacy compliance

### **API Security**
- Authorization headers
- Request rate limiting
- Error message sanitization
- CORS configuration

## 📚 Additional Resources

- [Flutter Documentation](https://docs.flutter.dev/)
- [Firebase Documentation](https://firebase.google.com/docs)
- [Google Sign-In Setup](./GOOGLE_AUTH_SETUP.md)
- [Material Design 3](https://m3.material.io/)

---