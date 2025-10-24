import pickle
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
from datetime import datetime
import json
import time
import plotly.graph_objects as go
import plotly.express as px
from collections import Counter
import random

# Page configuration
st.set_page_config(
    page_title="MusicVerse - AI Music Discovery",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Advanced Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    /* Animated gradient background */
    .stApp {
        background: linear-gradient(-45deg, #0f0c29, #302b63, #24243e, #0f0c29);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
    }
    
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Glassmorphism header */
    .hero-header {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 25px;
        padding: 3rem 2rem;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 20px 60px rgba(0,0,0,0.5);
        position: relative;
        overflow: hidden;
    }
    
    .hero-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(29,185,84,0.1) 0%, transparent 70%);
        animation: pulse 8s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 0.5; }
        50% { transform: scale(1.2); opacity: 0.8; }
    }
    
    .hero-header h1 {
        color: #fff;
        font-size: 4rem;
        font-weight: 800;
        margin: 0;
        text-shadow: 0 0 30px rgba(29,185,84,0.5), 0 0 60px rgba(29,185,84,0.3);
        background: linear-gradient(45deg, #1DB954, #1ed760, #1DB954);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: glow 2s ease-in-out infinite alternate;
        position: relative;
        z-index: 1;
    }
    
    @keyframes glow {
        from { filter: drop-shadow(0 0 10px #1DB954); }
        to { filter: drop-shadow(0 0 20px #1ed760); }
    }
    
    .hero-subtitle {
        color: rgba(255,255,255,0.8);
        font-size: 1.3rem;
        margin-top: 1rem;
        position: relative;
        z-index: 1;
    }
    
    /* Neon song cards */
    .neon-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(15px);
        border: 2px solid rgba(29, 185, 84, 0.3);
        border-radius: 20px;
        padding: 1.8rem;
        margin: 1.5rem 0;
        box-shadow: 
            0 0 20px rgba(29, 185, 84, 0.2),
            0 15px 35px rgba(0,0,0,0.5),
            inset 0 0 20px rgba(29, 185, 84, 0.05);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        position: relative;
        overflow: hidden;
    }
    
    .neon-card::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(45deg, #1DB954, #1ed760, #1DB954);
        border-radius: 20px;
        opacity: 0;
        z-index: -1;
        transition: opacity 0.4s;
    }
    
    .neon-card:hover {
        transform: translateY(-10px) scale(1.02);
        border-color: rgba(29, 185, 84, 0.8);
        box-shadow: 
            0 0 40px rgba(29, 185, 84, 0.6),
            0 20px 50px rgba(0,0,0,0.7),
            inset 0 0 30px rgba(29, 185, 84, 0.1);
    }
    
    .neon-card:hover::before {
        opacity: 0.2;
    }
    
    /* Animated music waves */
    .music-wave {
        display: inline-block;
        width: 4px;
        height: 20px;
        background: linear-gradient(180deg, #1DB954, #1ed760);
        margin: 0 2px;
        border-radius: 2px;
        animation: wave 1s ease-in-out infinite;
    }
    
    .music-wave:nth-child(2) { animation-delay: 0.1s; }
    .music-wave:nth-child(3) { animation-delay: 0.2s; }
    .music-wave:nth-child(4) { animation-delay: 0.3s; }
    .music-wave:nth-child(5) { animation-delay: 0.4s; }
    
    @keyframes wave {
        0%, 100% { height: 20px; }
        50% { height: 40px; }
    }
    
    /* Song title with gradient */
    .song-title-neon {
        background: linear-gradient(135deg, #1DB954 0%, #1ed760 50%, #fff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 1.6rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        text-shadow: 0 0 30px rgba(29,185,84,0.5);
    }
    
    .artist-name {
        color: rgba(255,255,255,0.7);
        font-size: 1.1rem;
        font-weight: 500;
        margin-bottom: 1rem;
    }
    
    /* Glassmorphism stats */
    .glass-stat {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .glass-stat:hover {
        background: rgba(255, 255, 255, 0.1);
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(29,185,84,0.3);
    }
    
    .stat-value {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #1DB954, #1ed760);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .stat-label {
        color: rgba(255,255,255,0.7);
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-top: 0.5rem;
    }
    
    /* Neon buttons */
    .stButton>button {
        background: linear-gradient(135deg, #1DB954 0%, #1ed760 100%);
        color: white;
        border: none;
        padding: 0.8rem 2.5rem;
        border-radius: 50px;
        font-weight: 700;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 0 20px rgba(29,185,84,0.5);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 0 40px rgba(29,185,84,0.8), 0 10px 30px rgba(0,0,0,0.3);
        background: linear-gradient(135deg, #1ed760 0%, #1DB954 100%);
    }
    
    /* Album art with glow */
    .album-glow {
        border-radius: 15px;
        box-shadow: 0 0 30px rgba(29,185,84,0.4), 0 15px 40px rgba(0,0,0,0.6);
        transition: all 0.4s ease;
    }
    
    .album-glow:hover {
        transform: scale(1.08) rotate(2deg);
        box-shadow: 0 0 50px rgba(29,185,84,0.8), 0 20px 60px rgba(0,0,0,0.8);
    }
    
    /* Progress bars */
    .progress-bar {
        height: 8px;
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
        overflow: hidden;
        margin: 0.5rem 0;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #1DB954, #1ed760);
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(29,185,84,0.8);
        animation: shimmer 2s infinite;
    }
    
    @keyframes shimmer {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    
    /* Feature badges */
    .feature-badge-glow {
        display: inline-block;
        background: rgba(29,185,84,0.2);
        border: 2px solid #1DB954;
        color: #1ed760;
        padding: 0.5rem 1.2rem;
        border-radius: 30px;
        font-size: 0.85rem;
        font-weight: 700;
        margin: 0.3rem;
        box-shadow: 0 0 15px rgba(29,185,84,0.4);
        transition: all 0.3s ease;
    }
    
    .feature-badge-glow:hover {
        background: rgba(29,185,84,0.4);
        box-shadow: 0 0 25px rgba(29,185,84,0.8);
        transform: scale(1.05);
    }
    
    /* Playlist items */
    .playlist-item-glass {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border-left: 4px solid #1DB954;
        padding: 1rem;
        margin: 0.8rem 0;
        border-radius: 12px;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    }
    
    .playlist-item-glass:hover {
        background: rgba(255, 255, 255, 0.08);
        transform: translateX(10px);
        box-shadow: 0 8px 25px rgba(29,185,84,0.3);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: rgba(255, 255, 255, 0.03);
        padding: 10px;
        border-radius: 15px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        color: rgba(255,255,255,0.7);
        padding: 12px 24px;
        font-weight: 600;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #1DB954, #1ed760);
        color: white;
        box-shadow: 0 0 20px rgba(29,185,84,0.5);
    }
    
    /* Metric cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(29, 185, 84, 0.3);
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.4);
    }
    
    /* Audio player styling */
    audio {
        width: 100%;
        filter: brightness(0.8) contrast(1.2);
    }
    
    /* Info box */
    .info-box-glow {
        background: rgba(29, 185, 84, 0.1);
        border: 2px solid rgba(29, 185, 84, 0.5);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 0 20px rgba(29,185,84,0.3);
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255,255,255,0.05);
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #1DB954, #1ed760);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #1ed760, #1DB954);
    }
    
    /* Loading animation */
    .loading-dots {
        display: inline-block;
    }
    
    .loading-dots span {
        display: inline-block;
        width: 8px;
        height: 8px;
        background: #1DB954;
        border-radius: 50%;
        margin: 0 3px;
        animation: loading 1.4s infinite both;
    }
    
    .loading-dots span:nth-child(2) { animation-delay: 0.2s; }
    .loading-dots span:nth-child(3) { animation-delay: 0.4s; }
    
    @keyframes loading {
        0%, 80%, 100% { transform: scale(0); opacity: 0.5; }
        40% { transform: scale(1); opacity: 1; }
    }
    
    /* Genre tags */
    .genre-tag {
        display: inline-block;
        background: linear-gradient(135deg, rgba(29,185,84,0.2), rgba(29,185,84,0.4));
        border: 1px solid #1DB954;
        color: #fff;
        padding: 0.3rem 1rem;
        border-radius: 20px;
        margin: 0.2rem;
        font-size: 0.8rem;
        font-weight: 600;
        box-shadow: 0 0 10px rgba(29,185,84,0.3);
    }
</style>
""", unsafe_allow_html=True)

# Initialize Spotify
CLIENT_ID = "70a9fb89662f4dac8d07321b259eaad7"
CLIENT_SECRET = "4d6710460d764fbbb8d8753dc094d131"

@st.cache_resource
def init_spotify():
    client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    return spotipy.Spotify(client_credentials_manager=client_credentials_manager)

sp = init_spotify()

# Initialize session state with more features
if 'playlist' not in st.session_state:
    st.session_state.playlist = []
if 'history' not in st.session_state:
    st.session_state.history = []
if 'liked_songs' not in st.session_state:
    st.session_state.liked_songs = []
if 'listening_time' not in st.session_state:
    st.session_state.listening_time = 0
if 'recommendations_count' not in st.session_state:
    st.session_state.recommendations_count = 0
if 'favorite_genres' not in st.session_state:
    st.session_state.favorite_genres = []
if 'mood_history' not in st.session_state:
    st.session_state.mood_history = []
if 'artist_stats' not in st.session_state:
    st.session_state.artist_stats = {}

# Load data
@st.cache_data
def load_data():
    try:
        music = pickle.load(open('df1.pkl', 'rb'))
        similarity = pickle.load(open('similarity.pkl', 'rb'))
        return music, similarity
    except:
        st.error("⚠️ Please ensure 'df1.pkl' and 'similarity.pkl' are in the same directory")
        st.stop()

music, similarity = load_data()

# Enhanced functions
def get_audio_features(track_id):
    """Get audio features from Spotify"""
    try:
        features = sp.audio_features(track_id)[0]
        if features:
            return {
                'energy': features.get('energy', 0) * 100,
                'danceability': features.get('danceability', 0) * 100,
                'valence': features.get('valence', 0) * 100,
                'acousticness': features.get('acousticness', 0) * 100,
                'tempo': features.get('tempo', 0)
            }
    except:
        pass
    return None

def get_song_details(song_name, artist_name):
    """Enhanced song details"""
    try:
        search_query = f"track:{song_name} artist:{artist_name}"
        results = sp.search(q=search_query, type="track", limit=1)
        
        if results and results["tracks"]["items"]:
            track = results["tracks"]["items"][0]
            audio_features = get_audio_features(track['id'])
            
            return {
                'album_cover': track["album"]["images"][0]["url"] if track["album"]["images"] else None,
                'preview_url': track.get("preview_url"),
                'spotify_url': track["external_urls"]["spotify"],
                'popularity': track.get("popularity", 0),
                'duration': track.get("duration_ms", 0) // 1000,
                'release_date': track["album"].get("release_date", "N/A"),
                'track_id': track['id'],
                'audio_features': audio_features,
                'album_name': track["album"]["name"],
                'genres': track.get('genres', [])
            }
    except:
        pass
    return None

def recommend(song, num_recommendations=5):
    """Generate recommendations"""
    try:
        index = music[music['song'] == song].index[0]
        distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
        
        recommended_songs = []
        for i in distances[1:num_recommendations+1]:
            song_data = music.iloc[i[0]]
            details = get_song_details(song_data.song, song_data.artist)
            
            recommended_songs.append({
                'name': song_data.song,
                'artist': song_data.artist,
                'similarity_score': distances[i[0]][1] * 100,
                'details': details
            })
        
        st.session_state.recommendations_count += 1
        return recommended_songs
    except:
        return []

def create_audio_features_chart(features):
    """Create radar chart for audio features"""
    if not features:
        return None
    
    categories = ['Energy', 'Danceability', 'Valence', 'Acousticness']
    values = [
        features['energy'],
        features['danceability'],
        features['valence'],
        features['acousticness']
    ]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        line=dict(color='#1DB954', width=3),
        fillcolor='rgba(29, 185, 84, 0.3)',
        name='Audio Features'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                gridcolor='rgba(255,255,255,0.2)',
                tickfont=dict(color='white')
            ),
            angularaxis=dict(
                gridcolor='rgba(255,255,255,0.2)',
                tickfont=dict(color='white', size=12)
            ),
            bgcolor='rgba(0,0,0,0)'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        height=300,
        margin=dict(t=40, b=40, l=40, r=40)
    )
    
    return fig

def create_stats_chart():
    """Create user statistics chart"""
    if not st.session_state.history:
        return None
    
    # Count artist frequency
    artists = [music[music['song'] == song]['artist'].values[0] for song in st.session_state.history if len(music[music['song'] == song]) > 0]
    artist_counts = Counter(artists).most_common(5)
    
    if not artist_counts:
        return None
    
    fig = go.Figure(data=[
        go.Bar(
            x=[count for _, count in artist_counts],
            y=[artist for artist, _ in artist_counts],
            orientation='h',
            marker=dict(
                color='#1DB954',
                line=dict(color='#1ed760', width=2)
            ),
            text=[count for _, count in artist_counts],
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title=dict(text='🎤 Your Top Artists', font=dict(color='white', size=20)),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(gridcolor='rgba(255,255,255,0.1)', color='white'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.1)', color='white'),
        height=300,
        margin=dict(t=60, b=40, l=40, r=40)
    )
    
    return fig

def create_listening_pattern():
    """Create listening pattern visualization"""
    if len(st.session_state.history) < 3:
        return None
    
    # Simulate time-based data
    times = list(range(len(st.session_state.history)))
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=times,
        y=list(range(len(st.session_state.history))),
        mode='lines+markers',
        line=dict(color='#1DB954', width=3, shape='spline'),
        marker=dict(size=10, color='#1ed760', line=dict(color='white', width=2)),
        fill='tozeroy',
        fillcolor='rgba(29, 185, 84, 0.2)'
    ))
    
    fig.update_layout(
        title=dict(text='📈 Your Discovery Journey', font=dict(color='white', size=20)),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(title='Sessions', gridcolor='rgba(255,255,255,0.1)', color='white'),
        yaxis=dict(title='Songs Discovered', gridcolor='rgba(255,255,255,0.1)', color='white'),
        height=300,
        margin=dict(t=60, b=40, l=40, r=40)
    )
    
    return fig

# Animated Header
st.markdown("""
<div class="hero-header">
    <h1>🎵 MUSICVERSE</h1>
    <p class="hero-subtitle">AI-Powered Music Discovery Platform</p>
    <div style="margin-top: 1rem;">
        <span class="music-wave"></span>
        <span class="music-wave"></span>
        <span class="music-wave"></span>
        <span class="music-wave"></span>
        <span class="music-wave"></span>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar with enhanced features
with st.sidebar:
    st.markdown("## ⚙️ Control Center")
    
    # Settings
    with st.expander("🎛️ Recommendation Settings", expanded=True):
        num_recommendations = st.slider("Number of Songs", 3, 15, 6)
        show_audio_features = st.checkbox("Show Audio Analysis", value=True)
        show_preview = st.checkbox("Enable Previews", value=True)
        auto_play = st.checkbox("Auto-add to Playlist", value=False)
    
    st.markdown("---")
    
    # Real-time statistics
    st.markdown("## 📊 Your Stats")
    
    stats_col1, stats_col2 = st.columns(2)
    with stats_col1:
        st.markdown(f"""
        <div class="glass-stat">
            <div class="stat-value">{len(st.session_state.playlist)}</div>
            <div class="stat-label">Playlist</div>
        </div>
        """, unsafe_allow_html=True)
    
    with stats_col2:
        st.markdown(f"""
        <div class="glass-stat">
            <div class="stat-value">{len(st.session_state.liked_songs)}</div>
            <div class="stat-label">Liked</div>
        </div>
        """, unsafe_allow_html=True)
    
    stats_col3, stats_col4 = st.columns(2)
    with stats_col3:
        st.markdown(f"""
        <div class="glass-stat">
            <div class="stat-value">{len(st.session_state.history)}</div>
            <div class="stat-label">Searches</div>
        </div>
        """, unsafe_allow_html=True)
    
    with stats_col4:
        st.markdown(f"""
        <div class="glass-stat">
            <div class="stat-value">{st.session_state.recommendations_count}</div>
            <div class="stat-label">Sessions</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Recently played with animations
    if st.session_state.history:
        st.markdown("## 🕐 Recent History")
        for idx, song in enumerate(st.session_state.history[:5]):
            st.markdown(f"""
            <div class="playlist-item-glass">
                <strong>#{idx+1}</strong> {song}
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick actions
    st.markdown("## ⚡ Quick Actions")
    if st.button("🔄 Shuffle Recommendations", use_container_width=True):
        if st.session_state.history:
            random_song = random.choice(st.session_state.history)
            st.session_state['random_recommendation'] = random_song
    
    if st.button("🗑️ Clear All Data", use_container_width=True):
        st.session_state.playlist = []
        st.session_state.history = []
        st.session_state.liked_songs = []
        st.rerun()
    
    if st.button("📥 Export Analytics", use_container_width=True):
        analytics = {
            'total_searches': len(st.session_state.history),
            'playlist_size': len(st.session_state.playlist),
            'liked_songs': len(st.session_state.liked_songs),
            'recommendation_sessions': st.session_state.recommendations_count
        }
        st.download_button(
            "Download JSON",
            json.dumps(analytics, indent=2),
            "music_analytics.json",
            "application/json"
        )

# Main tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔍 Discover", 
    "📋 My Playlist", 
    "📊 Analytics", 
    "🎯 Top Picks",
    "ℹ️ About"
])

with tab1:
    # Search section with enhanced UI
    col1, col2 = st.columns([4, 1])
    
    with col1:
        music_list = music['song'].values
        selected_song = st.selectbox(
            "🎵 Search for a song",
            music_list,
            help="Type to search or select from dropdown"
        )
    
    with col2:
        st.write("")
        st.write("")
        search_button = st.button("🚀 Discover", use_container_width=True)
    
    # Feature badges
    st.markdown("""
    <div style="text-align: center; margin: 1rem 0;">
        <span class="feature-badge-glow">🎯 AI Powered</span>
        <span class="feature-badge-glow">🎵 Audio Analysis</span>
        <span class="feature-badge-glow">📊 Real-time Stats</span>
        <span class="feature-badge-glow">🎧 Preview Tracks</span>
    </div>
    """, unsafe_allow_html=True)
    
    if search_button:
        st.session_state.history.insert(0, selected_song)
        if len(st.session_state.history) > 20:
            st.session_state.history.pop()
        
        # Loading animation
        with st.spinner(""):
            st.markdown("""
            <div style="text-align: center; padding: 2rem;">
                <div class="loading-dots">
                    <span></span><span></span><span></span>
                </div>
                <p style="color: rgba(255,255,255,0.7); margin-top: 1rem;">Finding perfect matches...</p>
            </div>
            """, unsafe_allow_html=True)
            time.sleep(1)
            recommendations = recommend(selected_song, num_recommendations)
        
        if recommendations:
            st.markdown("---")
            st.markdown("## 🎧 Your Personalized Recommendations")
            
            # Display original song first
            st.markdown("### 🎵 Selected Song")
            selected_details = get_song_details(selected_song, music[music['song'] == selected_song]['artist'].values[0])
            
            if selected_details:
                orig_col1, orig_col2 = st.columns([1, 3])
                with orig_col1:
                    if selected_details['album_cover']:
                        st.markdown(f'<img src="{selected_details["album_cover"]}" class="album-glow" style="width: 100%; border-radius: 15px;">', unsafe_allow_html=True)
                
                with orig_col2:
                    st.markdown(f"<div class='song-title-neon'>{selected_song}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='artist-name'>👤 {music[music['song'] == selected_song]['artist'].values[0]}</div>", unsafe_allow_html=True)
                    
                    if show_audio_features and selected_details.get('audio_features'):
                        st.plotly_chart(create_audio_features_chart(selected_details['audio_features']), use_container_width=True)
            
            st.markdown("---")
            st.markdown("### 🎯 Similar Tracks You'll Love")
            
            # Display recommendations
            for idx, song in enumerate(recommendations):
                with st.container():
                    st.markdown(f'<div class="neon-card">', unsafe_allow_html=True)
                    
                    col1, col2 = st.columns([1, 3])
                    
                    with col1:
                        if song['details'] and song['details']['album_cover']:
                            st.markdown(f'<img src="{song["details"]["album_cover"]}" class="album-glow" style="width: 100%; border-radius: 15px;">', unsafe_allow_html=True)
                        else:
                            st.image("https://i.postimg.cc/0QNxYz4V/social.png", use_container_width=True)
                    
                    with col2:
                        st.markdown(f"<div class='song-title-neon'>#{idx+1} {song['name']}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='artist-name'>👤 {song['artist']}</div>", unsafe_allow_html=True)
                        
                        # Similarity score with progress bar
                        st.markdown(f"""
                        <div style="margin: 1rem 0;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                                <span style="color: rgba(255,255,255,0.7);">Match Score</span>
                                <span style="color: #1DB954; font-weight: 700;">{song['similarity_score']:.1f}%</span>
                            </div>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: {song['similarity_score']:.1f}%"></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if song['details']:
                            # Song details
                            detail_col1, detail_col2, detail_col3, detail_col4 = st.columns(4)
                            with detail_col1:
                                st.metric("⭐ Popularity", f"{song['details']['popularity']}/100")
                            with detail_col2:
                                minutes = song['details']['duration'] // 60
                                seconds = song['details']['duration'] % 60
                                st.metric("⏱️ Duration", f"{minutes}:{seconds:02d}")
                            with detail_col3:
                                st.metric("📅 Released", song['details']['release_date'][:4] if song['details']['release_date'] != 'N/A' else 'N/A')
                            with detail_col4:
                                st.metric("💿 Album", song['details'].get('album_name', 'N/A')[:15] + '...' if song['details'].get('album_name') and len(song['details'].get('album_name', '')) > 15 else song['details'].get('album_name', 'N/A'))
                            
                            # Audio features radar chart
                            if show_audio_features and song['details'].get('audio_features'):
                                audio_col1, audio_col2 = st.columns([2, 1])
                                with audio_col1:
                                    st.plotly_chart(create_audio_features_chart(song['details']['audio_features']), use_container_width=True)
                                with audio_col2:
                                    features = song['details']['audio_features']
                                    st.markdown(f"""
                                    <div class="info-box-glow">
                                        <h4 style="color: #1DB954; margin-bottom: 1rem;">Audio Metrics</h4>
                                        <p style="color: rgba(255,255,255,0.9);">⚡ Energy: {features['energy']:.0f}%</p>
                                        <p style="color: rgba(255,255,255,0.9);">💃 Danceability: {features['danceability']:.0f}%</p>
                                        <p style="color: rgba(255,255,255,0.9);">😊 Mood: {features['valence']:.0f}%</p>
                                        <p style="color: rgba(255,255,255,0.9);">🎸 Acoustic: {features['acousticness']:.0f}%</p>
                                        <p style="color: rgba(255,255,255,0.9);">🥁 Tempo: {features['tempo']:.0f} BPM</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                        
                        # Action buttons
                        st.markdown("<br>", unsafe_allow_html=True)
                        btn_col1, btn_col2, btn_col3, btn_col4 = st.columns(4)
                        
                        with btn_col1:
                            if st.button(f"➕ Playlist", key=f"add_{idx}"):
                                song_data = {
                                    'name': song['name'], 
                                    'artist': song['artist'], 
                                    'added_at': datetime.now().strftime("%Y-%m-%d %H:%M"),
                                    'similarity': song['similarity_score']
                                }
                                if song_data not in st.session_state.playlist:
                                    st.session_state.playlist.insert(0, song_data)
                                    st.success("✅ Added!")
                                    if auto_play:
                                        st.balloons()
                                else:
                                    st.info("Already in playlist")
                        
                        with btn_col2:
                            if song['details'] and song['details']['spotify_url']:
                                st.link_button("🎵 Spotify", song['details']['spotify_url'])
                        
                        with btn_col3:
                            if st.button(f"❤️ Like", key=f"like_{idx}"):
                                if song['name'] not in st.session_state.liked_songs:
                                    st.session_state.liked_songs.append(song['name'])
                                    st.success("❤️ Liked!")
                                else:
                                    st.info("Already liked")
                        
                        with btn_col4:
                            if st.button(f"🔄 Similar", key=f"similar_{idx}"):
                                st.session_state['next_search'] = song['name']
                                st.rerun()
                        
                        # Preview player
                        if show_preview and song['details'] and song['details']['preview_url']:
                            st.markdown("<br>", unsafe_allow_html=True)
                            st.audio(song['details']['preview_url'])
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)

with tab2:
    st.markdown("## 📋 Your Personal Playlist")
    
    if st.session_state.playlist:
        # Playlist stats
        total_duration = sum([
            get_song_details(song['name'], song['artist'])['duration'] 
            for song in st.session_state.playlist 
            if get_song_details(song['name'], song['artist'])
        ] or [0])
        
        stat_col1, stat_col2, stat_col3 = st.columns(3)
        with stat_col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="stat-value">{len(st.session_state.playlist)}</div>
                <div class="stat-label">Total Songs</div>
            </div>
            """, unsafe_allow_html=True)
        
        with stat_col2:
            hours = total_duration // 3600
            minutes = (total_duration % 3600) // 60
            st.markdown(f"""
            <div class="metric-card">
                <div class="stat-value">{hours}h {minutes}m</div>
                <div class="stat-label">Total Duration</div>
            </div>
            """, unsafe_allow_html=True)
        
        with stat_col3:
            avg_similarity = sum([song.get('similarity', 0) for song in st.session_state.playlist]) / len(st.session_state.playlist)
            st.markdown(f"""
            <div class="metric-card">
                <div class="stat-value">{avg_similarity:.1f}%</div>
                <div class="stat-label">Avg Match Score</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Export options
        export_col1, export_col2 = st.columns(2)
        with export_col1:
            if st.button("📥 Export as JSON", use_container_width=True):
                playlist_json = json.dumps(st.session_state.playlist, indent=2)
                st.download_button(
                    "Download Playlist",
                    playlist_json,
                    "musicverse_playlist.json",
                    "application/json",
                    use_container_width=True
                )
        
        with export_col2:
            if st.button("🗑️ Clear Playlist", use_container_width=True):
                st.session_state.playlist = []
                st.rerun()
        
        st.markdown("---")
        
        # Display playlist items
        for idx, song in enumerate(st.session_state.playlist):
            st.markdown(f'<div class="neon-card">', unsafe_allow_html=True)
            
            pcol1, pcol2, pcol3 = st.columns([3, 2, 1])
            
            with pcol1:
                st.markdown(f"<div class='song-title-neon'>#{idx+1} {song['name']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='artist-name'>👤 {song['artist']}</div>", unsafe_allow_html=True)
            
            with pcol2:
                st.markdown(f"""
                <div style="padding-top: 0.5rem;">
                    <p style="color: rgba(255,255,255,0.7);">Added: {song['added_at']}</p>
                    {f'<p style="color: #1DB954;">Match: {song.get("similarity", 0):.1f}%</p>' if 'similarity' in song else ''}
                </div>
                """, unsafe_allow_html=True)
            
            with pcol3:
                if st.button("🗑️", key=f"remove_{idx}"):
                    st.session_state.playlist.pop(idx)
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
            
    else:
        st.markdown("""
        <div class="info-box-glow" style="text-align: center; padding: 3rem;">
            <h2 style="color: #1DB954;">🎵 Your Playlist is Empty</h2>
            <p style="color: rgba(255,255,255,0.7); font-size: 1.2rem;">
                Start discovering music and add your favorites!
            </p>
        </div>
        """, unsafe_allow_html=True)

with tab3:
    st.markdown("## 📊 Your Music Analytics")
    
    if len(st.session_state.history) > 0:
        # Overview metrics
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        
        with metric_col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="stat-value">{len(st.session_state.history)}</div>
                <div class="stat-label">Songs Searched</div>
            </div>
            """, unsafe_allow_html=True)
        
        with metric_col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="stat-value">{st.session_state.recommendations_count}</div>
                <div class="stat-label">Discovery Sessions</div>
            </div>
            """, unsafe_allow_html=True)
        
        with metric_col3:
            unique_artists = len(set([music[music['song'] == song]['artist'].values[0] for song in st.session_state.history if len(music[music['song'] == song]) > 0]))
            st.markdown(f"""
            <div class="metric-card">
                <div class="stat-value">{unique_artists}</div>
                <div class="stat-label">Artists Explored</div>
            </div>
            """, unsafe_allow_html=True)
        
        with metric_col4:
            engagement = (len(st.session_state.liked_songs) / max(len(st.session_state.history), 1)) * 100
            st.markdown(f"""
            <div class="metric-card">
                <div class="stat-value">{engagement:.0f}%</div>
                <div class="stat-label">Engagement Rate</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Charts
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            artist_chart = create_stats_chart()
            if artist_chart:
                st.plotly_chart(artist_chart, use_container_width=True)
        
        with chart_col2:
            pattern_chart = create_listening_pattern()
            if pattern_chart:
                st.plotly_chart(pattern_chart, use_container_width=True)
        
        # Detailed insights
        st.markdown("---")
        st.markdown("### 🎯 Personalized Insights")
        
        insight_col1, insight_col2 = st.columns(2)
        
        with insight_col1:
            st.markdown("""
            <div class="info-box-glow">
                <h4 style="color: #1DB954;">🔥 Your Music Taste</h4>
                <p style="color: rgba(255,255,255,0.9);">You've explored diverse genres and artists, showing an eclectic taste in music.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with insight_col2:
            st.markdown(f"""
            <div class="info-box-glow">
                <h4 style="color: #1DB954;">🎵 Discovery Power</h4>
                <p style="color: rgba(255,255,255,0.9);">You've discovered {len(set(st.session_state.history))} unique tracks. Keep exploring!</p>
            </div>
            """, unsafe_allow_html=True)
        
    else:
        st.markdown("""
        <div class="info-box-glow" style="text-align: center; padding: 3rem;">
            <h2 style="color: #1DB954;">📊 No Data Yet</h2>
            <p style="color: rgba(255,255,255,0.7); font-size: 1.2rem;">
                Start discovering music to see your analytics!
            </p>
        </div>
        """, unsafe_allow_html=True)

with tab4:
    st.markdown("## 🎯 Top Picks For You")
    
    if st.session_state.liked_songs:
        st.markdown("### ❤️ Based on Your Likes")
        
        # Get recommendations from liked songs
        random_liked = random.choice(st.session_state.liked_songs)
        top_picks = recommend(random_liked, 6)
        
        picks_col1, picks_col2, picks_col3 = st.columns(3)
        
        for idx, song in enumerate(top_picks[:6]):
            with [picks_col1, picks_col2, picks_col3][idx % 3]:
                st.markdown(f'<div class="neon-card">', unsafe_allow_html=True)
                
                if song['details'] and song['details']['album_cover']:
                    st.markdown(f'<img src="{song["details"]["album_cover"]}" class="album-glow" style="width: 100%; border-radius: 15px;">', unsafe_allow_html=True)
                
                st.markdown(f"<div class='song-title-neon' style='font-size: 1.2rem;'>{song['name'][:30]}...</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='artist-name'>{song['artist'][:25]}...</div>", unsafe_allow_html=True)
                
                if st.button(f"➕ Add", key=f"toppick_{idx}", use_container_width=True):
                    song_data = {
                        'name': song['name'], 
                        'artist': song['artist'], 
                        'added_at': datetime.now().strftime("%Y-%m-%d %H:%M")
                    }
                    if song_data not in st.session_state.playlist:
                        st.session_state.playlist.insert(0, song_data)
                        st.success("✅ Added!")
                
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="info-box-glow" style="text-align: center; padding: 3rem;">
            <h2 style="color: #1DB954;">🎯 Like Some Songs First!</h2>
            <p style="color: rgba(255,255,255,0.7); font-size: 1.2rem;">
                We'll create personalized picks based on your likes.
            </p>
        </div>
        """, unsafe_allow_html=True)

with tab5:
    st.markdown("## 🎵 About MusicVerse")
    
    st.markdown("""
    <div class="info-box-glow">
        <h3 style="color: #1DB954;">🚀 Premium Features</h3>
        <ul style="color: rgba(255,255,255,0.9); font-size: 1.1rem; line-height: 2;">
            <li>🎯 <strong>AI-Powered Recommendations</strong> - Advanced similarity algorithms</li>
            <li>🎵 <strong>Spotify Integration</strong> - Real-time data & 30s previews</li>
            <li>📊 <strong>Audio Analysis</strong> - Energy, danceability, mood metrics</li>
            <li>📋 <strong>Smart Playlists</strong> - Create & export custom playlists</li>
            <li>🕐 <strong>History Tracking</strong> - Never lose track of discoveries</li>
            <li>❤️ <strong>Like System</strong> - Save and revisit favorites</li>
            <li>📈 <strong>Analytics Dashboard</strong> - Visualize your music taste</li>
            <li>🎨 <strong>Beautiful UI</strong> - Glassmorphism & neon effects</li>
            <li>⚡ <strong>Real-time Stats</strong> - Track your discovery journey</li>
            <li>🎯 <strong>Personalized Picks</strong> - Based on your preferences</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="info-box-glow">
            <h3 style="color: #1DB954;">🎓 How It Works</h3>
            <ol style="color: rgba(255,255,255,0.9); font-size: 1rem; line-height: 1.8;">
                <li>Select a song you love</li>
                <li>Our AI analyzes audio features</li>
                <li>Get 6-15 similar recommendations</li>
                <li>Explore audio metrics & previews</li>
                <li>Build your perfect playlist</li>
                <li>Track your music journey</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-box-glow">
            <h3 style="color: #1DB954;">💻 Tech Stack</h3>
            <ul style="color: rgba(255,255,255,0.9); font-size: 1rem; line-height: 1.8;">
                <li><strong>Streamlit</strong> - Web framework</li>
                <li><strong>Spotipy</strong> - Spotify API</li>
                <li><strong>Plotly</strong> - Interactive charts</li>
                <li><strong>Machine Learning</strong> - Similarity engine</li>
                <li><strong>Python</strong> - Core language</li>
                <li><strong>CSS3</strong> - Modern styling</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: rgba(29, 185, 84, 0.1); border: 2px solid #1DB954; border-radius: 15px; padding: 2rem; text-align: center;">
        <h2 style="color: #1DB954; margin-bottom: 1rem;">🎵 Discover. Enjoy. Repeat.</h2>
        <p style="color: rgba(255,255,255,0.8); font-size: 1.1rem;">
            Made with ❤️ using AI, Music, and lots of ☕
        </p>
        <br>
        <div class="music-wave"></div>
        <div class="music-wave"></div>
        <div class="music-wave"></div>
        <div class="music-wave"></div>
        <div class="music-wave"></div>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 2rem;'>
    <p style='color: rgba(255,255,255,0.5); font-size: 1rem;'>🎵 MusicVerse v3.0 | Powered by Spotify API & AI</p>
    <p style='color: rgba(255,255,255,0.3); font-size: 0.9rem;'>Your Personal Music Discovery Platform</p>
</div>
""", unsafe_allow_html=True)