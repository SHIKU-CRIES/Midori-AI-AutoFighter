# Midori AI AutoFighter

A web-based auto-battler game featuring strategic party management, elemental combat, and character progression.

## Quick Start with Docker Compose (Recommended)

The easiest way to run Midori AI AutoFighter is with Docker Compose. Choose one of the four variants below:

### Prerequisites

- Install [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)

### Option 1: Standard Version (Recommended for most users)

```bash
docker compose up --build frontend backend
```

**Access the game:** Open your web browser and go to `http://YOUR_SYSTEM_IP:59001`

### Option 2: AI-Enhanced Version with NVIDIA GPU Support

For users with NVIDIA graphics cards who want AI-powered chat features:

```bash
docker compose --profile llm-cuda up --build
```

**Access the game:** Open your web browser and go to `http://YOUR_SYSTEM_IP:59001`

### Option 3: AI-Enhanced Version with AMD GPU Support

For users with AMD graphics cards who want AI-powered chat features:

```bash
docker compose --profile llm-amd up --build
```

**Access the game:** Open your web browser and go to `http://YOUR_SYSTEM_IP:59001`

### Option 4: AI-Enhanced Version with CPU-Only Support

For users who want AI-powered chat features but don't have a compatible GPU:

```bash
docker compose --profile llm-cpu up --build
```

**Access the game:** Open your web browser and go to `http://YOUR_SYSTEM_IP:59001`

**Note:** Replace `YOUR_SYSTEM_IP` with your computer's IP address (usually `localhost` or `127.0.0.1` if running locally).

## Alternative Installation: Development Setup

If you prefer to run the game without Docker or want to modify the code:

### Prerequisites

Install the required tools:

```bash
# Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install bun (JavaScript package manager)
curl -fsSL https://bun.sh/install | bash
```

### Setup Steps

1. **Start the Backend** (in one terminal):
   ```bash
   cd backend
   uv run app.py
   ```

2. **Start the Frontend** (in another terminal):
   ```bash
   cd frontend
   bun install
   bun run dev
   ```

**Access the game:** Open your web browser and go to `http://YOUR_SYSTEM_IP:59001`

## Getting Help

- **Game Information:** See [ABOUTGAME.md](ABOUTGAME.md) for detailed game mechanics, features, and character information
- **Development:** See [DEVELOPMENT.md](DEVELOPMENT.md) for development environment setup
- **Building:** See [BUILD.md](BUILD.md) for building standalone executables
- **Issues:** Report bugs or request features on [GitHub Issues](../../issues)

## Download Prebuilt Versions

You can also download prebuilt executables from our [Releases page](../../releases) instead of running from source.
