import streamlit as st
import openai
from newspaper import Article
import os  # For accessing environment variables

# Set your OpenAI API key using an environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

def fetch_article(url):
    """Fetch and parse the article using the Newspaper library."""
    article = Article(url)
    article.download()
    article.parse()
    return article.text

def generate_title_slug_tags_focus(content, keyphrase):
    """Generate a title, slug, and more SEO-related tags based on the content."""
    prompt = f"""
    Analyze the following content and generate:
    1. A concise and meaningful title (within 60 characters) with the keyphrase "{keyphrase}" at the beginning of the title. Ensure the title is exactly as the keyphrase or a close variation of it. Do not include any numbering at the start of the title.
    2. A relevant slug derived from the title, ensuring the keyphrase is part of the slug.
    3. A 2-3 word focus keyphrase that encapsulates the main topic of the content.
    4. At least 50 highly relevant, specific SEO-related tags that directly reflect the content's key themes.
       - Focus on niche and specific keywords.
       - Avoid generic tags like "news", "article", or "updates". 
       - Consider long-tail keywords and variations of key phrases that would improve search engine ranking.

    Content: {content}
    """
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=600,
        temperature=0.5
    )
    result = response.choices[0].message["content"].strip()
    
    # Extract title, slug, focus keyphrase, and tags
    lines = result.split("\n")
    title = lines[0].replace("Title:", "").strip()
    slug = lines[1].replace("Slug:", "").strip()
    focus_keyphrase = lines[2].replace("Focus Keyphrase:", "").strip()
    tags = lines[3].replace("Tags:", "").strip()

    # Clean up the tags to ensure they are a list of comma-separated keywords
    tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
    tags = ", ".join(tag_list)  # Join tags with commas
    
    return title, slug, focus_keyphrase, tags

def enhance_content(content, inbound_link, outbound_link, keyword, keyphrase):
    """Use OpenAI API to enhance content with SEO optimizations."""
    prompt = f"""
    Rewrite the following content for a news website called 'The Hans Bharat', ensuring:
    - The content is unique and untraceable to the original source.
    - A professional, engaging, and user-friendly tone.
    - Include an internal link: <a href="{inbound_link}">The Hans Bharat</a>, naturally within the content.
    - Embed the keyword '{keyword}' with an external link: <a href="{outbound_link}" target="_blank">{keyword}</a> in a natural context. Ensure this keyword is hyperlinked exactly where it appears in the text.
    - Ensure the content has at least 300 words.
    - Focus on using active voice, reducing passive voice, and shortening long sentences.
    - Include transition words where necessary to improve readability and SEO.
    - Add relevant images (optional) with alt text matching the keyphrase "{keyphrase}" if possible.
    - Ensure the HTML is clean and valid with proper semantic tags.

    Content: {content}
    """
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
        temperature=0.7
    )
    return response.choices[0].message["content"]

def generate_meta_description(content):
    """Generate a meta description from the content."""
    prompt = f"Create a concise, 156-character meta description for the following content, ensuring it's clear and concise:\n\n{content}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=50,
        temperature=0.5
    )
    return response.choices[0].message["content"]

# Streamlit UI
st.title("The Hans Bharat - SEO Content Enhancer")

# User Inputs
url = st.text_input("Enter the article URL:")
inbound_link = st.text_input("Enter an internal (inbound) link:")
outbound_link = st.text_input("Enter an external (outbound) link:")
keyword = st.text_input("Enter the keyword for the outbound link:")
keyphrase = st.text_input("Enter the keyphrase for SEO optimization:")

if st.button("Generate Article"):
    if url and inbound_link and outbound_link and keyword and keyphrase:
        with st.spinner("Fetching and processing content..."):
            try:
                # Fetch article content using Newspaper library
                content = fetch_article(url)
                # Generate title, slug, focus keyphrase, and tags
                title, slug, focus_keyphrase, tags = generate_title_slug_tags_focus(content, keyphrase)
                # Ensure title has no numbering
                title = title.lstrip('0123456789.- ')  # Remove any number and trailing spaces before the title
                # Enhance content
                enhanced_content = enhance_content(content, inbound_link, outbound_link, keyword, keyphrase)
                # Generate meta description
                meta_description = generate_meta_description(enhanced_content)
                
                # Prepare HTML Output with Meta Tags
                html_output = f"""
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>{title}</title>  <!-- Title without numbering -->
                    <meta name="keywords" content="{tags}">
                    <meta name="author" content="The Hans Bharat">
                    <meta name="description" content="{meta_description}">
                </head>
                <body>
                    <article>
                        <header>
                            <h1>{title}</h1>  <!-- Title in h1 -->
                        </header>
                        <section>
                            {enhanced_content}
                        </section>
                    </article>
                </body>
                </html>
                """
                
                # Display Results
                st.subheader("Generated Title")
                st.write(title)
                st.subheader("Slug")
                st.write(slug)
                st.subheader("Focus Keyphrase")
                st.write(focus_keyphrase)
                st.subheader("Tags")
                st.write(tags)
                st.subheader("HTML Content with Meta Tags")
                st.code(html_output, language="html")
                st.subheader("Meta Description (Plain Text)")
                st.write(meta_description)
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.error("Please provide all required inputs!")
