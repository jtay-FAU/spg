import streamlit as st
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from PIL import Image
import time
import os

os.environ['OPENAI_API_KEY'] = st.secrets["openai"]["api_key"]
client = OpenAI()

def check_password():
    """Returns `True` if the user entered the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["security"]["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True

@st.cache
def fetch_text_from_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    h1_title = soup.find('h1').get_text().strip() if soup.find('h1') else ""
    
    bespoke_page = (soup.find(id='bespokePage') 
                    or soup.find(attrs={'class': 'bespokePage'}) 
                    or soup.find(attrs={'class': 'htmlpage-content'})
                    or soup.find(attrs={'class': 'mainOffsetArticle'}))
    
    if bespoke_page:
        for table in bespoke_page.find_all(class_='table'):
            table.extract()
        for info_box in bespoke_page.find_all(class_='infoBox'):
            info_box.extract()
        for card_body in bespoke_page.find_all(class_='card-body'):
            card_body.extract()    
        for territory in bespoke_page.find_all(class_='territory'):
            territory.extract() 
        for territory in bespoke_page.find_all(class_='emg-similar-courses'):
            territory.extract()                
            
        text = bespoke_page.get_text().strip()
    else:
        text = "Oops. No text was found in the specified webpage."
    
    return h1_title, text

def generate_social_media_posts(text, platforms):
    social_media_platforms = {
        "Twitter": "twitter_logo.png",
        "LinkedIn": "linkedin_logo.png",
        "Facebook": "facebook_logo.png",
        "TikTok": "tiktok_logo.png",
        "Instagram": "instagram_logo.png"
    }
    posts = {}

    for platform in platforms:
        logo_file = social_media_platforms.get(platform, "custom_logo.png")

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            temperature=0.7,
            max_tokens=1000,
            messages=[                
                {"role": "system", "content": "You are a helpful social media post generator. Your role is to generate social network specific social posts for an article or blog post, using the provided text."},
                {"role": "user", "content": f"Create a social media post to promote the following article on {platform}. The post should be engaging and tailored to the {platform} audience demographic. Text: \n\n{text}\n\n{platform} Post:"}
            ]
        )  

        post = completion.choices[0].message.content
        posts[platform] = (post, logo_file)

        time.sleep(3)

    return posts

def main():
    if check_password():
        st.set_page_config(
            page_title="Social Media Post Generator",
            page_icon="🧭",
            layout="wide",
            initial_sidebar_state="expanded"
        )

        # Logo and title
        logo_url = "https://www.keg.com/hubfs/keg_left_Sharp.svg"
        st.image(logo_url, width=200)
        st.title("Social Media Post Generator")

        url = st.text_input("Enter the URL:")
        platforms = st.multiselect(
            "Select the social media platforms:",
            ["Twitter", "LinkedIn", "Facebook", "TikTok", "Instagram"]
        )

        select_all = st.checkbox("Select All")
        if select_all:
            platforms = ["Twitter", "LinkedIn", "Facebook", "TikTok", "Instagram"]

        new_platform = st.text_input("Enter a new platform (optional):")

        if new_platform:
            platforms.append(new_platform)

        if st.button("Generate Posts"):
            if not url or not platforms:
                 st.warning("Please enter a URL and select at least one platform before generating posts.")
            else:
                 h1_title, text = fetch_text_from_url(url)


            st.markdown("---")
            st.header("Generate Posts")
            st.write(f"H1 Title: {h1_title}")
            st.write(f"URL: {url}")

            st.subheader("Article Text:")
            st.markdown(f'<div style="width:100%; padding:10px; border-radius:5px; word-wrap: break-word;"><pre>{text}</pre></div>', unsafe_allow_html=True)

            st.subheader("Generated Social Media Posts:")
            posts = generate_social_media_posts(text, platforms)
            for platform, (post, logo_file) in posts.items():
                st.subheader(platform)               
                st.image(Image.open(logo_file).resize((32, 32)), width=32)
                st.markdown(f'<div style="margin-left:10px;"><div style="width:100%; padding:10px; background-color:#3399ff; border-radius:5px; word-wrap: break-word;"><pre>{post}</pre></div></div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
