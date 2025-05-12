import streamlit as st
import os
import sys
from dotenv import load_dotenv
from pymongo import MongoClient
import pandas as pd
from datetime import datetime, timedelta
import requests # Needed for download button
import time

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.ingest.youtube_fetcher import YouTubeFetcher
from backend.generation.content_generator import ContentGenerator
from backend.generation.vadoo_generator import ModelslabVideoGenerator

# Load environment variables
load_dotenv()

# MongoDB connection
client = MongoClient(os.getenv("MONGO_URI"))
db = client.social_media_automation
trending_videos_collection = db.trending_videos
managed_videos_collection = db.managed_videos # Collection for user-managed videos

# Initialize Generators
content_generator = ContentGenerator()
try:
    video_generator = ModelslabVideoGenerator() # Initialize Modelslab video generator
except ValueError as e:
    st.error(f"Failed to initialize Video Generator: {e}") # Show error if API key missing
    video_generator = None

# YouTube category mapping
CATEGORY_NAMES = {
    '1': 'Film & Animation', '2': 'Autos & Vehicles', '10': 'Music', '15': 'Pets & Animals',
    '17': 'Sports', '19': 'Travel & Events', '20': 'Gaming', '22': 'People & Blogs',
    '23': 'Comedy', '24': 'Entertainment', '25': 'News & Politics', '26': 'Howto & Style',
    '27': 'Education', '28': 'Science & Technology', '29': 'Nonprofits & Activism'
}

def main():
    st.set_page_config(page_title="Social Media Automation", layout="wide")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Go to", ["Dashboard", "Content Analysis & Generation", "Video Management"])
    
    if page == "Dashboard":
        show_dashboard()
    elif page == "Content Analysis & Generation":
        show_content_analysis_and_generation()
    elif page == "Video Management":
        show_video_management()

def show_dashboard():
    st.title("Dashboard")
    
    # Fetch managed videos (videos we've posted)
    managed_videos = list(managed_videos_collection.find().sort("upload_date", -1))
    
    if managed_videos:
        st.subheader("Your Posted Videos")
        for video in managed_videos:
            with st.expander(f"{video['title']} - {video['upload_date'].strftime('%Y-%m-%d')}"):
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.write(f"Description: {video['description']}")
                    st.write(f"Tags: {', '.join(video.get('tags', []))}")
                    st.write(f"Status: {video.get('status', 'Unknown')}")
                with col2:
                    if 'thumbnail_url' in video:
                        st.image(video['thumbnail_url'], width=200)
                    st.write(f"Views: {video.get('views', 0):,}")
                    st.write(f"Likes: {video.get('likes', 0):,}")
                    st.write(f"Comments: {video.get('comments', 0):,}")
    else:
        st.info("No videos posted yet. Use the Video Management section to upload your first video.")
    
    # Video insights section
    st.subheader("Video Insights")
    if managed_videos:
        # Calculate overall metrics
        total_views = sum(v.get('views', 0) for v in managed_videos)
        total_likes = sum(v.get('likes', 0) for v in managed_videos)
        total_comments = sum(v.get('comments', 0) for v in managed_videos)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Views", f"{total_views:,}")
        with col2:
            st.metric("Total Likes", f"{total_likes:,}")
        with col3:
            st.metric("Total Comments", f"{total_comments:,}")
        
        # Engagement rate analysis
        avg_engagement = (total_likes + total_comments) / total_views if total_views > 0 else 0
        st.metric("Average Engagement Rate", f"{avg_engagement:.2%}")
    else:
        st.info("No insights available yet. Upload videos to see performance metrics.")

