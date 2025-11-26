# SecureBank Fraud Alert - AI-Powered Voice Agent

**Day 6 Challenge - Fraud Detection & Verification System**

An intelligent fraud detection voice agent for SecureBank that contacts customers about suspicious transactions, verifies their identity through security questions, and updates case status based on customer confirmation. Built with LiveKit Agents and Murf Falcon TTS for ultra-fast voice interactions.

## About This Project

Part of the **#MurfAIVoiceAgentsChallenge** by [murf.ai](https://murf.ai), this project demonstrates how AI voice agents can handle real-time fraud detection calls, verify customer identity, present transaction details, and resolve fraud cases through natural conversation.

### Key Features

- 🛡️ **Fraud Detection Bot** - AI agent contacts customers about suspicious activity
- 🔐 **Identity Verification** - Security question-based customer authentication
- 💳 **Transaction Review** - Presents detailed transaction information for confirmation
- 💾 **Case Management** - SQLite database tracks fraud case status and outcomes
- ⚡ **Real-time Updates** - Case status updates based on customer responses
- 💬 **Natural Conversation** - Voice-first interaction with text chat support
- 🚀 **Lightning Fast** - Powered by Murf Falcon TTS (fastest TTS API)

## Repository Structure

```
Day_6_Fraud_Alert/
├── backend/              # Python fraud detection agent
│   ├── src/
│   │   └── agent.py      # Main fraud alert agent with verification
│   ├── init_fraud_db.py  # Database initialization script
│   └── fraud_cases.db    # SQLite database with fraud cases
├── frontend/             # Next.js UI with SecureBank branding
├── start_app.ps1         # Windows startup script
├── start_app.sh          # Unix/Mac startup script
└── README.md             # This file
```

### Backend

The fraud detection voice agent built with LiveKit Agents framework.

**Technologies:**

- **TTS**: Murf Falcon (ultra-fast voice synthesis)
- **STT**: Deepgram Nova-3
- **LLM**: Google Gemini 2.5-flash
- **VAD**: Silero (turn detection)
- **Database**: SQLite

**Agent Tools:**

- `load_fraud_case(username)` - Retrieves pending fraud case from database
- `verify_customer(customer_answer)` - Validates security question answer
- `update_fraud_case(customer_made_transaction)` - Updates case status (safe/fraud)

**Database Schema:**
- Stores customer username, security Q&A, card details, transaction info
- Tracks case status: `pending_review`, `confirmed_safe`, `confirmed_fraud`, `verification_failed`
- Records outcome notes and timestamps

[→ Backend Documentation](./backend/README.md)

### Frontend

Next.js 15 application with real-time voice and chat interface.

**Features:**

- Real-time voice interaction with LiveKit
- Live chat transcript for conversation tracking
- SecureBank branding (blue accent, security-focused design)
- Audio visualization and controls
- "Connect to Fraud Department" CTA button
- Responsive, accessible UI
- Professional banking interface

**Customization:**
- Branding configured in `app-config.ts`
- Landing page highlights fraud protection features
- Security-first design with shield iconography

[→ Frontend Documentation](./frontend/README.md)

## Quick Start

### Prerequisites

