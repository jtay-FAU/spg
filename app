import requests
from bs4 import BeautifulSoup
import openai
import streamlit as st
from PIL import Image

# Use Streamlit Secrets to store the OpenAI API key
openai.api_key = st.secrets["openai_api_key"]

def fetch_text_from_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    h1_title = soup.find('h1').get_text().strip() if soup.find('h1') else ""
    bespoke_page = soup.find(id='bespokePage', class_='bespokePage')

    if bespoke_page:
        for table in bespoke_page.find_all(class_='table'):
            table.extract()
        for info_box in bespoke_page.find_all(class_='infoBox'):
            info_box.extract()

        text = bespoke_page.get_text().strip()
    else:
        text = "No text found in the specified div."

    return h1_title, text

def generate_social_media_posts(text):
    social_media_platforms = {
        "Twitter": "twitter_logo.png",
        "LinkedIn": "linkedin_logo.png",
        "Facebook": "facebook_logo.png",
        "TikTok": "tiktok_logo.png",
        "Instagram": "instagram_logo.png"
    }
    posts = {}

    for platform, logo_file in social_media_platforms.items():
        prompt = f"Create a social media post to promote the following article on {platform}. The post should be engaging and tailored to the {platform} audience. Text: \n\n{text}\n\n{platform} Post:"
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=1000,
            n=1,
            stop=None,
            temperature=0.7,
            top_p=1
        )
        post = response.choices[0].text.strip()
        posts[platform] = (post, logo_file)

    return posts

def authenticate(password):
    if password == PASSWORD:
        return True
    return False

def main():
    st.title("Social Media Post Generator")

    # Streamlit password protection
    if "authenticated" not in st.session_state:
        password_input = st.text_input("Password", type="password")
        if st.button("Submit"):
            if authenticate(password_input):
                st.session_state.authenticated = True
            else:
                st.error("Incorrect password. Please try again.")
        return

    url = st.text_input("Enter the URL:")
    if st.button("Generate Posts"):
        h1_title, text = fetch_text_from_url(url)

        st.subheader("H1 Title:")
        st.text(h1_title)

        st.subheader("URL:")
        st.text(url)

        st.subheader("Extracted Text:")
        st.text(text)

        st.subheader("Generated Social Media Posts:")
        posts = generate_social_media_posts(text)
        for platform, (post, logo_file) in posts.items():
            st.subheader(platform)
            st.image(Image.open(logo_file), use_column_width=True)
            st.text(post)

if __name__ == "__main__":
    main()
