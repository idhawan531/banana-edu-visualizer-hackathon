# 📚 EduVisualizer - AI-Powered Educational Concept Visualizer

**Create consistent educational illustrations with the SAME character across different concepts using Google's Gemini 2.5 Flash Image API.**

![Python](https://img.shields.io/badge/pythonensehon by Google*

## 🚀 **[Try EduVisualizer Live!](https://banana-edu-visualizer-hackatho-we2n3qsp7axcayhgpbbcbe.streamlit.app/)**

**No installation required - Start creating educational visuals immediately!**

## 🌟 Overview

EduVisualizer is an innovative educational tool that leverages AI to create consistent, engaging visual learning materials. The app generates educational illustrations featuring the same character across multiple learning concepts, helping students build familiarity and connection with educational content.

## ✨ Key Features

### 🎨 Character Consistency System
- **Base Character Creation**: Generate or upload a custom educational character
- **Cross-Concept Consistency**: Maintain the same character appearance across all educational topics
- **Style Preservation**: Keep consistent visual style, clothing, and distinctive features

### 📖 Educational Concept Generation
- **Pre-defined Topics**: Ready-to-use concepts including:
  - Photosynthesis process
  - Ancient Roman marketplace
  - Water cycle diagram
  - Newton's laws of motion
  - Human digestive system
- **Custom Concepts**: Enter your own educational topics
- **Clear Visualizations**: Bright, labeled educational diagrams suitable for students

### ✏️ Advanced Editing Capabilities
- **Natural Language Editing**: Modify generated images using simple text descriptions
- **Educational Focus**: Ensures all edits remain pedagogically relevant
- **Character Preservation**: Maintains character consistency during edits

### 🖼️ User-Friendly Interface
- **Gallery View**: Organized display of all generated concepts
- **API Usage Tracking**: Monitor your API call consumption
- **Error Handling**: Comprehensive guidance for troubleshooting
- **Pre-generated Examples**: Fallback demonstrations for API limit scenarios

## 🚀 Getting Started

### Option 1: Use Live Application (Recommended)
**🌐 [Access EduVisualizer Online](https://banana-edu-visualizer-hackatho-we2n3qsp7axcayhgpbbcbe.streamlit.app/)**

1. Click the link above to open the live application
2. Enter your Gemini API key ([Get one here](https://aistudio.google.com/app/apikey))
3. Start creating educational visuals immediately!

### Option 2: Run Locally

#### Prerequisites
- Python 3.8 or higher
- Google Gemini API key ([Get one here](https://aistudio.google.com/app/apikey))

#### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/eduvisualizer.git
cd eduvisualizer
```

2. **Install dependencies:**
```bash
pip install streamlit google-genai pillow
```

3. **Run the application:**
```bash
streamlit run app.py
```

4. **Open your browser:**
Navigate to `http://localhost:8501`

## 🔧 Usage

### 1. API Setup
- Enter your Gemini API key in the provided field
- The app will confirm successful configuration

### 2. Character Creation
**Option A: Generate a Character**
- Describe your desired educational character
- Example: "A curious 10-year-old student with glasses, wearing blue t-shirt, brown hair"
- Click "Generate Base Character"

**Option B: Upload a Character**
- Upload your own character image (JPG, JPEG, PNG)
- The app will process and optimize the image automatically

### 3. Generate Educational Concepts
- Select from pre-defined concepts or enter a custom topic
- Click "Generate Concept Scene"
- View your character demonstrating the educational concept

### 4. Edit Generated Images
- Select any generated concept scene
- Describe desired edits in natural language
- Apply changes while maintaining character consistency

## 📁 Project Structure

```
eduvisualizer/
│
├── app.py                 # Main Streamlit application
├── GeneratedImages/       # Sample images for demonstration
│   ├── BaseImage1.jpg
│   ├── BaseImage2.jpg
│   ├── GeneratedImage1-3.jpg
│   └── ...
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🔑 API Configuration

The app uses Google's Gemini 2.5 Flash Image Preview model. You'll need:

1. A Google AI Studio account
2. An API key with image generation permissions
3. Understanding of rate limits (Free tier: 100 requests/day)

## 🎯 Educational Benefits

- **Visual Consistency**: Same character across topics builds student familiarity
- **Engagement**: Personalized learning experiences with consistent visual elements
- **Comprehension**: Clear, labeled educational diagrams improve understanding
- **Accessibility**: Bright, clear illustrations suitable for various learning styles

## 🛠️ Technical Details

### Core Technologies
- **Frontend**: Streamlit for interactive web interface
- **AI Integration**: Google Gemini 2.5 Flash Image API
- **Image Processing**: PIL (Python Imaging Library)
- **Session Management**: Streamlit session state
- **Deployment**: Streamlit Community Cloud

### Key Functions
- `generate_image()`: Handles API calls with optional reference images
- Character consistency through reference-based generation
- Automatic image optimization and format conversion
- Comprehensive error handling and user feedback

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 🐛 Troubleshooting

### Common Issues
- **API Key Issues**: Verify your key is correct and has image generation permissions
- **Rate Limits**: Free tier has daily limits; consider upgrading for higher usage
- **Image Upload**: Ensure images are in JPG, JPEG, or PNG format
- **Large Images**: App automatically resizes images that exceed size limits

## 🌐 Live Demo

**Experience EduVisualizer now**: [https://banana-edu-visualizer-hackatho-we2n3qsp7axcayhgpbbcbe.streamlit.app/](https://banana-edu-visualizer-hackatho-we2n3qsp7axcayhgpbbcbe.streamlit.app/)

*No installation required - just bring your Gemini API key and start creating!*

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏆 Hackathon Information

This project was developed for the **Nano Banana 48 Hour Hackathon by Google**, showcasing the capabilities of Gemini 2.5 Flash Image for educational content creation.

## 📞 Contact

- **Live Application**: [EduVisualizer on Streamlit Cloud](https://banana-edu-visualizer-hackatho-we2n3qsp7axcayhgpbbcbe.streamlit.app/)
- **Project Repository**: [GitHub Link]
- **Issues**: Report bugs and request features through GitHub Issues
- **Hackathon**: Nano Banana 48 Hour Hackathon Submission

***

**Made with ❤️ for educators and students everywhere**

*Empowering education through consistent AI-generated visual learning materials*

**🎯 [Start Creating Educational Visuals Now!](https://banana-edu-visualizer-hackatho-we2n3qsp7axcayhgpbbcbe.streamlit.app/)**
