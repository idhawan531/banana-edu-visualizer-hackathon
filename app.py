# -*- coding: utf-8 -*-
import streamlit as st
import google.genai.types as types
from google import genai
from io import BytesIO
from PIL import Image

# Initialize global variables properly
if 'client' not in st.session_state:
    st.session_state.client = None

model_name = "gemini-2.5-flash-image-preview"

# Configure page
st.set_page_config(
    page_title="EduVisualizer",
    page_icon="📚",
    layout="wide"
)

# Title and description
st.title("📚 AI-Powered Educational Concept Visualizer")
st.markdown("""
Create consistent educational illustrations with the SAME character across different concepts.
This demo showcases Gemini 2.5 Flash Image's capabilities for educational content creation.
""")

# Initialize session state
if 'base_character' not in st.session_state:
    st.session_state.base_character = None
if 'api_calls' not in st.session_state:
    st.session_state.api_calls = 0
if 'concept_images' not in st.session_state:
    st.session_state.concept_images = {}
if 'character_description' not in st.session_state:
    st.session_state.character_description = ""

# API key setup
api_key = st.text_input("Enter your Gemini API Key", type="password", help="Get a free API key at https://aistudio.google.com/app/apikey")
if api_key:
    try:
        st.session_state.client = genai.Client(api_key=api_key)
        st.success("API Key configured! Ready to create educational visuals.")
    except Exception as e:
        st.error(f"API configuration error: {str(e)}")
else:
    st.warning("Please enter your Gemini API Key to proceed")

# --- Function Definitions (Must come BEFORE usage) ---

def generate_image(prompt, reference_image=None):
    """
    Generates an image using the Gemini API.
    Handles both text-only prompts and prompts with a reference image.
    """
    try:
        # Ensure client is configured
        if not st.session_state.client:
            raise ValueError("API client not configured. Please enter your API key.")

        # Start building the parts of the content
        parts = []

        # Add the text prompt first
        parts.append(types.Part.from_text(text=prompt))

        # Add reference image if provided
        if reference_image is not None:
            try:
                # Prepare the image data
                if isinstance(reference_image, bytes):
                    image_bytes = reference_image
                elif hasattr(reference_image, 'getvalue'):
                    image_bytes = reference_image.getvalue()
                else:
                    raise ValueError("Reference image must be bytes or BytesIO object.")

                # Create the image part
                image_part = types.Part(
                    inline_data=types.Blob(
                        mime_type="image/jpeg",
                        data=image_bytes
                    )
                )
                parts.append(image_part)

            except Exception as img_prep_error:
                st.warning(f"Could not prepare reference image for API call: {img_prep_error}. Proceeding with text prompt only.")

        # Create the content structure
        contents = [types.Content(role="user", parts=parts)]

        # Configure the generation request
        generate_content_config = types.GenerateContentConfig(
            response_modalities=["IMAGE"]
        )

        # Make the API call
        response = st.session_state.client.models.generate_content(
            model=model_name,
            contents=contents,
            config=generate_content_config
        )

        # Check if response is valid
        if not response or not response.candidates:
            raise ValueError("Empty response received from API.")

        candidate = response.candidates[0]
        if not candidate.content or not candidate.content.parts:
            raise ValueError("No content parts found in API response candidate.")

        # Extract image data from the response
        for part in candidate.content.parts:
            if hasattr(part, 'inline_data') and part.inline_data and hasattr(part.inline_data, 'data'):
                return part.inline_data.data

        raise ValueError("No image data found in the API response parts.")

    except Exception as e:
        # Re-raise the exception with context for the calling function
        raise Exception(f"Image generation failed: {str(e)}")


