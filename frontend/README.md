# Customer Support Chat UI

A modern React-based chat interface for customer support, connected to the AI-powered backend.

## Features

- 💬 Real-time chat interface
- 🎨 Modern, responsive UI design
- 🔍 Automatic order number and email detection
- 📱 Mobile-friendly design
- ⚡ Fast and responsive

## Setup

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Configure API URL (optional):**
   Create a `.env` file in the `frontend` directory:
   ```
   VITE_API_URL=http://localhost:8100
   ```
   If not set, it defaults to `http://localhost:8000`

3. **Start the development server:**
   ```bash
   npm run dev
   ```

   The app will open at `http://localhost:3000`

## Usage

1. Make sure the backend API is running:
   ```bash
   python -m agent.api
   ```

2. Open the frontend in your browser

3. Start chatting! You can ask questions like:
   - "What's the status of my order #12345?"
   - "I need help with my recent order"
   - "Can you check my order status?"

## Building for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ChatWindow.jsx      # Main chat container
│   │   ├── MessageList.jsx     # Message list component
│   │   ├── Message.jsx          # Individual message component
│   │   ├── MessageInput.jsx     # Input field component
│   │   └── LoadingIndicator.jsx # Loading animation
│   ├── services/
│   │   └── api.js               # API service layer
│   ├── App.jsx                  # Main app component
│   ├── main.jsx                 # Entry point
│   └── index.css                # Global styles
├── index.html
├── package.json
└── vite.config.js
```

