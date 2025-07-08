#  Crafty Generator - AI-Powered Crochet Pattern Generator

Transform your crochet inspiration into detailed patterns using AI. Upload a photo and/or description to get an AI generated crochet pattern, with skill level, estimated time, materials needed, and the pattern instructions.

[![React](https://img.shields.io/badge/React-18%2B-blue)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.8%2B-yellow)](https://www.python.org/)
[![AI](https://img.shields.io/badge/AI-Powered-purple)](#)

## Features

- **Dual Input**: Upload images OR describe your project in text
- **Model trained on 1000+ Patterns**: For accurate results
- **Smart Analysis**: Automatic difficulty estimation, time estimates, materials extraction
- **Downloadable**: Clean .txt files with patterns are instantly available for download
- **Beautiful UI**: Modern React interface with pink/purple theme

##  Quick Start

### Prerequisites
- [Python 3.8+](https://python.org/downloads) - Programming language for the backend
- [Node.js 16+](https://nodejs.org/en/download) - JavaScript runtime for the frontend
- [Git](https://git-scm.com/downloads) - Version control system

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/crafty-generator.git
cd crafty-generator
```

2. **Set up environment variables**

**Get your Gemini API key:**
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated API key

**Create your .env file:**
```bash
# Create .env file with your Gemini API key
echo "GEMINI_API_KEY=your_actual_api_key_here" > .env
```

**Important:** Never share your API key or commit it to version control!

## 🔑 Detailed API Key Setup

### Getting Your Gemini API Key

**Step 1: Go to Google AI Studio**
1. Visit [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account

**Step 2: Create API Key**
1. Click the **"Create API Key"** button
2. Choose **"Create API key in new project"** (recommended)
3. Your API key will be generated (starts with `AIzaSy`)
4. **Copy the API key immediately** - you won't be able to see it again!

**Step 3: Set Up Your Environment**
1. In your project root directory, create a `.env` file:
```bash
echo "GEMINI_API_KEY=your_actual_api_key_here" > .env
```

2. Replace `your_actual_api_key_here` with your real API key

**Step 4: Verify Setup**
Your `.env` file should look like this:
```
GEMINI_API_KEY=AIzaSy_your_actual_key_here_32_characters_long
```

### 🔒 Security Best Practices

**✅ DO:**
- Keep your API key in the `.env` file only
- Add `.env` to your `.gitignore` file
- Use environment variables in your code
- Regenerate your key if it's ever exposed

**❌ DON'T:**
- Share your API key with anyone
- Commit your API key to version control
- Hardcode API keys in your source code
- Post your API key in forums or chat

### 💰 API Usage & Costs

**Free Tier Limits:**
- **15 requests per minute**
- **1,500 requests per day**
- **1 million tokens per month**

**Monitoring Usage:**
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click on your API key
3. View usage statistics

**Cost Management:**
- Set up billing alerts in Google Cloud Console
- Monitor your usage regularly
- The free tier is usually sufficient for development

### 🔄 Regenerating Your API Key

If your API key is compromised:
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click the trash icon next to your old key
3. Create a new API key
4. Update your `.env` file with the new key
5. Restart your application

3. **Set up the backend**
```bash
cd fastapi-template
python -m venv .venv310
source .venv310/bin/activate  # On Windows: .venv310\Scripts\activate
pip install -r requirements.txt
```

4. **Set up the frontend**
```bash
cd ../crochet-decoder
npm install
```

5. **Start the application**
```bash
cd ..
./start_yarn_master.sh
```

## Access Points

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## How to Use

### From Homepage:
1. Click **"Upload Image"** for image-based generation
2. Click **"Describe Project"** for text-based generation
3. Both buttons lead to the same unified interface

### Pattern Generation:

**Method 1: Image Upload**
1. Select "Upload Image" tab (or click "Upload Image" from homepage)
2. Upload a crochet photo
3. Add optional description for context
4. Generate pattern

**Method 2: Text Description**
1. Select "Text Description" tab (or click "Describe Project" from homepage)
2. Describe your project in detail
3. Generate pattern

**Switch Between Modes:**
- Use the tab buttons to switch between image and text input
- Both modes available on the same page for convenience

### Pattern Output
- Materials needed
- Difficulty level
- Estimated completion time
- Step-by-step instructions
- Downloadable text file

## Project Structure

```
crafty-generator/
├── fastapi-template/          # Backend API
│   ├── main.py               # FastAPI application
│   ├── pattern_generator.py  # AI pattern generation
│   └── requirements.txt      # Python dependencies
├── crochet-decoder/          # Frontend React app
│   ├── src/
│   │   ├── HomePage.js      # Landing page
│   │   └── FileUpload.js    # Pattern generation interface
│   └── package.json         # Node dependencies
├── start_yarn_master.sh     # Startup script
└── README.md # Full documentation
```

## API Endpoints

- `POST /generate-pattern` - Generate pattern from image
- `POST /generate-pattern-from-text` - Generate pattern from text
- `GET /health` - Health check
- `GET /models` - Available models and styles

##  AI Technology

- **Base Model**: Gemini AI for pattern generation
- **Training Data**: 4496+ processed crochet patterns
- **RAG Pipeline**: Retrieval-Augmented Generation for context
- **Smart Analysis**: Image processing and pattern intelligence

## Development

### Adding New Features
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

### Local Development
```bash
# Backend
cd fastapi-template
source .venv310/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Frontend
cd crochet-decoder
npm start
```

## Technical Details

### Architecture
- **Frontend**: React.js with Tailwind CSS
- **Backend**: FastAPI (Python)
- **AI Processing**: Gemini AI with RAG pipeline
- **Communication**: RESTful API with JSON

### API Examples

**Generate from Text:**
```bash
curl -X POST "http://localhost:8000/generate-pattern-from-text" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "A cozy winter scarf with cable pattern",
    "style": "standard",
    "model_type": "yarn_master"
  }'
```

**Response Format:**
```json
{
  "success": true,
  "pattern": "CROCHET PATTERN\n===============\n...",
  "generation_time": "0.05s",
  "materials": ["Yarn", "Hook", "Needle"],
  "difficulty": "Beginner",
  "estimated_time": "2-4 hours"
}
```

##  Troubleshooting

### Common Issues

**Backend won't start:**
```bash
cd fastapi-template
source .venv310/bin/activate
pip install -r requirements.txt
```

**Frontend won't start:**
```bash
cd crochet-decoder
npm install
npm start
```

**Port conflicts:**
- Backend uses port 8000
- Frontend uses port 3000
- Change ports in startup script if needed

**Pattern generation fails:**
- Check internet connection
- Ensure Gemini API key is set in .env file
- Verify your API key is valid at [Google AI Studio](https://makersuite.google.com/app/apikey)
- Try refreshing and starting over

**API key issues:**
- Make sure `.env` file exists in the root directory
- Check that your API key starts with `AIzaSy`
- Ensure no extra spaces or quotes around the API key
- Restart the backend after changing the .env file

##  Usage Tips

### For Best Results

**Image Uploads:**
- Use clear, well-lit photos
- Show the full crochet item
- Include close-ups of stitch details
- Add descriptive text for context

**Text Descriptions:**
- Be specific about size (baby blanket, adult scarf, etc.)
- Mention yarn weight (worsted, DK, etc.)
- Include style details (cables, lace, solid, etc.)
- Specify skill level preference

**Example Good Descriptions:**
- "A baby blanket in soft pastels with simple stitches, about 30x40 inches"
- "An adult-sized beanie with ribbed brim in chunky yarn"
- "A rectangular table runner with lace edging in cotton yarn"

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

##  License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

##  Acknowledgments

- Inspired by Harvard's AC215 Yarn Master project
- Built with FastAPI, React, and Gemini AI

---

**Happy Crocheting! 🧶✨**