# Character setup
with st.expander("Character Setup", expanded=True):
    col1, col2 = st.columns(2)

    with col1:
        character_desc = st.text_input(
            "Describe your educational character",
            "A curious 10-year-old student with glasses, wearing blue t-shirt, brown hair",
            help="This character will appear consistently across all educational concepts",
            key="char_desc_input"
        )

        # For base character generation
        if st.button("Generate Base Character", type="primary", key="gen_base_btn"):
            if not st.session_state.client:
                st.error("Please configure your API key first")

            elif not character_desc.strip():
                st.error("Please provide a character description.")

            else:
                with st.spinner("Creating base character profile..."):
                    try:
                        prompt = (
                            f"Create a detailed full-body image of: {character_desc}. "
                            f"This character will appear in multiple educational contexts. "
                            f"Focus on distinctive features that will remain consistent across different scenes. "
                            f"Style: Bright, clear educational illustration, suitable for children."
                        )
                        # Call the generate_image function (now defined above)
                        img_data = generate_image(prompt)

                        # Store results in session state
                        st.session_state.base_character = img_data
                        st.session_state.character_description = character_desc
                        st.session_state.api_calls += 1

                        st.success("Base character created!")
                        st.image(img_data, caption="Base Character Profile")

                    except Exception as e:
                        st.error(f"Error generating base character: {str(e)}")
                        if "429" in str(e) or "quota" in str(e).lower():
                             st.info("You might have hit API rate limits. Please check your plan or try again later.")
                        elif "400" in str(e) and "model" in str(e).lower():
                             st.info("Verify you're using a model that supports image generation.")
                        else:
                             st.info("Try these fixes:")
                             st.markdown("- Verify your API key is correct")
                             st.markdown("- Ensure character description is detailed enough")

    with col2:
        # Image upload option
        uploaded_image = st.file_uploader("Upload your own character image", type=["jpg", "jpeg", "png"])

        if uploaded_image is not None:
            try:
                # Validate image size and format
                image = Image.open(uploaded_image)

                # Check image dimensions
                max_size = (1024, 1024)
                if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                    image.thumbnail(max_size)
                    st.warning("Image was resized to meet potential size requirements")

                # Convert to RGB if necessary
                if image.mode != 'RGB':
                    image = image.convert('RGB')

                # Convert to bytes
                buffered = BytesIO()
                image.save(buffered, format="JPEG")
                img_bytes = buffered.getvalue()

                # Store the uploaded image
                st.session_state.base_character = img_bytes
                st.session_state.character_description = "Uploaded character image"
                # st.session_state.api_calls += 1 # Only increment for actual API calls

                st.success("Character image uploaded successfully!")

                # Display the uploaded image
                st.image(image, caption="Uploaded Character")

            except Exception as e:
                st.error(f"Error processing image: {str(e)}")
                st.info("Please upload a valid JPG, JPEG, or PNG file")

# Concept generation
if st.session_state.base_character:
    st.subheader("Generate Educational Concepts")

    # Concept selection
    concept_options = [
        "Photosynthesis process",
        "Ancient Roman marketplace",
        "Water cycle diagram",
        "Newton's laws of motion",
        "Human digestive system"
    ]

    selected_concept = st.selectbox(
        "Select or enter an educational concept",
        concept_options,
        index=0
    )

    custom_concept = st.text_input("Or enter your own concept")
    concept = custom_concept if custom_concept else selected_concept

    # For concept generation
    if st.button("Generate Concept Scene", type="primary", key="gen_scene_btn"):
        if not st.session_state.client:
            st.error("Please configure your API key first")

        elif not st.session_state.base_character:
            st.error("Please generate or upload a base character first")

        elif not concept.strip():
             st.error("Please select or enter an educational concept.")

        else:
            with st.spinner(f"Creating {concept} scene with consistent character..."):
                try:
                    prompt = f"""Create an educational illustration showing {concept}.
                    IMPORTANT CHARACTER GUIDELINES:
                    1. Use the provided character image as exact reference.
                    2. Maintain ALL physical features of the character (appearance, clothing, style).
                    3. The character should be prominently featured in the scene.
                    4. Keep the character's proportions and style consistent.

                    SCENE REQUIREMENTS:
                    - Style: Clear educational diagram with bright colors.
                    - Make the concept easy to understand for students.
                    - Include labeled elements and simple explanations.
                    - Ensure the character is actively involved in demonstrating the concept."""

                    # Call the generate_image function with the base character as reference
                    concept_img_data = generate_image(prompt, st.session_state.base_character)

                    # Store result
                    st.session_state.concept_images[concept] = concept_img_data
                    st.session_state.api_calls += 1 # Increment API call counter

                    # Display results side-by-side
                    col1, col2 = st.columns(2)
                    with col1:
                        st.image(st.session_state.base_character, caption="Base Character")
                    with col2:
                        st.image(concept_img_data, caption=f"{concept} Scene")

                except Exception as e:
                    st.error(f"Error generating scene: {str(e)}")
                    if "429" in str(e) or "quota" in str(e).lower():
                         st.info("You might have hit API rate limits (RPD/RPM/TPM). Check your plan or try again later.")
                    elif "400" in str(e) and "model" in str(e).lower():
                         st.info("Verify you're using a model that supports image generation.")
                    else:
                         st.info("Try these fixes:")
                         st.markdown("- Verify your API key is correct")
                         st.markdown("- Reduce complexity of prompts")
                         st.markdown("- Wait a few minutes and try again")

