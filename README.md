# 🎯 Intelliview - AI-Powered Interview Preparation Platform

<div align="center">

![Intelliview Logo](https://img.shields.io/badge/Intelliview-Interview%20AI-blue?style=for-the-badge&logo=robot)

**An intelligent platform that helps you ace your job interviews with AI-powered mock interviews and personalized feedback**

[![Flutter](https://img.shields.io/badge/Flutter-02569B?style=for-the-badge&logo=flutter&logoColor=white)](https://flutter.dev/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Firebase](https://img.shields.io/badge/Firebase-FFCA28?style=for-the-badge&logo=firebase&logoColor=black)](https://firebase.google.com/)
[![Google Cloud](https://img.shields.io/badge/Google%20Cloud-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white)](https://cloud.google.com/)

</div>

## 🚀 Features

### 📋 Interview Preparation
- **Smart Workflow Management**: Create and manage interview workflows for different positions
- **Resume Analysis**: Upload your PDF resume for AI-powered analysis and optimization suggestions  
- **Personalized Q&A**: Get tailored interview questions based on your background and target role
- **Resource Recommendations**: Access curated learning materials and preparation resources

### 🤖 AI-Powered Mock Interviews
- **Real-time Conversations**: Engage in natural conversations with AI interviewer via text or voice
- **Adaptive Questioning**: Dynamic follow-up questions based on your responses
- **Session Management**: Timed interview sessions with automatic transcript generation
- **Multi-modal Support**: Text and audio communication options

### 📊 Intelligent Feedback System
- **Comprehensive Analysis**: Detailed performance evaluation across multiple dimensions
- **Strength Recognition**: Highlight what you did well during the interview
- **Improvement Areas**: Specific suggestions with examples and actionable advice
- **Progress Tracking**: Monitor your improvement over multiple interview sessions
- **Resource Library**: Curated links to help you improve identified weak areas

### 📈 Interview History & Analytics
- **Session History**: Access all your past interview transcripts and feedback
- **Position-based Filtering**: Filter interviews by specific job positions
- **Performance Trends**: Track your progress across different interview sessions
- **Exportable Reports**: Download interview transcripts and feedback for review

## 🛠️ Tech Stack

### Frontend
- **Flutter Web** - Cross-platform UI framework for responsive web applications
- **Dart** - Programming language optimized for building user interfaces
- **Material Design** - Google's design system for consistent UI/UX

### Backend
- **FastAPI** - Modern, fast Python web framework for building APIs
- **Python 3.9+** - Core backend programming language
- **Google ADK** - Agent Development Kit for AI agent orchestration
- **WebSocket** - Real-time bidirectional communication

### AI & ML
- **Google Gemini 2.0** - Advanced language model for interview conversations
- **Google Cloud AI** - Cloud-based AI services and infrastructure

### Database & Storage
- **Firestore** - NoSQL document database for scalable data storage
- **Firebase Auth** - Authentication and user management

### DevOps & Deployment
- **Google Cloud Platform** - Cloud infrastructure and hosting
- **GitHub Actions** - CI/CD pipeline automation

## 📦 Installation & Setup

### Prerequisites
- **Flutter SDK** (3.0+)
- **Python** (3.9+)
- **Node.js** (16+)
- **Firebase Project** with Firestore and Authentication enabled
- **Google Cloud Project** with required APIs enabled

### 🔧 Backend Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/lydia-yan/Intelliview
   cd Intelliview
   ```

2. **Set up Python environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   Create a `.env` file in the `backend/` directory:
   
   ```bash
   # backend/.env
   GOOGLE_CLOUD_PROJECT=your-actual-project-id
   GOOGLE_CLOUD_LOCATION=us-central1
   GOOGLE_GENAI_USE_VERTEXAI=True
   ```

4. **Set up Firebase credentials**
   Create a `credentials` folder and put your `firebase_key.json` inside it

   ```bash
   FIREBASE_KEY_PATH=credentials/firebase_key.json #Or change it to your actual path of firebase_key.json
   ```

5. **Run the backend server**
   From the project root path
   ```bash
   uvicorn backend.app:app --reload --port 8000
   ```

### 🎨 Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend/mocker_web
   ```

2. **Install Flutter dependencies**
   ```bash
   flutter pub get
   ```

3. **Configure Firebase and Google Sign-In Client ID**
   - Add your `firebase_options.dart` file or change the ID and key to your own version in the existing `firebase_options.dart` file
   - Add your own Google Sign-In Client ID in `lib/services/auth_service.dart` and `web/index.html` file

4. **Run the web application**
   ```bash
   flutter run -d chrome --web-port 3000
   ```

## 📁 Project Structure

```
mocker/
├── backend/                    # Python FastAPI backend
│   ├── agents/                # AI agents (interviewer, judge)
│   ├── api/                   # REST API endpoints
│   ├── data/                  # Database models and schemas
│   ├── coordinator/           # Session management
│   └── service/              
├── frontend/                  # Flutter web frontend
│   └── mocker_web/
│       ├── lib/
│       │   ├── pages/         # UI pages/screens
│       │   ├── services/      # API service layer
│       │   ├── models/        # Data models
│       │   ├── widgets/       # Reusable UI components
│       │   └── config/        # App configuration
│       └── web/               # Web-specific assets
└── README.md                  # Project documentation
```

## 🎯 Usage

1. **Create Account**: Sign up using your email or social login
2. **Prepare Workflow**: Upload your resume and create a workflow for your target position
3. **Get Recommendation Q&A**: Review AI-generated interview questions tailored to your profile
4. **Practice Interview**: Start a mock interview session with our AI interviewer
5. **Receive Feedback**: Get detailed analysis and suggestions for improvement
6. **Track Progress**: Monitor your performance across multiple sessions

## 🔗 API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive API documentation powered by Swagger UI.

## 🤝 Contributing

We welcome contributions! 

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

If you have any questions or need help, please:
- 📧 Open an issue on GitHub
- 💬 Join our community discussions
- 📖 Check the documentation

---

<div align="center">

**Built with ❤️ using Flutter, Python, and Google AI**

⭐ Star this repo if you find it helpful!

</div>
