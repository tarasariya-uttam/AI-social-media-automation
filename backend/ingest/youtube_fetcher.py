import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime, timedelta
import isodate

load_dotenv()

class YouTubeFetcher:
    def __init__(self):
        self.api_key = os.getenv("YOUTUBE_API_KEY")
        if not self.api_key:
            raise ValueError("YOUTUBE_API_KEY environment variable not set")
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)
    
    def fetch_trending_videos(self, max_results=20, region_code='IN', language='hi', days_old=7):
        try:
            # Calculate threshold date
            threshold_date = (datetime.utcnow() - timedelta(days=days_old)).isoformat() + 'Z'
            
            # First get video IDs from search
            search_request = self.youtube.search().list(
                part="id",
                type="video",
                order="viewCount",
                publishedAfter=threshold_date,
                regionCode=region_code,
                relevanceLanguage=language,
                maxResults=max_results * 2  # Get more results to filter
            )
            search_response = search_request.execute()
            
            # Extract video IDs
            video_ids = [item['id']['videoId'] for item in search_response['items']]
            
            # Get detailed video information
            videos_request = self.youtube.videos().list(
                part="snippet,contentDetails,statistics",
                id=','.join(video_ids)
            )
            videos_response = videos_request.execute()
            
            videos = []
            for item in videos_response['items']:
                # Convert duration from ISO 8601 to seconds
                duration = isodate.parse_duration(item['contentDetails']['duration']).total_seconds()
                
                video_data = {
                    'video_id': item['id'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'published_at': item['snippet']['publishedAt'],
                    'channel_id': item['snippet']['channelId'],
                    'channel_title': item['snippet']['channelTitle'],
                    'views': int(item['statistics'].get('viewCount', 0)),
                    'likes': int(item['statistics'].get('likeCount', 0)),
                    'comments': int(item['statistics'].get('commentCount', 0)),
                    'duration_seconds': duration,
                    'duration_formatted': str(timedelta(seconds=int(duration))),
                    'tags': item['snippet'].get('tags', []),
                    'category_id': item['snippet']['categoryId']
                }
                videos.append(video_data)
            
            # Sort by views and take top max_results
            videos = sorted(videos, key=lambda x: x['views'], reverse=True)[:max_results]
            
            return videos
            
        except HttpError as e:
            print(f"An HTTP error occurred: {e}")
            return []
    
    def analyze_video_performance(self, videos):
        # Convert to DataFrame for analysis
        df = pd.DataFrame(videos)
        
        # Calculate engagement metrics
        df['engagement_rate'] = (df['likes'] + df['comments']) / df['views']
        
        # Sort by views and engagement rate
        top_videos = df.sort_values(['views', 'engagement_rate'], ascending=[False, False]).head(10)
        
        # Analyze common patterns
        analysis = {
            'average_duration_seconds': df['duration_seconds'].mean(),
            'common_tags': df['tags'].explode().value_counts().head(5).to_dict(),
            'top_categories': df['category_id'].value_counts().head(3).to_dict(),
            'average_engagement_rate': df['engagement_rate'].mean(),
            'top_videos': top_videos.to_dict('records')
        }
        
        return analysis
    
    def get_video_details(self, video_id):
        try:
            request = self.youtube.videos().list(
                part="snippet,statistics,contentDetails",
                id=video_id
            )
            response = request.execute()
            
            if response['items']:
                item = response['items'][0]
                duration = isodate.parse_duration(item['contentDetails']['duration']).total_seconds()
                return {
                    'video_id': item['id'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'views': int(item['statistics'].get('viewCount', 0)),
                    'likes': int(item['statistics'].get('likeCount', 0)),
                    'comments': int(item['statistics'].get('commentCount', 0)),
                    'duration_seconds': duration,
                    'duration_formatted': str(timedelta(seconds=int(duration)))
                }
            return None
            
        except HttpError as e:
            print(f"An HTTP error occurred: {e}")
            return None 