# Add generated concepts gallery
if st.session_state.concept_images:
    st.subheader("Your Generated Concepts Gallery")
    st.markdown("See how your character appears across different concepts:")
    
    # Create a list of all concept names, including the edited ones
    # We'll sort them so that original concepts come first, followed by their edited versions
    concept_list = []
    for concept in st.session_state.concept_images.keys():
        if concept.startswith("Edited_"):
            # If it's an edited concept, add it after its original counterpart
            original_concept = concept[7:]  # Remove "Edited_" prefix
            if original_concept not in concept_list:
                concept_list.append(original_concept)
            concept_list.append(concept)
        else:
            # If it's an original concept, just add it
            if concept not in concept_list:
                concept_list.append(concept)
    
    # Create rows of 2 columns for gallery
    for i in range(0, len(concept_list), 2):
        cols = st.columns(2)
        # First concept in row
        with cols[0]:
            concept = concept_list[i]
            st.image(st.session_state.concept_images[concept], caption=concept)

        # Second concept in row (if exists)
        if i + 1 < len(concept_list):
            with cols[1]:
                concept = concept_list[i + 1]
                st.image(st.session_state.concept_images[concept], caption=concept)
                
# Image Editing Section
if st.session_state.concept_images and st.session_state.base_character:
    st.subheader("Edit Your Generated Concept Scene")
    
    # Select which concept scene to edit
    concepts_to_edit = list(st.session_state.concept_images.keys())
    selected_concept_for_edit = st.selectbox(
        "Select a concept scene to edit",
        concepts_to_edit,
        index=0
    )
    
    # Get the image data for the selected concept
    current_image_data = st.session_state.concept_images[selected_concept_for_edit]
    
    # Display the original image
    col1, col2 = st.columns(2)
    with col1:
        st.image(current_image_data, caption=f"Original {selected_concept_for_edit} Scene")
    
    # Prompt for editing
    with col2:
        edit_prompt = st.text_area(
            "Describe the edits you want to make to this image:",
            "For example: 'Add a label pointing to the sun', 'Make the plant larger', 'Change the background to a classroom'",
            height=100
        )
        
        if st.button("Apply Edits", type="primary"):
            if not edit_prompt.strip():
                st.error("Please enter an edit description.")
            else:
                with st.spinner(f"Applying edits to {selected_concept_for_edit} scene..."):
                    try:
                        # Create a prompt that includes the original image as reference
                        # and describes the desired changes
                        full_prompt = f"""You are an expert educational illustrator.
                        You have been given the following image of {selected_concept_for_edit}.
                        Apply these edits to the image:
                        {edit_prompt}
                        
                        IMPORTANT INSTRUCTIONS:
                        1.  Keep the main character from the original image (use it as a reference).
                        2.  Maintain all physical features of the character (appearance, clothing, style).
                        3.  Make the requested changes clearly visible and relevant to the educational concept.
                        4.  Ensure the final image remains a clear educational diagram."""
                        
                        # Call the generate_image function with the original image as reference
                        edited_img_data = generate_image(full_prompt, current_image_data)
                        
                        # Store the edited image
                        st.session_state.concept_images[f"Edited_{selected_concept_for_edit}"] = edited_img_data
                        
                        # Display the result
                        st.success("Edits applied successfully!")
                        st.image(edited_img_data, caption=f"Edited {selected_concept_for_edit} Scene")
                        
                    except Exception as e:
                        st.error(f"Error applying edits: {str(e)}")

# Add pre-generated examples as fallback (for submission)
with st.expander("Pre-generated Examples (For Submission Verification)"):
    st.markdown("""
    **Important for judges**: These examples demonstrate our implementation concept when API calls are limited.
    They show the intended character consistency feature.
    """)

    example_col1, example_col2, example_col3  = st.columns(3)
    with example_col1:
        st.image("./GeneratedImages/BaseImage1.jpg", caption="Base Character 1")
    with example_col2:
        st.image("./GeneratedImages/GeneratedImage1-3.jpg", caption="Human Digestive System")
    with example_col3:
        st.image("./GeneratedImages/GeneratedImage1-4.jpg", caption="Newton's Laws of Motion")

    example_col4, example_col5, example_col6 = st.columns(3)
    with example_col4:
        st.image("./GeneratedImages/BaseImage2.jpg", caption="Base Character 2")
    with example_col5:
        st.image("./GeneratedImages/GeneratedImage2-1.jpg", caption="Water Cycle Scene")
    with example_col6:
        st.image("./GeneratedImages/GeneratedImage2-2.jpg", caption="Ancitent Roman Marketplace")


# Footer
st.markdown("---")
st.caption("Nano Banana Hackathon Submission • Character consistency across educational concepts")

# Display API call counter in sidebar
st.sidebar.metric("API Calls Used", st.session_state.api_calls)
st.sidebar.info("Free tier: 100 requests/day for gemini-2.5-flash-image-preview")