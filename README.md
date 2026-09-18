# FaceAuth

A face authentication identity provider, built the way OAuth providers like Auth0 or Okta work, but using your face instead of a password.

## Overview

FaceAuth is an identity provider that lets other applications outsource login to it, similar to how many apps let you log in with Google or GitHub. Instead of a password, users authenticate with their face through a webcam. A client application redirects the user to FaceAuth, the user logs in there, and FaceAuth sends back an authorization code the client app can exchange for a token. The client app never sees or stores any face data.

The project includes the FaceAuth platform itself (backend and frontend), a developer portal for registering client applications, and a small demo client app called MyApp that shows the full flow working end to end.

This project was built to learn new technologies and get hands-on experience with full stack development and computer vision, covering everything from session management and OAuth-style authentication to implementing face recognition with classical computer vision models.

## Architecture

The project is made up of two separate applications:

**FaceAuth (the platform itself)**
- Backend: FastAPI, handles user accounts, face enrollment and matching, session management, and the OAuth-style authorize and token endpoints
- Frontend: React, provides the login and signup pages, the account dashboard, and a developer portal for registering and managing client applications

**MyApp (the demo client)**
- A small separate application with its own backend and frontend, used to demonstrate what it looks like for a third party app to integrate with FaceAuth
- Its backend holds the client secret and performs the code exchange with FaceAuth server to server
- Its frontend is a simple page that shows a Login button and, once authenticated, displays the logged in user's email and a log out button

The two applications run independently, on separate ports, and only communicate through the same kind of HTTP requests any real third party client would use to talk to FaceAuth.

## Features

- Face based login and signup, using webcam capture in the browser
- Password fallback for account recovery if face login fails
- Global user identity shared across all connected apps, so a user only enrolls their face once
- OAuth-style authorization flow, using redirect based login, authorization codes, and token exchange
- Account dashboard where users can view their account, re-enroll their face, and manage which third party apps they are connected to
- Ability to disconnect a connected app, revoking its access
- Developer accounts, separate from regular users, for registering and managing client applications
- Developer portal for creating, editing, and deleting registered applications, including client id and client secret management
- Audit logging of authentication attempts made through third party applications
- A working demo client application showing the full integration flow from a third party's perspective

## Tech stack

**Backend**
- Python, FastAPI
- SQLite for the database
- OpenCV for face detection and preprocessing, using the YuNet model
- Face embeddings generated using the SFace model
- NumPy for supporting computer vision work
- Pydantic for request and response validation

**Frontend**
- React with TypeScript
- Vite as the build tool and dev server

**MyApp (demo client)**
- FastAPI backend
- React with TypeScript frontend, also built with Vite

## How the auth flow works

1. A user clicks Login on a third party application (for example, MyApp)
2. The third party app redirects the user's browser to FaceAuth, including its client id and redirect URL
3. FaceAuth prompts the user to log in, either with their face via webcam or with their password
4. Once authenticated, FaceAuth generates a one time authorization code and redirects the user's browser back to the third party app's redirect URL, with the code attached
5. The third party app's backend takes that code and exchanges it directly with FaceAuth's backend, along with its client id and client secret, to prove it is a legitimate registered application
6. FaceAuth verifies the code and secret, then returns an access token to the third party app's backend
7. The third party app stores the token server side and uses it to identify the user, for example by calling FaceAuth's userinfo endpoint to get the user's email
8. The user is now logged into the third party app, without that app ever seeing the user's face data or password at any point

## Setup and installation

**Requirements**
- Python 3.10 or higher
- Node.js (LTS) and npm

### FaceAuth backend

1. Navigate to the backend directory

   ```bash
   cd backend
   ```

2. Create and activate a virtual environment

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies

   ```bash
   pip install -r requirements.txt
   ```

4. Run the server

   ```bash
   uvicorn app.main:app --reload
   ```

   Runs on port `8000` by default.

The FaceAuth backend has no required environment variables. All configuration lives in `config.py` with sensible defaults, including the database path and the paths to the ONNX face detection and embedding models.

### FaceAuth frontend

1. Navigate to the frontend directory

   ```bash
   cd frontend
   ```

2. Install dependencies

   ```bash
   npm install
   ```

3. Run the dev server

   ```bash
   npm run dev
   ```

   Runs on port `5173` by default.

### MyApp backend

1. Navigate to the MyApp backend directory

   ```bash
   cd myapp/backend
   ```

2. Uses the same virtual environment as the FaceAuth backend, so no separate install needed if it is already set up

3. Create a `.env` file with the following variables:

   ```
   CLIENT_ID=your_client_id
   CLIENT_SECRET=your_client_secret
   FACEAUTH_URL=http://localhost:8000
   ```

4. Run the server

   ```bash
   uvicorn main:app --reload --port 8001
   ```

### MyApp frontend

1. Navigate to the MyApp frontend directory

   ```bash
   cd myapp/frontend
   ```

2. Install dependencies

   ```bash
   npm install
   ```

3. Run the dev server

   ```bash
   npm run dev -- --port 5174
   ```

## Usage

Once all four servers are running (FaceAuth backend, FaceAuth frontend, MyApp backend, MyApp frontend):

1. Open the FaceAuth frontend (http://localhost:5173/) and sign up for a new account, enrolling your face through the webcam
2. Open MyApp's frontend (http://localhost:5174/) and click Login with FaceAuth
3. You will be redirected to FaceAuth, already logged in from the previous step, or prompted to log in again with your face if the session expired
4. After authenticating, you will be redirected back to MyApp, now showing you as logged in with your email
5. Back on the FaceAuth frontend, visit the account page to see MyApp listed as a connected app, with the option to disconnect any it

To register a new client application from scratch instead of using the existing MyApp setup:

1. Sign up for a developer account on the FaceAuth developer portal
2. Create a new application, providing a redirect URL
3. Note the generated client id and client secret, the secret is only shown once
4. Use these values in your own client application's integration with FaceAuth's authorize and token endpoints

## Project structure

```
FaceAuth/
  backend/
    app/
      core/
        config.py
        database.py
        dependencies.py
        face_models.py
        security.py
      models/
      routers/
      schemas/
      services/
      main.py

    ml_models/
      face_detection/
        face_detection_yunet.onnx
        face_recognition_sface.onnx

    scripts/
      test_face_detection.py
      test_face_embedding.py
      test_face_matching.py

    requirements.txt

  frontend/
    src/

  myApp/
    backend/
      main.py

    frontend/
      src/

  LICENSE
  README.md
```

## Known limitations

This is a personal learning project, built to explore full stack development and computer vision, not a production system. While it is functionally complete and demonstrates the full authentication flow end to end, it has not been created for real world use and should not be relied on as a secure, production ready identity provider.

## License

This project is licensed under the MIT License.
