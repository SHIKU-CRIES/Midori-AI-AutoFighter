FROM oven/bun:1

ENV ANDROID_SDK_ROOT=/opt/android-sdk

RUN apt-get update \
  && apt-get install -y openjdk-17-jdk unzip curl \
  && rm -rf /var/lib/apt/lists/* \
  && mkdir -p "$ANDROID_SDK_ROOT/cmdline-tools" \
  && curl -fsSL https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip -o /tmp/cli.zip \
  && unzip /tmp/cli.zip -d "$ANDROID_SDK_ROOT/cmdline-tools" \
  && yes | "$ANDROID_SDK_ROOT/cmdline-tools/cmdline-tools/bin/sdkmanager" --sdk_root="$ANDROID_SDK_ROOT" \
     "platform-tools" "platforms;android-34" "build-tools;34.0.0"

WORKDIR /workspace

COPY package.json bun.lock capacitor.config.ts ./
RUN bun install

# Copy and build web assets from frontend
COPY ../../frontend ../frontend
RUN bun run build:web

# Sync Capacitor files and build the Android project
RUN bun run sync

# Arguments for signing
ARG KEYSTORE_FILE=keystore.jks
ARG KEY_ALIAS=autofighter
ARG KEYSTORE_PASSWORD=password
ARG KEY_PASSWORD=password

# Copy keystore and build a signed release APK
COPY $KEYSTORE_FILE android/app/$KEYSTORE_FILE
RUN cd android \
  && ./gradlew assembleRelease \
  && cp app/build/outputs/apk/release/app-release.apk /workspace/app-release.apk

CMD ["/bin/bash"]
