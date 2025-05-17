# Alpha-Q

Alpha-Q is an advanced AI application builder with capabilities similar to Cursor and V0. It enables building both frontend and backend components for all programming languages and devices.

## Features

- **Natural Language & Voice AI**: Local text and voice processing
- **Persistent Memory**: Supabase DB or local DB + vector store
- **Full-Stack Code Creation**: Issue fixing and deployment for multiple languages
- **System Control & CLI Execution**: Via Python or Open Interpreter
- **Web Preview/Build/Deploy**: Local or remote via Vercel, Railway, etc.
- **Auth + GitHub Integration**: Automated repository management
- **Browser & Internet Automation**: Using Puppeteer/Playwright
- **Bitget Integration**: API + real trading capabilities
- **User-Centric Learning**: Context retention across sessions

## Tech Stack

- **Frontend**: Next.js, Tailwind CSS, Monaco Editor, Web APIs for STT/TTS
- **Backend**: Python (FastAPI), Node.js, Rust (for performance tasks)
- **AI Models**: 
  - Deepseek-Coder-33B-Instruct (via text-generation-webui)
  - Smaller fallback: WizardCoder-15B or CodeLlama-Instruct
- **Model Host**: text-generation-webui or LM Studio (no API keys)
- **Execution Agent**: Open Interpreter
- **Voice AI**: Whisper (STT), Coqui (TTS)
- **Memory/Storage**: Supabase (or SQLite for offline), Chroma for vector memory
- **Automation**: Puppeteer (Node), Playwright (Python)
- **Deployment**: Vercel, Railway, GitHub Actions

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Flask and other required packages (see installation)
- Supabase account and database

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/alpha-q.git
   cd alpha-q
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root directory with the following content:
   ```
   SUPABASE_URL=https://xxwrambzzwfmxqytoroh.supabase.co
   SUPABASE_ANON_KEY=your_anon_key
   SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
   JWT_SECRET=your_jwt_secret
   SESSION_SECRET=your_session_secret
   ```

4. Run the application:
   ```
   python main.py
   ```

5. Open a web browser and navigate to `http://localhost:5000`

## Deployment

This application is configured for easy deployment to Vercel. See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

## Project Structure

```
/alpha-q
├── app.py                 # Main Flask application
├── database.py            # Database configuration
├── config.py              # Application configuration
├── main.py                # Entry point
├── templates/             # HTML templates
│   ├── layout.html        # Base template
│   ├── index.html         # Main page
│   ├── success.html       # Success page
│   └── error.html         # Error page
├── static/                # Static assets
│   ├── css/               # CSS files
│   └── js/                # JavaScript files
├── .env                   # Environment variables
├── vercel.json            # Vercel deployment configuration
└── README.md              # Project documentation
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [Flask](https://flask.palletsprojects.com/)
- [Supabase](https://supabase.io/)
- [Bootstrap](https://getbootstrap.com/)
- [Font Awesome](https://fontawesome.com/)
- [Vercel](https://vercel.com/)