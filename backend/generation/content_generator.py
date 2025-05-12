import os
import openai
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional, Tuple
import logging
from .vadoo_generator import ModelslabVideoGenerator

load_dotenv()

class ContentGenerator:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        openai.api_key = self.api_key
        self.logger = logging.getLogger(__name__)
        
    def analyze_trending_topics(self, video_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze trending topics from video data using GPT-4
        """
        video_titles = [video['title'] for video in video_data]
        video_descriptions = [video['description'] for video in video_data]
        
        prompt = f"""
        Analyze the following trending YouTube video titles and descriptions to identify:
        1. Common themes and topics
        2. Popular content formats
        3. Engaging title patterns
        4. Key elements that make these videos successful
        
        Video Titles:
        {video_titles}
        
        Video Descriptions:
        {video_descriptions}
        
        Provide a detailed analysis in JSON format with the following structure:
        {{
            "common_themes": [],
            "content_formats": [],
            "title_patterns": [],
            "success_factors": []
        }}
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a content analysis expert specializing in YouTube trends."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        try:
            import json
            analysis_result = json.loads(response.choices[0].message['content'])
        except json.JSONDecodeError:
            print("Warning: Could not parse analysis response as JSON")
            analysis_result = {"error": "Invalid analysis format"}
        except Exception as e:
            print(f"Error processing analysis response: {e}")
            analysis_result = {"error": "Could not process analysis"}
            
        return analysis_result
    
    def generate_content(self, topic: str, content_type: str, tone: str, 
                         length: str, story_summary: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a concise video prompt (1-2 sentences), video length, and tags/concepts for text-to-video generation.
        """
        # Compose a concise, vivid prompt for the video model
        prompt = f"""
        Given the following information:
        - Topic: {topic}
        - Tone: {tone}
        - Length: {length}
        - Story Summary: {story_summary}
        Write a single, vivid, and engaging 1-2 sentence prompt for a text-to-video AI model. Do NOT write a full story or script. Focus on the main visual and emotional concept, using descriptive language. Avoid scene breakdowns or dialogue. Example: 'A mother lovingly chases her child through a sunlit village street, with trees and a temple in the background.'
        """
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert at writing concise, vivid prompts for text-to-video AI models."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        video_prompt = response.choices[0].message['content'].strip().replace('\n', ' ')
        
        # Extract tags/concepts from topic and summary
        tags = []
        if topic:
            tags.extend([t.strip() for t in topic.split(',') if t.strip()])
        if story_summary:
            import re
            # Extract keywords (nouns) from summary
            words = re.findall(r'\b\w+\b', story_summary)
            for w in words:
                if w.lower() not in tags and len(w) > 3:
                    tags.append(w.lower())
        # Remove duplicates and keep top 5
        tags = list(dict.fromkeys(tags))[:5]
        
        # Map length to seconds (default: 60)
        length_map = {"short": "30", "medium": "60", "long": "120"}
        video_length = length_map.get(length.lower(), "60")
        
        return {
            "video_prompt": video_prompt,
            "video_length": video_length,
            "tags": tags
        }
    
    def generate_video_script(self, content: Dict, style: str = "educational") -> Dict:
        """
        Generate a detailed video script from the content, optimized for Vadoo video generation.
        
        Args:
            content (Dict): The content to convert into a video script
            style (str): The style of the video (educational, entertaining, etc.)
            
        Returns:
            Dict: A dictionary containing the script and scene descriptions
        """
        try:
            prompt = f"""Create a detailed video script from this content:
            Title: {content.get('title', '')}
            Main Points: {content.get('main_points', [])}
            Key Takeaways: {content.get('key_takeaways', [])}
            
            Format the script as follows:
            1. A clear narrative flow divided into scenes
            2. Each scene should have:
               - Scene description (visual elements)
               - Voiceover text
               - Any text overlays or captions
            3. Keep scenes concise and visually engaging
            4. Maintain a {style} tone throughout
            5. Include natural transitions between scenes
            """

            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional video scriptwriter."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
            )

            script = response.choices[0].message['content']

            # Process the script into a format suitable for Vadoo
            formatted_script = self._process_script_for_vadoo(script)

            return {
                "title": content.get("title", ""),
                "script": formatted_script,
                "style": style,
                "raw_script": script
            }

        except Exception as e:
            self.logger.error(f"Error generating video script: {str(e)}")
            raise

    def _process_script_for_vadoo(self, script: str) -> str:
        """
        Process the raw script into a format suitable for Vadoo video generation.
        Vadoo expects a single text prompt, so we'll format the script accordingly.
        
        Args:
            script (str): The raw script text
            
        Returns:
            str: Formatted script text for Vadoo
        """
        # Clean up the script and format it for Vadoo
        lines = [line.strip() for line in script.split('\n') if line.strip()]
        formatted_script = ' '.join(lines)
        
        # Ensure the script isn't too long for Vadoo's limits
        max_length = 2000
        if len(formatted_script) > max_length:
            formatted_script = formatted_script[:max_length-3] + "..."
            
        return formatted_script

    def generate_video(self, script: Dict, video_generator: ModelslabVideoGenerator) -> str:
        """
        Generate a video using the Modelslab video generator.
        
        Args:
            script (Dict): The processed video script
            video_generator (ModelslabVideoGenerator): Instance of the Modelslab video generator
            
        Returns:
            str: URL or path to the generated video
        """
        try:
            # Use the concise prompt for Modelslab
            text_prompt = script["video_prompt"] if "video_prompt" in script else script.get("raw_script", "")
            video_url = video_generator.generate_video_from_text(
                text_prompt=text_prompt
            )
            return video_url
        except Exception as e:
            self.logger.error(f"Error in video generation: {str(e)}")
            raise 