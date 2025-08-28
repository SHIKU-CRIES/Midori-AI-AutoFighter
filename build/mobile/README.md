# Mobile Client

This directory wraps the existing Svelte frontend with [Capacitor](https://capacitorjs.com) to produce an Android APK.

## Backend Strategy

The mobile app connects to a **remote backend server**. Start the backend from this repository and expose it on a reachable URL. Set `VITE_API_BASE` before building to point at that address; otherwise the app defaults to `http://localhost:59002`.

## Building

1. Install [Bun](https://bun.sh) and ensure Docker is available, or use the provided Dockerfile.
2. Generate a signing keystore:

   ```bash
   keytool -genkeypair -alias autofighter -keyalg RSA -keysize 2048 -validity 10000 -keystore keystore.jks
   ```

3. Build the APK inside Docker:

   ```bash
   docker build -f build/mobile/Dockerfile \
     --build-arg KEYSTORE_FILE=keystore.jks \
     --build-arg KEY_ALIAS=autofighter \
     --build-arg KEYSTORE_PASSWORD=your_password \
     --build-arg KEY_PASSWORD=your_password \
     -t autofighter-mobile build/mobile
   ```

   The resulting `app-release.apk` will appear in the build context root (`build/mobile/`).

## Running

Install the APK on a device or emulator:

```bash
adb install app-release.apk
```

The app serves the built frontend assets from `frontend/` and communicates with the backend using the URL supplied in `VITE_API_BASE`.