def show_content_analysis_and_generation():
    st.title("Content Analysis & Generation")
    
    # Part 1: Content Analysis
    st.header("1. Analyze Trending Content")
    
    # Fetch parameters
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        max_results = st.number_input("Number of videos to fetch", min_value=5, max_value=50, value=20)
    with col2:
        region_code = st.selectbox("Region", ["IN", "US", "GB", "CA", "AU"], index=0)
    with col3:
        language = st.selectbox("Language", ["hi", "en", "es", "fr"], index=0)
    with col4:
        days_old = st.number_input("Days old", min_value=1, max_value=30, value=7)
    
    if st.button("Fetch & Analyze Trending Videos"):
        with st.spinner("Fetching and analyzing trending videos..."):
            youtube_fetcher = YouTubeFetcher()
            videos = youtube_fetcher.fetch_trending_videos(
                max_results=max_results,
                region_code=region_code,
                language=language,
                days_old=days_old
            )
            
            if videos:
                # Display fetched videos first
                st.subheader(f"📊 Fetched {len(videos)} Trending Videos")
                for idx, video in enumerate(videos, 1):
                    with st.expander(f"{idx}. {video['title']} ({video['views']:,} views)"):
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            st.write("📝 **Description:**")
                            st.write(video['description'][:200] + "..." if len(video['description']) > 200 else video['description'])
                            st.write(f"🏷️ **Tags:** {', '.join(video['tags'][:5])}..." if video['tags'] else "No tags")
                            st.write(f"📺 **Channel:** {video['channel_title']}")
                        with col2:
                            st.write(f"⏱️ **Duration:** {video['duration_formatted']}")
                            st.write(f"👁️ **Views:** {video['views']:,}")
                            st.write(f"👍 **Likes:** {video['likes']:,}")
                            st.write(f"💬 **Comments:** {video['comments']:,}")
                            engagement = (video['likes'] + video['comments']) / video['views'] if video['views'] > 0 else 0
                            st.write(f"📈 **Engagement:** {engagement:.2%}")
                
                # Then show the analysis
                analysis = youtube_fetcher.analyze_video_performance(videos)
                
                st.markdown("---")
                st.subheader("📊 Content Analysis Summary")
                
                # Display analysis results in columns
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("🎯 Top Categories")
                    for category_id, count in analysis['top_categories'].items():
                        category_name = CATEGORY_NAMES.get(category_id, f'Category {category_id}')
                        st.write(f"• {category_name}: {count} videos")
                
                with col2:
                    st.subheader("🏷️ Common Tags")
                    for tag, count in analysis['common_tags'].items():
                        st.write(f"• #{tag}: {count} times")
                
                st.markdown("---")
                st.subheader("📈 Performance Metrics")
                metrics_col1, metrics_col2 = st.columns(2)
                with metrics_col1:
                    st.write(f"⏱️ **Average Duration:** {timedelta(seconds=int(analysis['average_duration_seconds']))}")
                with metrics_col2:
                    st.write(f"📊 **Average Engagement Rate:** {analysis['average_engagement_rate']:.2%}")
                
                # Key Takeaways
                st.markdown("---")
                st.subheader("🔑 Key Takeaways")
                
                # Calculate optimal duration range
                duration_min = timedelta(seconds=int(analysis['average_duration_seconds'] * 0.8))
                duration_max = timedelta(seconds=int(analysis['average_duration_seconds'] * 1.2))
                
                # Get top category name
                top_category_id = list(analysis['top_categories'].keys())[0]
                top_category_name = CATEGORY_NAMES.get(top_category_id, f'Category {top_category_id}')
                
                # Get top 3 tags
                top_tags = list(analysis['common_tags'].keys())[:3]
                
                st.write("For best performance, consider these insights:")
                st.write(f"1. 🎬 **Optimal Video Duration:** {duration_min} to {duration_max}")
                st.write(f"2. 📺 **Most Popular Category:** {top_category_name}")
                st.write(f"3. 🏷️ **Recommended Tags:** #{', #'.join(top_tags)}")
                st.write(f"4. 📊 **Target Engagement Rate:** > {analysis['average_engagement_rate']:.2%}")
                
                # Store analysis results in session state
                st.session_state.analysis_results = analysis
            else:
                st.error("Failed to fetch trending videos. Please check your API key and try again.")
    
    # Part 2: Content Generation
    st.markdown("---")
    st.header("2. Generate New Content")
    st.info("Use the analysis above to guide your inputs below.")
    
    with st.form("content_generation_form"):
        gen_topic = st.text_input("Topic/Keywords")
        gen_type = "Video Script"  # Fixed to Video Script only
        gen_tone = st.selectbox("Tone", ["Professional", "Casual", "Humorous", "Educational"])
        gen_length = st.selectbox("Length", ["Short", "Medium", "Long"])
        gen_story = st.text_area("Story Summary (Optional)")
        
        submitted = st.form_submit_button("Generate Content")
        
        if submitted:
            if not gen_topic and not gen_story:
                st.error("Please provide at least a Topic/Keywords or a Story Summary.")
            else:
                with st.spinner("Generating content..."):
                    current_analysis = st.session_state.get('analysis_results', {})
                    generated_content = content_generator.generate_content(
                        gen_topic, gen_type, gen_tone, gen_length, gen_story, current_analysis
                    )
                    
                    # Store the generated content in session state
                    st.session_state.generated_content = generated_content
                    st.session_state.show_video_button = True

    # Display generated content and video generation button outside the form
    if hasattr(st.session_state, 'generated_content'):
        gen_result = st.session_state.generated_content
        if isinstance(gen_result, dict) and 'video_prompt' in gen_result:
            st.subheader("Generated Video Prompt & Details")
            st.markdown(f"**Video Prompt:** {gen_result['video_prompt']}")
            st.markdown(f"**Video Length:** {ModelslabVideoGenerator.DURATIONS.get(gen_result['video_length'], gen_result['video_length'] + ' seconds')}")
            st.markdown(f"**Tags/Concepts:** {' '.join(['#'+tag for tag in gen_result['tags']]) if gen_result['tags'] else 'None'}")
            
            # Video generation option
            if video_generator and hasattr(st.session_state, 'show_video_button'):
                # Only duration selection is needed for Modelslab
                duration = st.selectbox(
                    "Video Duration",
                    options=list(ModelslabVideoGenerator.DURATIONS.keys()),
                    format_func=lambda x: ModelslabVideoGenerator.DURATIONS[x],
                    index=list(ModelslabVideoGenerator.DURATIONS.keys()).index(gen_result['video_length']) if gen_result['video_length'] in ModelslabVideoGenerator.DURATIONS else 1
                )
                if st.button("Generate Video"):
                    with st.spinner("Generating video... This may take a few minutes."):
                        try:
                            print("\n=== Starting Video Generation Process ===")
                            print(f"Content Type: {gen_type}")
                            print(f"Topic: {gen_topic}")
                            print(f"Tone: {gen_tone}")
                            print(f"Length: {gen_length}")
                            print(f"Story: {gen_story}")
                            
                            # Map duration to num_frames (approx: 2 sec = 8 frames at 4 fps, 4 sec = 16, 6 sec = 24, etc.)
                            duration_to_frames = {
                                "30": 16,  # 30 seconds
                                "60": 25,  # 1 minute
                                "90": 25,  # 1.5 minutes
                                "120": 25, # 2 minutes
                                "180": 25, # 3 minutes
                                "300": 25  # 5 minutes
                            }
                            num_frames = duration_to_frames.get(duration, 16)
                            print(f"\n=== Video Generation Parameters ===")
                            print(f"Selected Duration: {duration} seconds")
                            print(f"Calculated Frames: {num_frames}")
                            
                            print("\n=== Calling Video Generator ===")
                            video_result = video_generator.generate_video_from_text(
                                text_prompt=gen_result['video_prompt'],
                                num_frames=num_frames,
                                output_type="mp4",
                                fps=7
                            )
                            
                            print("\n=== Video Generation Result ===")
                            print(f"Result: {video_result}")
                            
                            if isinstance(video_result, dict) and video_result.get("status") == "processing":
                                print("\n=== Video is Processing ===")
                                eta = video_result['eta']
                                st.info(f"Video is being generated. Estimated time: {eta} seconds")
                                
                                # Get the fetch URL from the response
                                fetch_url = video_result['fetch_url']
                                
                                # Create a placeholder for the video
                                video_placeholder = st.empty()
                                
                                # Wait for the initial ETA before starting to poll
                                print(f"\n=== Waiting for initial ETA: {eta} seconds ===")
                                time.sleep(eta)
                                
                                # Poll for the result using the fetch URL
                                max_attempts = 10
                                attempt = 0
                                while attempt < max_attempts:
                                    try:
                                        print(f"\n=== Polling Attempt {attempt + 1} ===")
                                        print(f"Fetching from URL: {fetch_url}")
                                        fetch_response = requests.get(fetch_url)
                                        fetch_response.raise_for_status()
                                        fetch_result = fetch_response.json()
                                        
                                        print(f"Fetch Response: {fetch_result}")
                                        
                                        if fetch_result.get("status") == "success":
                                            # Get the video URL from the fetch result's output array
                                            video_url = fetch_result.get("output", [])[0]
                                            if video_url:
                                                print("\n=== Video Generated Successfully ===")
                                                print(f"Video URL: {video_url}")
                                                st.success("Video generated successfully!")
                                                video_placeholder.video(video_url)
                                                try:
                                                    print("\n=== Attempting to Download Video ===")
                                                    video_response = requests.get(video_url, stream=True)
                                                    video_response.raise_for_status()
                                                    print("Video download successful")
                                                    st.download_button(
                                                        label="Download Video",
                                                        data=video_response.content,
                                                        file_name="generated_video.mp4",
                                                        mime="video/mp4"
                                                    )
                                                except requests.exceptions.RequestException as e:
                                                    print("\n=== Download Error ===")
                                                    print(f"Error: {str(e)}")
                                                    st.error(f"Could not download video: {str(e)}")
                                            break
                                        elif fetch_result.get("status") == "processing":
                                            new_eta = fetch_result.get('eta', 5)
                                            print(f"Still processing... New ETA: {new_eta} seconds")
                                            time.sleep(new_eta)  # Wait for the new ETA before next attempt
                                            attempt += 1
                                        else:
                                            print("\n=== Error in Fetch Response ===")
                                            print(f"Error Message: {fetch_result.get('message')}")
                                            st.error(f"Error during video generation: {fetch_result.get('message')}")
                                            break
                                    except requests.exceptions.RequestException as e:
                                        print(f"\n=== Polling Error ===")
                                        print(f"Error: {str(e)}")
                                        st.error(f"Error while checking video status: {str(e)}")
                                        break
                                
                                if attempt >= max_attempts:
                                    st.warning("Video generation is taking longer than expected. Please check back later.")
                            elif isinstance(video_result, str) and video_result:
                                print("\n=== Video Generated Successfully ===")
                                st.success("Video generated successfully!")
                                st.video(video_result)
                                try:
                                    print("\n=== Attempting to Download Video ===")
                                    video_response = requests.get(video_result, stream=True)
                                    video_response.raise_for_status()
                                    print("Video download successful")
                                    st.download_button(
                                        label="Download Video",
                                        data=video_response.content,
                                        file_name="generated_video.mp4",
                                        mime="video/mp4"
                                    )
                                except requests.exceptions.RequestException as e:
                                    print("\n=== Download Error ===")
                                    print(f"Error: {str(e)}")
                                    st.error(f"Could not download video: {str(e)}")
                            else:
                                print("\n=== Video Generation Failed ===")
                                st.error("Failed to generate video. Please check the logs for details.")
                                st.info("This could be due to:\n"
                                       "1. API key issues\n"
                                       "2. Network connectivity\n"
                                       "3. Server limitations\n"
                                       "4. Content restrictions\n"
                                       "Please try again or try with a different prompt.")
                        except Exception as e:
                            print("\n=== Video Generation Exception ===")
                            print(f"Error: {str(e)}")
                            print(f"Error Type: {type(e)}")
                            st.error(f"An error occurred during video generation: {str(e)}")
        else:
            st.warning("Old or invalid content detected. Please generate new content.")
            if st.button("Clear Generated Content"):
                del st.session_state.generated_content
                st.experimental_rerun()

def show_video_management():
    st.title("Video Management")
    
    # Upload new video
    st.header("Upload New Video")
    with st.form("video_upload_form"):
        title = st.text_input("Video Title")
        description = st.text_area("Description")
        tags = st.text_input("Tags (comma-separated)")
        video_file = st.file_uploader("Video File", type=['mp4', 'mov'])
        
        if st.form_submit_button("Upload"):
            if video_file:
                tags_list = [tag.strip() for tag in tags.split(',')] if tags else []
                upload_video(title, description, tags_list, video_file)
            else:
                st.error("Please select a video file to upload.")

def upload_video(title, description, tags, video_file):
    # TODO: Implement YouTube upload functionality
    st.info("Uploading video... This feature will be implemented soon.")
    # After successful upload, add to managed_videos_collection
    video_data = {
        "title": title,
        "description": description,
        "tags": tags,
        "upload_date": datetime.now(),
        "status": "Uploaded",
        "platform": "YouTube"
    }
    managed_videos_collection.insert_one(video_data)
    st.success("Video uploaded successfully!")

if __name__ == "__main__":
    main() 