# import os
# import requests
# import time
# from dotenv import load_dotenv
# import json
# 
# load_dotenv()
# 
# class ImagineVideoGenerator:
#     ... (existing code commented out)

import os
import requests
import json
from dotenv import load_dotenv
import logging
from typing import Optional

load_dotenv()

class ModelslabVideoGenerator:
    DURATIONS = {
        "30": "30 seconds",
        "60": "1 minute",
        "90": "1.5 minutes",
        "120": "2 minutes",
        "180": "3 minutes",
        "300": "5 minutes"
    }
    
    API_URL = "https://modelslab.com/api/v6/video/text2video"
    DEFAULT_MODEL_ID = "cogvideox"
    DEFAULT_NEGATIVE_PROMPT = "low quality"
    DEFAULT_HEIGHT = 512
    DEFAULT_WIDTH = 512
    DEFAULT_NUM_FRAMES = 16
    DEFAULT_NUM_INFERENCE_STEPS = 20
    DEFAULT_GUIDANCE_SCALE = 7
    DEFAULT_OUTPUT_TYPE = "mp4"
    DEFAULT_FPS = 7
    DEFAULT_UPSCALE_HEIGHT = 1024
    DEFAULT_UPSCALE_WIDTH = 1024
    DEFAULT_UPSCALE_STRENGTH = 0.6
    DEFAULT_UPSCALE_GUIDANCE_SCALE = 8
    DEFAULT_UPSCALE_NUM_INFERENCE_STEPS = 20

    def __init__(self):
        self.api_key = os.getenv("MODELSLAB_API_KEY")
        if not self.api_key:
            raise ValueError("MODELSLAB_API_KEY environment variable is not set")
        self.logger = logging.getLogger(__name__)

    def generate_video_from_text(
        self,
        text_prompt: str,
        model_id: str = DEFAULT_MODEL_ID,
        negative_prompt: str = DEFAULT_NEGATIVE_PROMPT,
        height: int = DEFAULT_HEIGHT,
        width: int = DEFAULT_WIDTH,
        num_frames: int = DEFAULT_NUM_FRAMES,
        num_inference_steps: int = DEFAULT_NUM_INFERENCE_STEPS,
        guidance_scale: float = DEFAULT_GUIDANCE_SCALE,
        output_type: str = DEFAULT_OUTPUT_TYPE,
        fps: int = DEFAULT_FPS,
        upscale_height: int = DEFAULT_UPSCALE_HEIGHT,
        upscale_width: int = DEFAULT_UPSCALE_WIDTH,
        upscale_strength: float = DEFAULT_UPSCALE_STRENGTH,
        upscale_guidance_scale: float = DEFAULT_UPSCALE_GUIDANCE_SCALE,
        upscale_num_inference_steps: int = DEFAULT_UPSCALE_NUM_INFERENCE_STEPS,
        use_improved_sampling: bool = False,
        improved_sampling_seed: Optional[int] = None,
        webhook: Optional[str] = None,
        track_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate a video from text using Modelslab's API.
        
        Args:
            text_prompt (str): The text description for video generation
            model_id (str): The model to use (cogvideox or wanx)
            negative_prompt (str): Items to avoid in the video
            height (int): Height of the video (max 512)
            width (int): Width of the video (max 512)
            num_frames (int): Number of frames (max 25)
            num_inference_steps (int): Number of denoising steps (max 50)
            guidance_scale (float): Scale for classifier-free guidance (0-8)
            output_type (str): Output format (mp4 or gif)
            fps (int): Frames per second (max 16)
            upscale_height (int): Height for upscaled video
            upscale_width (int): Width for upscaled video
            upscale_strength (float): Strength of upscaling (0-1)
            upscale_guidance_scale (float): Guidance scale for upscaling (0-8)
            upscale_num_inference_steps (int): Steps for upscaling (max 50)
            use_improved_sampling (bool): Whether to use improved sampling
            improved_sampling_seed (int): Seed for improved sampling
            webhook (str): URL for webhook callback
            track_id (str): ID for tracking the request
            
        Returns:
            str: URL of the generated video if successful, None otherwise
        """
        try:
            print("\n=== Starting Video Generation ===")
            print(f"Text Prompt: {text_prompt}")
            print(f"Model ID: {model_id}")
            print(f"Number of Frames: {num_frames}")
            print(f"Output Type: {output_type}")
            print(f"FPS: {fps}")
            
            # Validate parameters
            if not text_prompt:
                raise ValueError("Text prompt cannot be empty")
            
            if model_id not in ["cogvideox", "wanx"]:
                raise ValueError("Invalid model_id. Must be 'cogvideox' or 'wanx'")
            
            if height > 512 or width > 512:
                raise ValueError("Height and width cannot exceed 512 pixels")
            
            if num_frames > 25:
                raise ValueError("Number of frames cannot exceed 25")
            
            if num_inference_steps > 50:
                raise ValueError("Number of inference steps cannot exceed 50")
            
            if guidance_scale < 0 or guidance_scale > 8:
                raise ValueError("Guidance scale must be between 0 and 8")
            
            if output_type not in ["mp4", "gif"]:
                raise ValueError("Output type must be 'mp4' or 'gif'")
            
            if fps > 16:
                raise ValueError("FPS cannot exceed 16")
            
            # Prepare the request payload
            payload = {
                "key": self.api_key,
                "model_id": model_id,
                "prompt": text_prompt,
                "negative_prompt": negative_prompt,
                "height": height,
                "width": width,
                "num_frames": num_frames,
                "num_inference_steps": num_inference_steps,
                "guidance_scale": guidance_scale,
                "output_type": output_type,
                "fps": fps,
                "upscale_height": upscale_height,
                "upscale_width": upscale_width,
                "upscale_strength": upscale_strength,
                "upscale_guidance_scale": upscale_guidance_scale,
                "upscale_num_inference_steps": upscale_num_inference_steps,
                "use_improved_sampling": "yes" if use_improved_sampling else "no",
                "webhook": webhook,
                "track_id": track_id
            }
            
            if improved_sampling_seed is not None:
                payload["improved_sampling_seed"] = improved_sampling_seed
            
            print("\n=== API Request Payload ===")
            print(json.dumps(payload, indent=2))
            
            # Make the API request
            print("\n=== Making API Request ===")
            print(f"URL: {self.API_URL}")
            response = requests.post(
                self.API_URL,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            print("\n=== API Response ===")
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {response.headers}")
            print(f"Response Content: {response.text}")
            
            response.raise_for_status()
            
            # Parse the response
            result = response.json()
            
            print("\n=== Parsed Response ===")
            print(f"Status: {result.get('status')}")
            print(f"Message: {result.get('message')}")
            print(f"Output: {result.get('output')}")
            print(f"ETA: {result.get('eta')}")
            print(f"Fetch Result URL: {result.get('fetch_result')}")
            
            if result["status"] == "processing":
                print("\n=== Video Processing ===")
                print(f"ETA: {result.get('eta')} seconds")
                print(f"Fetch URL: {result.get('fetch_result')}")
                print(f"Future Video URL: {result.get('future_links', [])[0] if result.get('future_links') else 'Not available yet'}")
                
                # Return the future video URL and fetch URL for the caller to handle
                return {
                    "status": "processing",
                    "eta": result.get("eta"),
                    "fetch_url": result.get("fetch_result"),
                    "future_video_url": result.get("future_links", [])[0] if result.get("future_links") else None
                }
            elif result["status"] == "success":
                video_url = result["output"][0] if result["output"] else None
                print(f"\n=== Video URL ===")
                print(f"Generated Video URL: {video_url}")
                return video_url
            else:
                print("\n=== Error Status ===")
                print(f"Error Message: {result.get('message')}")
                return None
                
        except requests.exceptions.RequestException as e:
            print("\n=== Request Exception ===")
            print(f"Error: {str(e)}")
            print(f"Response: {e.response.text if hasattr(e, 'response') else 'No response'}")
            return None
        except Exception as e:
            print("\n=== General Exception ===")
            print(f"Error: {str(e)}")
            print(f"Error Type: {type(e)}")
            return None 