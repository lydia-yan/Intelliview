# Firebase Authentication & Firestore Setup

This project uses **Firebase Admin SDK** for both:

- Firebase Authentication (to verify user ID tokens)
- Firestore Database (to store user profiles, workflows, and interviews)

Both services are initialized using the same Firebase service account key.
> **Note**: If you've already set up the database, **no additional steps are needed** here.

## Setup Instructions
1. Download the Firebase Admin SDK Key
   - Use the shared service account key already configured for this project.
   - Download it from this [Google Drive link](https://drive.google.com/drive/folders/1zJE616rPCja9FTuYRf2He_sUTzVAJQ0i?usp=sharing).
2. Save the key file locally
   - Create the `credentials` folder under the `backend/` directory
   - Place the file inside: `backend/credentials/firebase-key.json`
3. Update `.env`
   In the `backend/.env` file, add the following line:
   ```ini
   FIREBASE_KEY_PATH=credentials/firebase-key.json
   ```
4. You're all set!
Firebase will be initialized automatically when you run the app, using the shared key for both:
- Verifying tokens from the frontend (Auth)
- Reading and writing data (Firestore)

## If You Want to Set Up Firebase Auth Yourself
If you're starting from scratch or using your own Firebase project:

### Step-by-step to enable Firebase Auth (Google Login)
1. Go to the **Firebase Console**
2. Select your project (or create a new one)
3. In the left menu, go to **Build → Authentication**
4. Click **"Get Started"** to enable Authentication
5. Go to the **Sign-in method** tab
6. Enable **Google** as a provider (or any method you want to support log-in)
7. Set a project support email and save

Now your frontend app can authenticate users with Google and send the token to the backend for verification.