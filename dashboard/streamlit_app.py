import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.storage.mongodb_client import MongoDBClient
from src.utils.config import Config

st.set_page_config(
    page_title="Advanced News Sentiment Dashboard",
    page_icon="📊",
    layout="wide"
)

@st.cache_resource
def get_database():
    return MongoDBClient()

db = get_database()

def create_wordcloud(text_list):
    """Create word cloud from list of texts"""
    if not text_list:
        return None
    
    text = ' '.join(text_list)
    
    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color='white',
        colormap='viridis'
    ).generate(text)
    
    return wordcloud

def main():
    st.title("📊 Advanced News Sentiment Dashboard")
    
    # Sidebar
    st.sidebar.header("Settings")
    
    selected_topics = st.sidebar.multiselect(
        "Select Topics",
        Config.TOPICS,
        default=Config.TOPICS[:2]
    )
    
    if not selected_topics:
        st.warning("Please select at least one topic")
        return
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Overview",
        "☁️ Word Clouds",
        "🔥 Top Keywords",
        "📈 Deep Dive"
    ])
    
    # Tab 1: Overview
    with tab1:
        st.header("Sentiment Overview")
        
        for topic in selected_topics:
            st.subheader(f"📌 {topic}")
            
            stats = db.get_sentiment_stats(topic=topic)
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total", stats['total'])
            col2.metric("😊 Positive", stats['positive'])
            col3.metric("😞 Negative", stats['negative'])
            col4.metric("😐 Neutral", stats['neutral'])
            
            # Mini pie chart
            if stats['total'] > 0:
                fig = go.Figure(data=[go.Pie(
                    labels=['Positive', 'Negative', 'Neutral'],
                    values=[stats['positive'], stats['negative'], stats['neutral']],
                    hole=0.3,
                    marker_colors=['#00cc00', '#ff0000', '#808080']
                )])
                fig.update_layout(height=300, showlegend=True)
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
    
    # Tab 2: Word Clouds
    with tab2:
        st.header("☁️ Word Clouds by Sentiment")
        
        selected_topic = st.selectbox("Choose Topic", selected_topics)
        
        articles = list(db.articles_collection.find({'search_topic': selected_topic}).limit(500))
        
        if articles:
            col1, col2, col3 = st.columns(3)
            
            # Positive word cloud
            with col1:
                st.subheader("😊 Positive")
                positive_texts = [
                    a.get('processed_text', '') 
                    for a in articles 
                    if a.get('sentiment_label') == 'positive'
                ]
                
                if positive_texts:
                    wc = create_wordcloud(positive_texts)
                    if wc:
                        fig, ax = plt.subplots(figsize=(10, 5))
                        ax.imshow(wc, interpolation='bilinear')
                        ax.axis('off')
                        st.pyplot(fig)
                else:
                    st.info("No positive articles")
            
            # Negative word cloud
            with col2:
                st.subheader("😞 Negative")
                negative_texts = [
                    a.get('processed_text', '') 
                    for a in articles 
                    if a.get('sentiment_label') == 'negative'
                ]
                
                if negative_texts:
                    wc = create_wordcloud(negative_texts)
                    if wc:
                        fig, ax = plt.subplots(figsize=(10, 5))
                        ax.imshow(wc, interpolation='bilinear')
                        ax.axis('off')
                        st.pyplot(fig)
                else:
                    st.info("No negative articles")
            
            # Neutral word cloud
            with col3:
                st.subheader("😐 Neutral")
                neutral_texts = [
                    a.get('processed_text', '') 
                    for a in articles 
                    if a.get('sentiment_label') == 'neutral'
                ]
                
                if neutral_texts:
                    wc = create_wordcloud(neutral_texts)
                    if wc:
                        fig, ax = plt.subplots(figsize=(10, 5))
                        ax.imshow(wc, interpolation='bilinear')
                        ax.axis('off')
                        st.pyplot(fig)
                else:
                    st.info("No neutral articles")
    
    # Tab 3: Top Keywords
    with tab3:
        st.header("🔥 Top Keywords")
        
        selected_topic = st.selectbox("Select Topic", selected_topics, key='keywords_topic')
        
        articles = list(db.articles_collection.find({'search_topic': selected_topic}).limit(1000))
        
        if articles:
            # Collect all keywords
            all_keywords = []
            for article in articles:
                keywords = article.get('keywords', [])
                all_keywords.extend(keywords)
            
            # Count frequency
            keyword_counts = Counter(all_keywords)
            top_keywords = keyword_counts.most_common(20)
            
            if top_keywords:
                df_keywords = pd.DataFrame(top_keywords, columns=['Keyword', 'Count'])
                
                fig = px.bar(
                    df_keywords,
                    x='Count',
                    y='Keyword',
                    orientation='h',
                    title=f'Top 20 Keywords for {selected_topic}',
                    color='Count',
                    color_continuous_scale='Blues'
                )
                fig.update_layout(height=600)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No keywords found")
    
    # Tab 4: Deep Dive
    with tab4:
        st.header("📈 Deep Dive Analysis")
        
        selected_topic = st.selectbox("Pick Topic", selected_topics, key='deepdive_topic')
        
        articles = list(
            db.articles_collection.find({'search_topic': selected_topic})
            .sort('publishedAt', -1)
            .limit(500)
        )
        
        if articles:
            df = pd.DataFrame(articles)
            df['publishedAt'] = pd.to_datetime(df['publishedAt'])
            
            # Sentiment distribution histogram
            st.subheader("Sentiment Score Distribution")
            
            fig = px.histogram(
                df,
                x='vader_compound',
                color='sentiment_label',
                nbins=50,
                title='Distribution of Sentiment Scores',
                color_discrete_map={
                    'positive': '#00cc00',
                    'negative': '#ff0000',
                    'neutral': '#808080'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Most extreme sentiments
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📈 Most Positive Articles")
                most_positive = df.nlargest(5, 'vader_compound')
                for _, row in most_positive.iterrows():
                    st.markdown(f"**{row.get('title', 'No title')}**")
                    st.markdown(f"Score: {row['vader_compound']:.3f}")
                    st.markdown(f"[Read]({row.get('url', '#')})")
                    st.markdown("---")
            
            with col2:
                st.subheader("📉 Most Negative Articles")
                most_negative = df.nsmallest(5, 'vader_compound')
                for _, row in most_negative.iterrows():
                    st.markdown(f"**{row.get('title', 'No title')}**")
                    st.markdown(f"Score: {row['vader_compound']:.3f}")
                    st.markdown(f"[Read]({row.get('url', '#')})")
                    st.markdown("---")

if __name__ == "__main__":
    main()