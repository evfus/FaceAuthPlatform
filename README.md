# FaceAuth - WIP

FaceAuth is a face authentication identity provider. It works like OAuth, but instead of a password screen, client apps redirect users to FaceAuth to log in with their face. FaceAuth handles the webcam capture and face matching, then sends back a short-lived auth code that the client app exchanges for an access token. The client app never sees or stores raw face data.

This is a work in progress. It's a personal project I'm building to learn how identity providers and applied computer vision work in practice. The backend auth flow and the face recognition pipeline are working end to end. The frontend and admin tooling are still being built.

How it works

A client app registers with FaceAuth and receives a client_id and client_secret
Users are redirected to FaceAuth to sign up with email and password, then enroll their face
On future logins, users authenticate with email and a face match, or password as a fallback
FaceAuth issues a single use auth code, which the client app exchanges server to server for an access token

Tech stack

Backend: Python, FastAPI, SQLite

Computer vision: OpenCV, using YuNet for face detection and SFace for face embeddings

Frontend: React with TypeScript