from backend.core import run_llm
import streamlit as st
from typing import Set
from PIL import Image, ImageDraw, ImageFont


def create_profile_image(
    name: str,
    size: tuple = (200, 200),
    bg_color: str = "#EE4C2C",
    text_color: str = "white",
):
    """Create a profile image with initials."""
    # Create a new image with a background color
    img = Image.new("RGB", size, bg_color)
    draw = ImageDraw.Draw(img)

    # Get initials from name (up to 2 characters)
    initials = "".join(word[0].upper() for word in name.split()[:2])

    # Calculate font size (approximately 40% of image width)
    font_size = int(size[0] * 0.4)

    try:
        # Try to use Arial font, fall back to default if not available
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        # Use default font
        font = ImageFont.load_default()

    # Calculate text size and position
    text_bbox = draw.textbbox((0, 0), initials, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    # Center the text
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2

    # Draw the text
    draw.text((x, y), initials, fill=text_color, font=font)

    return img


# Add sidebar with user information
with st.sidebar:
    st.title("User Profile")

    # Get user info if available
    user_info = st.user.to_dict()

    # If no real user info, show example data
    if not user_info:
        user_info = {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "role": "Developer",
            "status": "Active",
            "joined": "2024-01-01",
        }

    # Create and display profile picture
    profile_img = create_profile_image(user_info.get("name", "User"))
    st.image(profile_img, width=150, caption=user_info.get("name", "User Profile"))

    # Display user information in a more formatted way
    st.write("### User Information")
    st.write(f"👤 **Name:** {user_info.get('name', 'N/A')}")
    st.write(f"📧 **Email:** {user_info.get('email', 'N/A')}")
    st.write(f"🎯 **Role:** {user_info.get('role', 'N/A')}")
    st.write(f"🟢 **Status:** {user_info.get('status', 'N/A')}")
    st.write(f"📅 **Joined:** {user_info.get('joined', 'N/A')}")

    st.divider()


st.header("LangChain - Documentation Assistant")

# Create a form for the prompt input and submit button
with st.form(key="prompt_form"):
    prompt = st.text_input("Prompt", placeholder="Enter your prompt here...")
    submit_button = st.form_submit_button("Submit")

if (
    "chat_answer_history" not in st.session_state
    and "user_prompt_history" not in st.session_state
    and "chat_history" not in st.session_state
):
    st.session_state["user_prompt_history"] = []
    st.session_state["chat_answer_history"] = []
    st.session_state["chat_history"] = []


def create_sources_string(source_urls: Set[str]) -> str:
    if not source_urls:
        return ""
    sources_list = list(source_urls)
    sources_list.sort()
    sources_string = "sources:\n"
    for i, source in enumerate(sources_list):
        sources_string += f"{i+1}. {source}\n"
    return sources_string


if submit_button and prompt:
    with st.spinner("Generating response..."):
        generated_response = run_llm(
            query=prompt,
            chat_history=st.session_state["chat_history"],
        )

        # extract URLs
        sources = set(
            [doc.metadata["source"] for doc in generated_response["source_documents"]]
        )

        formatted_response = (
            f"{generated_response['result']} \n\n {create_sources_string(sources)}"
        )

        st.session_state["user_prompt_history"].append(prompt)
        st.session_state["chat_answer_history"].append(formatted_response)
        st.session_state["chat_history"].append(("human", prompt))
        st.session_state["chat_history"].append(("ai", generated_response["result"]))

if st.session_state["chat_answer_history"]:
    for generated_response, user_query in zip(
        st.session_state["chat_answer_history"], st.session_state["user_prompt_history"]
    ):
        st.chat_message("user").write(user_query)
        st.chat_message("assistant").write(generated_response)
