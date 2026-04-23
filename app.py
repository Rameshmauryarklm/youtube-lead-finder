from googleapiclient.discovery import build
import streamlit as st
import pandas as pd

# 🔑 ADD YOUR API KEY HERE
API_KEY = "AIzaSyAx9vzKdFnurIVV8_5Z2c_vZcF1iUyzIqM"

youtube = build('youtube', 'v3', developerKey=API_KEY)

# 🔥 Buy intent keywords
BUY_KEYWORDS = [
    # English
    "price", "cost", "buy", "purchase", "order", "shop",
    "where to buy", "how to buy", "link", "product link",
    "send link", "give link", "available", "availability",
    "is it available", "in stock", "out of stock",
    "discount", "offer", "coupon", "deal",
    "best price", "lowest price",
    "i want this", "i need this", "interested",
    "take my money", "add to cart",
    
    # Hindi (Roman)
    "price kya hai", "kitne ka hai", "kitna price hai",
    "kaise kharide", "kaha se kharide", "link bhejo",
    "link do", "available hai kya", "stock me hai kya",
    "order kaise kare", "buy kaise kare", "discount hai kya",
    "offer hai kya", "mujhe chahiye", "mujhe lena hai",
    "interested hu", "ye chahiye",
    
    # Hindi (Devanagari)
    "कीमत क्या है", "कितने का है", "कैसे खरीदें",
    "कहां से खरीदें", "लिंक भेजो", "लिंक दो",
    "उपलब्ध है क्या", "स्टॉक में है क्या",
    "ऑर्डर कैसे करें", "मुझे चाहिए", "मुझे लेना है"
]

# 🎯 Extract video ID
def get_video_id(url):
    if "v=" in url:
        return url.split("v=")[-1].split("&")[0]
    return url

# 📥 Get comments
def get_comments(video_id):
    comments = []

    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=100
    )

    while request:
        response = request.execute()

        for item in response['items']:
            comment_data = item['snippet']['topLevelComment']['snippet']

            comments.append({
                "author": comment_data['authorDisplayName'],
                "comment": comment_data['textDisplay'],
                "likes": comment_data['likeCount'],
                "date": comment_data['publishedAt']
            })

        request = youtube.commentThreads().list_next(request, response)

    return comments

# 🔍 Filter leads
def filter_leads(comments):
    leads = []
    for c in comments:
        text = c["comment"].lower()
        if any(word in text for word in BUY_KEYWORDS):
            leads.append(c)
    return leads

# ---------------- UI ----------------

st.title("🔥 YouTube Comment Lead Finder")

url = st.text_input("Enter YouTube URL")

if st.button("Extract Leads"):

    video_id = get_video_id(url)

    with st.spinner("Fetching comments..."):
        comments = get_comments(video_id)
        leads = filter_leads(comments)

    st.success("Done!")

    # 📊 Stats
    st.write(f"Total Comments: {len(comments)}")
    st.write(f"Leads Found: {len(leads)}")

    if len(comments) > 0:
        conversion_rate = (len(leads) / len(comments)) * 100
        st.write(f"Lead %: {round(conversion_rate, 2)}%")

    # 👀 Preview Leads
    st.subheader("Leads Preview")
    for lead in leads[:10]:
        st.write(lead["comment"])

    # 📥 Download Leads CSV
    leads_df = pd.DataFrame(leads)
    leads_csv = leads_df.to_csv(index=False).encode('utf-8')

    st.download_button(
        "Download Leads CSV",
        leads_csv,
        file_name="leads.csv",
        mime='text/csv'
    )

    # 📥 Download ALL Comments CSV
    all_df = pd.DataFrame(comments)
    all_csv = all_df.to_csv(index=False).encode('utf-8')

    st.download_button(
        "Download All Comments CSV",
        all_csv,
        file_name="all_comments.csv",
        mime='text/csv'
    )

    # 📋 Show some comments
    st.subheader("All Comments Preview")
    for c in comments[:10]:
        st.write(c["comment"])