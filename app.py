import streamlit as st

from google import genai
from google.genai import types

from prompts import (
    SYSTEM_PROMPT,
    WELCOME_MESSAGE_TEMPLATE,
)

MODEL_NAME = "gemini-3.5-flash"

st.set_page_config(
    page_title="StudyMate",
    page_icon="⚙️",
    layout="centered"
)

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]


@st.cache_resource
def get_gemini_client():
    return genai.Client(
        api_key=GEMINI_API_KEY
    )


gemini_client = get_gemini_client()


def render_message(message):

    with st.chat_message(message["role"]):

        if message["kind"] == "text":
            st.write(message["content"])

        elif message["kind"] == "image":
            st.image(message["content"])


def add_message(role, kind, content):

    message = {
        "role": role,
        "kind": kind,
        "content": content
    }

    st.session_state.messages.append(message)

    render_message(message)


def ask_gemini(parts):

    try:

        response = st.session_state.chat.send_message(parts)

        return response.text

    except Exception as error:

        return (
            "Sorry, something went wrong.\n\n"
            f"Error: {error}"
        )


# -------------------------------
# USER ONBOARDING
# -------------------------------

if "onboarded" not in st.session_state:

    st.title("⚙️ StudyMate")

    st.caption(
        "Your AI-powered Mechanical Engineering Study Assistant"
    )

    with st.form("onboarding_form"):

        name = st.text_input(
            "Your name",
            placeholder="Enter your name"
        )

        submitted = st.form_submit_button(
            "Start Learning 🚀"
        )

    if submitted:

        if not name.strip():

            st.warning("Please enter your name.")

        else:

            st.session_state.name = name.strip()

            st.session_state.chat = (
                gemini_client.chats.create(
                    model=MODEL_NAME,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT
                    )
                )
            )

            st.session_state.messages = []

            st.session_state.onboarded = True

            st.rerun()

    st.stop()


# -------------------------------
# MAIN PAGE
# -------------------------------

st.title("⚙️ StudyMate")

st.caption(
    f"Student: {st.session_state.name} | "
    "Mechanical Engineering Study Assistant"
)


# -------------------------------
# WELCOME MESSAGE
# -------------------------------

if not st.session_state.messages:

    add_message(
        "assistant",
        "text",
        WELCOME_MESSAGE_TEMPLATE.format(
            name=st.session_state.name
        )
    )


# -------------------------------
# DISPLAY CHAT HISTORY
# -------------------------------

else:

    for message in st.session_state.messages:

        render_message(message)


# -------------------------------
# CHAT INPUT + IMAGE UPLOAD
# -------------------------------

user_input = st.chat_input(
    "Ask a question or upload an image...",
    accept_file=True,
    file_type=[
        "jpg",
        "jpeg",
        "png"
    ]
)


if user_input:

    photo = (
        user_input.files[0]
        if user_input.files
        else None
    )

    text = user_input.text

    parts = []


    # -------------------------------
    # IMAGE
    # -------------------------------

    if photo is not None:

        photo_bytes = photo.getvalue()

        add_message(
            "user",
            "image",
            photo_bytes
        )

        parts.append(
            types.Part.from_bytes(
                data=photo_bytes,
                mime_type=photo.type
            )
        )


    # -------------------------------
    # TEXT
    # -------------------------------

    if text:

        add_message(
            "user",
            "text",
            text
        )

        parts.append(text)


    # -------------------------------
    # IMAGE WITHOUT TEXT
    # -------------------------------

    elif photo is not None:

        parts.append(
            """
            Analyze this image as a Mechanical Engineering
            study assistant.

            If it contains a mechanical component:

            1. Identify the component.
            2. Explain its main function.
            3. Explain its working principle.
            4. Mention common materials.
            5. Mention applications.
            6. Mention important engineering parameters.
            7. Mention common defects or failure modes
               when relevant.

            If it contains an engineering question:

            1. Read the question.
            2. Identify the given information.
            3. Identify what is required.
            4. Select the appropriate formula.
            5. Solve the problem step by step.
            6. Give the final answer with units.

            If the image is unclear,
            clearly mention what information is unclear.
            """
        )


    # -------------------------------
    # SEND TO GEMINI
    # -------------------------------

    with st.chat_message("assistant"):

        with st.spinner(
            "StudyMate is analyzing..."
        ):

            answer = ask_gemini(parts)

        st.write(answer)


    add_message(
        "assistant",
        "text",
        answer
    )