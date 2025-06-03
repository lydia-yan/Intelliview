# Google Authentication Setup Guide

This guide will help you set up Google Authentication for the Mocker Flutter Web app.

## Prerequisites

- A Google account
- Access to Google Cloud Console
- Firebase project already created

## Step 0: Get Firebase Configuration (IMPORTANT)

### 0.1 Get Firebase Web App Config
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project: `mock-interview-app-2025`
3. Click the **gear icon** (Settings) → **Project settings**
4. Scroll down to **Your apps** section
5. If you don't have a web app, click **Add app** → Web (</>) icon
6. Register your app with nickname "Mocker Web"
7. Copy the **Firebase SDK configuration**

You'll see something like this:
```javascript
const firebaseConfig = {
  apiKey: "AIzaSyAxxxxxxxxxxxxx",
  authDomain: "mock-interview-app-2025.firebaseapp.com",
  projectId: "mock-interview-app-2025",
  storageBucket: "mock-interview-app-2025.firebasestorage.app",
  messagingSenderId: "3469018xxxxx",
  appId: "1:3469xxxx2089:web:4462xxxxxb9d5a8",
  measurementId: "G-RY4QxxxxD6"
};
```

### 0.2 Update firebase_options.dart
Your `lib/firebase_options.dart` should match these values:

```dart
static const FirebaseOptions web = FirebaseOptions(
  apiKey: 'YOUR_API_KEY_HERE',                    // from firebaseConfig.apiKey
  appId: 'YOUR_APP_ID_HERE',                      // from firebaseConfig.appId
  messagingSenderId: 'YOUR_SENDER_ID_HERE',       // from firebaseConfig.messagingSenderId
  projectId: 'YOUR_PROJECT_ID_HERE',              // from firebaseConfig.projectId
  authDomain: 'YOUR_AUTH_DOMAIN_HERE',            // from firebaseConfig.authDomain
  storageBucket: 'YOUR_STORAGE_BUCKET_HERE',      // from firebaseConfig.storageBucket
  measurementId: 'YOUR_MEASUREMENT_ID_HERE',      // from firebaseConfig.measurementId
);
```

**Replace all `YOUR_*_HERE` with the actual values you get from the Firebase Console.**

## Step 1: Enable Google APIs

### 1.1 Open Google Cloud Console
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project: `mock-interview-app-2025`

### 1.2 Enable Required APIs
Navigate to **APIs & Services** → **Library** and enable:
- **Google Sign-In API**
- **People API** (Required for user profile data)

Or use these direct links:
- [Enable Google Sign-In API](https://console.developers.google.com/apis/api/plus.googleapis.com)
- [Enable People API](https://console.developers.google.com/apis/api/people.googleapis.com)

## Step 2: Create OAuth 2.0 Credentials

### 2.1 Create Credentials
1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth 2.0 Client IDs**
3. Select **Web application**
4. Name: `Mocker Web App`

### 2.2 Configure Authorized Origins
Add these URLs to **Authorized JavaScript origins**:
- `http://localhost:3000` (for development)
- `http://localhost:8080` (Flutter default)
- `https://your-domain.com` (for production)

### 2.3 Configure Redirect URIs
Add these URLs to **Authorized redirect URIs**:
- `http://localhost:3000`
- `http://localhost:8080`
- `https://your-domain.com` (for production)

### 2.4 Save and Copy Client ID
After creation, you'll see your **Client ID**. It looks like:
```
34xxxxxxx12xx9-xxxxxxxxxxxxxxxxx.apps.googleusercontent.com
```

**⚠️ Important: This Client ID needs to be used in two places:**
1. `web/index.html` file
2. `lib/services/auth_service.dart` file

### 2.5 Find Your Existing Client ID (If Already Created)
If you already have a project, you can find the Client ID like this:
1. In Firebase Console → Authentication → Sign-in method → Google
2. Expand the Google provider
3. Copy the Client ID from **Web SDK configuration**

Or check existing OAuth 2.0 Client IDs in Google Cloud Console → APIs & Services → Credentials.

## Step 3: Configure Firebase Authentication

### 3.1 Enable Google Sign-In
1. Open [Firebase Console](https://console.firebase.google.com/)
2. Select your project: `mock-interview-app-2025`
3. Go to **Authentication** → **Sign-in method**
4. Enable **Google**
5. Enter your **Web SDK configuration** (Client ID from Step 2.4)
6. Save

## Step 4: Update Flutter App Configuration

### 4.1 Update index.html
Add this meta tag to `web/index.html` in the `<head>` section:
```html
<meta name="google-signin-client_id" content="YOUR_CLIENT_ID_HERE">
```

### 4.2 Update AuthService
In `lib/services/auth_service.dart`, update the GoogleSignIn configuration:
```dart
final GoogleSignIn _googleSignIn = GoogleSignIn(
  clientId: 'YOUR_CLIENT_ID_HERE',
  scopes: ['email', 'profile'],
);
```

Replace `YOUR_CLIENT_ID_HERE` with your actual Client ID from Step 2.4.

## Step 5: Test the Setup

### 5.1 Run the App
```bash
flutter run -d chrome --web-port=3000
```

### 5.2 Test Login Flow
1. Click "Sign in with Google"
2. Complete Google OAuth flow
3. Verify user is logged in
4. Test logout functionality

## Production Deployment

When deploying to production:

1. Add your production domain to OAuth configuration
2. Update Client ID in environment variables
3. Ensure HTTPS is enabled
4. Test the complete authentication flow

---

For more information, refer to:
- [Google Sign-In for Web](https://developers.google.com/identity/sign-in/web)
- [Firebase Authentication](https://firebase.google.com/docs/auth)
- [Flutter Google Sign-In Plugin](https://pub.dev/packages/google_sign_in) 