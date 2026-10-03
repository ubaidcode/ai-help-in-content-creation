import json
from google import genai
from google.genai import types
import streamlit as st

# ============================================================
# INSTALLATIONstreamlit 
# ============================================================
# Run this once in CMD / Terminal:
#
# pip install -r requirements.txt
#
# Then run:
#
# streamlit run app.py
#
# ============================================================
# DEVELOPER SETTINGS
# ============================================================
# YAHAN SIRF AAP apni Gemini API key aur model name likhein.
# END USER ko API key ya model name nahi dikhaya jayega.


GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
MODEL_NAME = "gemini-3.5-flash"

# ============================================================
# STREAMLIT PAGE
# ============================================================

st.set_page_config(
    page_title="AI Video Content Generator",
    page_icon="🎬",
    layout="centered"
)

# ============================================================
# GEMINI CLIENT
# ============================================================

if not GEMINI_API_KEY or GEMINI_API_KEY == "PASTE_YOUR_GEMINI_API_KEY_HERE":
    st.error("Developer setup required: app.py mein GEMINI_API_KEY add karein.")
    st.stop()

if not MODEL_NAME.strip():
    st.error("Developer setup required: app.py mein MODEL_NAME add karein.")
    st.stop()

try:
    client = genai.Client(api_key=GEMINI_API_KEY)
except Exception as e:
    st.error(f"Gemini client start nahi ho saka: {e}")
    st.stop()

# ============================================================
# HEADER
# ============================================================

st.title("🎬 AI Video Content Generator")

st.write(
    "Apne video ko describe karein aur Gemini aapke liye "
    "Caption, Description, Keywords aur Hashtags generate karega."
)

st.info(
    "Describe Your Video "
    "API key aur model developer settings mein already configured hain."
)

# ============================================================
# USER INPUT
# ============================================================

video_description = st.text_area(
    "🎥 Describe Your Video",
    placeholder=(
        "Example:\n"
        "Ek funny classroom video hai jisme ek bachcha teacher "
        "ke question ka funny jawab deta hai. Classroom mein "
        "students hans rahe hain aur video ka mood comedy hai."
    ),
    height=220
)

# ============================================================
# GEMINI PROMPT
# ============================================================

def create_prompt(description):
    return f"""
You are a professional social media content writer and SEO assistant.

The user has described a video below.

Your job is to create exactly FOUR outputs:

1. Caption
2. Description
3. Keywords
4. Hashtags

IMPORTANT RULES:
- Understand the user's video description carefully.
- Do not invent events, people, places, products, or facts that were not described.
- Caption should be engaging and suitable for social media.
- Description should clearly explain the video.
- Keywords should be relevant search/SEO keywords.
- Hashtags should be relevant to the video's actual topic.
- Keep the language natural.
- Do not add an introduction or explanation.
- Return ONLY valid 3SON.
- Do not use Markdown code fences.
- return minmum 1000+ and maximum 4000 words in description.

Return exactly this JSON structure:

{{
    "caption": "Your caption here",
    "description": "Your description here",
    "keywords": [
        "keyword 1",
        "keyword 2",
        "keyword 3",
        "keyword 4",
        "keyword 5",
        "keyword 6",
        "keyword 7",
        "keyword 8"
    ],
    "hashtags": [
        "#hashtag1",
        "#hashtag2",
        "#hashtag3",
        "#hashtag4",
        "#hashtag5",
        "#hashtag6",
        "#hashtag7",
        "#hashtag8"
    ]
}}

VIDEO DESCRIPTION:
{description}
"""

# ============================================================
# GENERATE CONTENT
# ============================================================

if st.button("✨ Generate Content", type="primary", use_container_width=True):

    if not video_description.strip():
        st.warning("Pehle apne video ka description likhein.")
        st.stop()

    try:
        with st.spinner("🤖 Gemini content generate kar raha hai..."):

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=create_prompt(video_description.strip()),
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.7
                )
            )

        if not response.text:
            st.error("Gemini ne koi response nahi diya.")
            st.stop()

        try:
            result = json.loads(response.text)
        except json.JSONDecodeError:
            st.error("Gemini ka response valid JSON mein nahi tha.")
            st.code(response.text)
            st.stop()

        # ====================================================
        # RESULTS
        # ====================================================

        st.success("✅ Content generated successfully!")

        st.subheader("💬 Caption")
        st.text_area(
            "Caption",
            value=str(result.get("caption", "")),
            height=100,
            key="caption_result"
        )

        st.subheader("📝 Description")
        st.text_area(
            "Description",
            value=str(result.get("description", "")),
            height=180,
            key="description_result"
        )

        keywords = result.get("keywords", [])

        if isinstance(keywords, list):
            keywords_text = ", ".join(str(x) for x in keywords)
        else:
            keywords_text = str(keywords)

        st.subheader("🔎 Keywords")
        st.text_area(
            "Keywords",
            value=keywords_text,
            height=100,
            key="keywords_result"
        )

        hashtags = result.get("hashtags", [])

        if isinstance(hashtags, list):
            hashtags_text = " ".join(str(x) for x in hashtags)
        else:
            hashtags_text = str(hashtags)

        st.subheader("#️⃣ Hashtags")
        st.text_area(
            "Hashtags",
            value=hashtags_text,
            height=100,
            key="hashtags_result"
        )

        # Optional complete JSON download
        st.download_button(
            "⬇️ Download Result",
            data=json.dumps(result, ensure_ascii=False, indent=2),
            file_name="video_content.json",
            mime="application/json",
            use_container_width=True
        )

    except Exception as e:
        st.error(f"❌ Gemini Error: {e}")

# ============================================================
# FOOTER
# ============================================================

st.divider()
st.caption("Powered by Google Gemini")