- **Python 3.9+** with virtual environment support
- **Node.js 18+** with pnpm (`npm install -g pnpm`)
- **LiveKit Server** - Download from [LiveKit releases](https://github.com/livekit/livekit/releases)
- **API Keys**:
  - [Murf Falcon API key](https://murf.ai/api)
  - [Google AI API key](https://makersuite.google.com/app/apikey)
  - [Deepgram API key](https://deepgram.com/)

### 1. Clone the Repository

```bash
git clone https://github.com/Ayushnema704/Day_6_Fraud_Alert_Voice_Agent.git
cd Day_6_Fraud_Alert_Voice_Agent
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -e .

# Create .env.local with your credentials
# Copy from .env.example and fill in:
```

**backend/.env.local:**
```bash
LIVEKIT_URL=ws://127.0.0.1:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret
GOOGLE_API_KEY=your_google_api_key_here
MURF_API_KEY=your_murf_api_key_here
DEEPGRAM_API_KEY=your_deepgram_api_key_here
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
pnpm install

# Create .env.local (same LiveKit credentials as backend)
```

**frontend/.env.local:**
```bash
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret
LIVEKIT_URL=ws://127.0.0.1:7880
```

### 4. Initialize the Database

```bash
cd backend
python init_fraud_db.py
```

This creates `fraud_cases.db` with 5 sample fraud cases for testing.

### 5. Run the Application

**Windows PowerShell:**
```powershell
# Terminal 1 - LiveKit Server
.\livekit-server.exe --dev

# Terminal 2 - Backend Agent
cd backend
.\.venv\Scripts\python.exe src\agent.py dev

# Terminal 3 - Frontend
cd frontend
pnpm dev
```

**macOS/Linux:**
```bash
# Terminal 1 - LiveKit Server
livekit-server --dev

# Terminal 2 - Backend Agent
cd backend
source venv/bin/activate
python src/agent.py dev

# Terminal 3 - Frontend
cd frontend
pnpm dev
```

**Access the app:** Open http://localhost:3000 in your browser and click **"Connect to Fraud Department"**

## How It Works

1. **Introduction** - Agent Martinez from SecureBank calls about suspicious transaction
2. **Username Request** - Agent asks for registered username to load case
3. **Case Loading** - System retrieves pending fraud case from database using `load_fraud_case()`
4. **Security Verification** - Agent asks security question (e.g., "What city were you born in?")
5. **Identity Check** - System validates answer using `verify_customer()`
   - ✅ **Success**: Proceeds to transaction details
   - ❌ **Failure**: Case marked as `verification_failed`, call ends
6. **Transaction Review** - Agent presents:
   - Merchant name and location
   - Transaction amount (₹)
   - Date and time
   - Last 4 digits of card
7. **Customer Confirmation** - "Did you make this transaction?"
   - **YES**: Case marked as `confirmed_safe`
   - **NO**: Case marked as `confirmed_fraud`
8. **Case Resolution** - System updates database via `update_fraud_case()`
   - **Safe**: "Thank you, routine security check"
   - **Fraud**: "Card blocked, new card in 5-7 days, dispute filed"
9. **Closing** - Professional goodbye with security reminder

### Sample Test Cases

**Test Case 1: Confirmed Safe (John Smith)**
```
Agent: "May I please have your registered username?"
User: "John Smith"
Agent: "What is your favorite color?"
User: "blue"
Agent: "Transaction: ₹2,499.99 at ABC Electronics... Did you make this?"
User: "Yes"
Agent: "Thank you, routine security check. Have a great day!"
```

**Test Case 2: Confirmed Fraud (Sarah Johnson)**
```
Agent: "May I please have your registered username?"
User: "Sarah Johnson"
Agent: "What city were you born in?"
User: "delhi"
Agent: "Transaction: ₹15,999.00 at Luxury Fashion Boutique... Did you make this?"
User: "No"
Agent: "Card blocked immediately. New card in 5-7 days. Dispute filed."
```

**Test Case 3: Verification Failed (Michael Brown)**
```
Agent: "May I please have your registered username?"
User: "Michael Brown"
Agent: "What is your mother's maiden name?"
User: "incorrect answer"
Agent: "Verification failed. Please contact the bank directly. Goodbye."
```

## Database Structure

The `fraud_cases.db` includes 5 sample users for testing:

| Username | Security Question | Answer | Card | Amount | Merchant | Location |
|----------|------------------|--------|------|--------|----------|----------|
| John Smith | Favorite color? | blue | 4242 | ₹2,499.99 | ABC Electronics | Shanghai |
| Sarah Johnson | Birth city? | delhi | 5678 | ₹15,999.00 | Luxury Fashion | Paris |
| Michael Brown | Mother's maiden name? | sharma | 9012 | ₹899.50 | Gaming Paradise | Tokyo |
| Emily Davis | Pet's name? | max | 3456 | ₹5,299.99 | Tech Gadgets | Singapore |
| David Wilson | Favorite food? | pizza | 7890 | ₹12,500.00 | Watch Collection | Dubai |

## Project Highlights

SecureBank Fraud Alert includes several fraud detection optimizations:

- **Real-time Verification** - Instant identity validation via security questions
- **Database Integration** - SQLite for persistent case management
- **Status Tracking** - Comprehensive case lifecycle (pending → verified → resolved)
- **Professional Persona** - Calm, reassuring Agent Martinez character
- **SecureBank Branding** - Blue theme matching banking/security industry
- **Natural Conversation** - Voice-first fraud detection without forms
- **Murf Falcon TTS** - Fastest TTS API for minimal latency

## Troubleshooting

### Common Issues

**Agent not responding?**
- Ensure all three services are running (LiveKit server, backend agent, frontend)
- Check that all API keys are correct in `.env.local` files (Murf, Google, Deepgram)
- Verify `fraud_cases.db` exists in backend folder
- Restart backend agent if it shut down

**Database errors?**
- Re-initialize database: `python init_fraud_db.py`
- Check backend logs for "Loading fraud case for username: [name]"
- Verify all 5 test cases are in database: `sqlite3 fraud_cases.db "SELECT userName FROM fraud_cases"`

**Case not loading?**
- Use exact username from test data (case-insensitive)
- Check backend logs for "No pending fraud case found"
- Ensure case status is `pending_review` (re-run init script to reset)
- Database must be in `backend/fraud_cases.db` location

**"Failed to fetch" error?**
- Restart frontend to reload environment variables: `pnpm dev`
- Verify `.env.local` exists in both backend and frontend directories
- Check LIVEKIT_URL is set to `ws://127.0.0.1:7880` for local development

**Microphone permission denied?**
- Allow microphone access in browser settings (Chrome/Edge: Settings → Privacy → Microphone)
- Ensure you're using localhost or HTTPS (required for microphone access)
- Test mic: Open DevTools (F12) → Console → `navigator.mediaDevices.getUserMedia({audio: true})`

**SecureBank branding not showing?**
- Hard refresh browser (Ctrl+Shift+R)
- Check `app-config.ts` has SecureBank branding
- Clear Next.js cache: `Remove-Item -Recurse -Force frontend\.next`

### Quick Reset
```powershell
# If nothing works, clean restart:
cd backend
Remove-Item -Recurse -Force .venv, *.egg-info
python -m venv .venv
.\.venv\Scripts\activate
pip install -e .
python init_fraud_db.py

cd ..\frontend
Remove-Item -Recurse -Force node_modules, .next
pnpm install
```

## Resources

- [Murf Falcon TTS Documentation](https://murf.ai/api/docs/text-to-speech/streaming)
- [LiveKit Agents Documentation](https://docs.livekit.io/agents)
- [Google Gemini API](https://ai.google.dev/docs)
- [Deepgram STT](https://developers.deepgram.com/)

## Technical Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| TTS | Murf Falcon | Ultra-fast, natural voice synthesis |
| STT | Deepgram Nova-3 | High-accuracy speech recognition |
| LLM | Google Gemini 2.5-flash | Fraud detection conversation intelligence |
| VAD | Silero | Voice activity detection & turn detection |
| Backend | LiveKit Agents (Python) | Fraud alert agent orchestration |
| Frontend | Next.js 15 + LiveKit React | Real-time banking UI |
| Database | SQLite | Fraud case storage & management |

## Future Enhancements

- 📊 Analytics dashboard for fraud patterns and statistics
- 🔗 Integration with banking core systems
- 📧 Automated email/SMS notifications for customers
- 💾 PostgreSQL/MongoDB for enterprise-scale fraud detection
- 📈 Machine learning for fraud prediction scoring
- 🎯 Multi-factor authentication options
- 📱 Mobile app version for on-the-go verification
- 🔒 Advanced encryption for sensitive data
- 🌐 Multi-language support for global banking
- 🤖 Sentiment analysis for customer stress detection
- 📞 Call recording and compliance features
- 🔔 Real-time alerts to fraud investigation teams

## License

This project is based on MIT-licensed templates from LiveKit. See individual LICENSE files in backend and frontend directories.

## Acknowledgments

- Built for **#MurfAIVoiceAgentsChallenge** by [murf.ai](https://murf.ai)
- Based on [LiveKit's agent starter templates](https://github.com/livekit-examples)
- Uses [Murf Falcon TTS](https://murf.ai/api) - the fastest TTS API for voice synthesis
- SecureBank is a fictional institution created for this educational demo

---

**Day 6 Challenge Submission** | Built with 🛡️ for fraud detection and customer security

**Challenge Hashtags:** #MurfAIVoiceAgentsChallenge #10DaysofAIVoiceAgents
