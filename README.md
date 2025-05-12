# AI-Powered Social Media Content Automation 🚀

Transform your social media presence with AI-driven content creation and automation. This powerful tool helps you discover trending content, generate engaging posts, and create stunning videos - all with minimal effort.

## 🌟 Overview

AI Social Media Automation is your all-in-one solution for creating viral-worthy content. Currently supporting YouTube (with Instagram and TikTok integration coming soon), this tool leverages advanced AI to:

- Discover high-performing content from top creators
- Analyze trending topics and engagement patterns
- Generate unique, engaging content ideas
- Create professional-quality videos automatically
- Optimize content for maximum reach and engagement

## 🎥 Video Demonstration

Watch our demo video to see the AI Social Media Automation tool in action:
[Project Demo Video](https://drive.google.com/file/d/17SPsZGLQRE9T07N-I-eLRbDtieOfcOaK/view?usp=sharing)

## ✨ Key Features

### Content Discovery & Analysis
- **Trending Content Detection**: Automatically identify viral content patterns
- **Performance Analytics**: Analyze views, engagement, and growth metrics
- **Topic Analysis**: Extract trending topics and themes
- **Competitor Insights**: Track successful content strategies

### AI-Powered Content Generation
- **Smart Content Creation**: Generate unique content ideas based on trends
- **Automated Script Writing**: Create engaging video scripts
- **Tag Optimization**: Generate relevant hashtags and keywords
- **Style Customization**: Match your brand voice and tone

### Video Generation
- **Text-to-Video Conversion**: Transform scripts into professional videos
- **Modelslab Integration**: High-quality video generation
- **Custom Duration**: Generate videos of varying lengths
- **Style Consistency**: Maintain brand identity across content

## 🎯 Use Cases

### For Brands & Businesses
- **Automated Brand Building**: Create consistent, engaging content
- **Marketing Campaign Automation**: Scale your marketing efforts
- **Content Calendar Management**: Plan and schedule content
- **Competitive Analysis**: Stay ahead of industry trends

### For Content Creators
- **Content Research**: Discover trending topics
- **Video Production**: Generate professional videos
- **Engagement Optimization**: Maximize content reach
- **Time Efficiency**: Reduce content creation time

### For Marketing Teams
- **Campaign Automation**: Streamline marketing workflows
- **Performance Tracking**: Monitor content success
- **Content Strategy**: Data-driven content planning
- **Resource Optimization**: Reduce production costs

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python
- **AI/ML**: 
  - OpenAI GPT-4
  - Modelslab Video Generation
- **APIs**: 
  - YouTube Data API v3
  - (Coming soon) Instagram Graph API
  - (Coming soon) TikTok API
- **Database**: MongoDB Atlas
- **Video Processing**: Modelslab

## 📋 Prerequisites

- Python 3.8+
- MongoDB Atlas account
- YouTube API key and credentials:
  1. Go to [Google Cloud Console](https://console.cloud.google.com/)
  2. Create a new project or select an existing one
  3. Enable the YouTube Data API v3
  4. Create OAuth 2.0 credentials:
     - Go to "APIs & Services" > "Credentials"
     - Click "Create Credentials" > "OAuth client ID"
     - Choose "Desktop app" as the application type
     - Download the credentials and save as `credentials.json` in the project root
  5. Create an API key:
     - Go to "APIs & Services" > "Credentials"
     - Click "Create Credentials" > "API key"
     - Copy the API key for your `.env` file
- OpenAI API key
- Modelslab API key

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/tarasariya-uttam/ai-social-media-automation.git
cd ai-social-media-automation
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory and add the following environment variables:
```
OPENAI_API_KEY=your_openai_api_key
YOUTUBE_API_KEY=your_youtube_api_key
MODELSLAB_API_KEY=your_modelslab_api_key
MONGO_URI=your_mongodb_connection_string
```

## 💻 Usage

1. Start the application:
```bash
streamlit run app/main.py
```

2. Access the dashboard at `http://localhost:8501`

3. Key Features:
   - Content Discovery: Find trending videos
   - Content Generation: Create new content
   - Video Creation: Generate videos
   - Performance Analytics: Track results

## 🔜 Roadmap

- Instagram content integration
- TikTok content integration
- Advanced analytics dashboard
- Multi-platform posting
- Custom video templates
- AI-powered thumbnail generation
- Automated scheduling system

## 🤝 Contributing

We welcome contributions! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support, email support@example.com or create an issue in the repository.

---

Built with ❤️ for content creators and marketers 