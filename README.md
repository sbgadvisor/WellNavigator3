# WellNavigator MVP Chatbot

An empathetic, LLM-driven patient advocacy chatbot that helps patients and caregivers navigate their healthcare journey through natural, dynamic conversations.

## 🎯 Overview

WellNavigator is a conversation-first assistant that guides users through healthcare situations without predefined flows. The chatbot listens, asks clarifying questions, and dynamically decides what kind of help to offer—whether that's preparing for appointments, understanding test results, finding resources, or providing caregiver support.

## ✨ Key Features

### Core Capabilities
- 💬 **Empathetic Conversations** - Warm, conversational, non-clinical tone that speaks like a caring human friend
- 🧠 **Dynamic Understanding** - LLM-powered reasoning that adapts to each user's unique situation
- 🎯 **Autonomous Track Detection** - Intelligently identifies user needs (appointments, results, resources, caregiver support)
- 🛠️ **Mock Tools Integration** - Appointment guides, results explanations, resource finder, and caregiver support
- 🔄 **Re-engagement** - Always invites further conversation and help
- ⚠️ **Transparency** - Clear disclaimers that the chatbot is not a medical professional

### Technical Features
- 🤖 **OpenAI Integration** - Powered by GPT-4o-mini, GPT-4o, or GPT-3.5-turbo
- 💾 **Session Memory** - Maintains conversation context throughout the session
- 📊 **Streaming Responses** - Real-time response streaming for better UX
- 🎨 **Modern UI** - Clean, accessible interface with visual disclaimers
- 🔌 **Modular Architecture** - Mock tools designed for easy replacement with real APIs

## 📁 Project Structure

```
WellNavigator/
├── app.py              # Main Streamlit application
├── prompts.py          # System prompts and message templates
├── tools.py            # Mock tools (appointments, results, resources, caregiver)
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
└── README.md          # This file
```

## 🚀 Setup

### Prerequisites
- Python 3.9+
- OpenAI API key

### Installation

1. **Activate virtual environment:**
   ```bash
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API key:**
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` and add your OpenAI API key:
     ```
     OPENAI_API_KEY=sk-your-actual-api-key-here
     ```

4. **Run the app:**
   ```bash
   streamlit run app.py
   ```

The app will open in your browser at `http://localhost:8501`

## 💡 Usage

### Starting a Conversation
1. The chatbot greets you with a welcome message and disclaimer
2. Share your situation freely—no rigid forms or predefined paths
3. The chatbot will ask clarifying questions if needed
4. It will propose helpful tracks (appointment prep, results explanation, etc.)
5. After helping, it invites you to continue the conversation

### Example Conversation Flow
```
User: "I have an appointment next week and I'm nervous"

Bot: [Empathetic response, asks clarifying questions]
     "It sounds like preparing for your upcoming appointment 
      might help most—would you like to start there?"

User: "Yes, that would be great"

Bot: [Provides appointment preparation guide with checklist]
     [Re-engagement prompt]
```

## 🏗️ Architecture

### System Prompts (`prompts.py`)
- Defines WellNavigator's persona and behavior
- Emphasizes empathy, plain English, and transparency
- Guides conversational flow patterns

### Mock Tools (`tools.py`)
- **AppointmentTool** - Appointment preparation guides and mock booking
- **ResultsTool** - Test results explanation and context
- **ResourcesTool** - Health resources and support services finder
- **CaregiverTool** - Caregiver support and guidance

All tools are designed with interfaces that can be replaced with real API calls later.

### Main App (`app.py`)
- Handles conversation flow and state management
- Integrates LLM calls with system prompts
- Detects user intent and suggests appropriate tools
- Formats and displays tool results
- Manages re-engagement and disclaimer messaging

## 🔮 Future Enhancements

The architecture supports easy integration of:
- **Supabase** - Chat persistence and history
- **Real Appointment APIs** - Actual scheduling systems
- **RAG Integration** - Context-aware responses from curated health sources
- **Function Calling** - More sophisticated tool invocation using OpenAI's function calling API
- **Community Modules** - Expanded caregiver and community support features

## ⚠️ Important Disclaimers

**WellNavigator is not a medical professional.** The chatbot:
- Provides guidance and support
- Helps navigate healthcare systems
- Offers preparation assistance and resources
- **Does NOT** provide medical advice, diagnoses, or treatment recommendations

Always consult with licensed healthcare professionals for medical advice.

## 📝 License

This is an MVP/prototype implementation for demonstration purposes.

## 🤝 Contributing

This is currently an MVP. Future contributions welcome once the project structure is finalized.
