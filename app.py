# -*- coding: utf-8 -*-
import streamlit as st
import google.genai.types as types
from google import genai
from io import BytesIO
from PIL import Image
import json

# Initialize global variables properly
if 'client' not in st.session_state:
    st.session_state.client = None

IMAGE_MODEL = "gemini-2.5-flash-image-preview"
REVIEW_MODEL = "gemini-2.0-flash"  # For image analysis

# Configure page
st.set_page_config(
    page_title="📚 EduVisualizer",
    page_icon="📚",
    layout="wide"
)

# Title and description
st.title("📚 AI-Powered Educational Concept Visualizer")
st.markdown("""
Create consistent educational illustrations with the SAME character across different concepts.
This demo uses AI to review and fix errors in generated images.
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

# --- FUNCTION DEFINITIONS ---

def generate_image(prompt, reference_image=None):
    """
    Generates an image using the Gemini API.
    Handles both text-only prompts and prompts with a reference image.
    """
    try:
        if not st.session_state.client:
            raise ValueError("API client not configured. Please enter your API key.")

        parts = []
        parts.append(types.Part.from_text(text=prompt))

        if reference_image is not None:
            try:
                if isinstance(reference_image, bytes):
                    image_bytes = reference_image
                elif hasattr(reference_image, 'getvalue'):
                    image_bytes = reference_image.getvalue()
                else:
                    raise ValueError("Reference image must be bytes or BytesIO object.")

                image_part = types.Part(
                    inline_data=types.Blob(
                        mime_type="image/jpeg",
                        data=image_bytes
                    )
                )
                parts.append(image_part)
            except Exception as img_prep_error:
                st.warning(f"Could not prepare reference image: {img_prep_error}. Proceeding with text prompt only.")

        contents = [types.Content(role="user", parts=parts)]
        generate_content_config = types.GenerateContentConfig(response_modalities=["IMAGE"])

        response = st.session_state.client.models.generate_content(
            model=IMAGE_MODEL,
            contents=contents,
            config=generate_content_config
        )

        if not response or not response.candidates:
            raise ValueError("Empty response from API.")
        candidate = response.candidates[0]
        if not candidate.content or not candidate.content.parts:
            raise ValueError("No content parts in API response.")

        for part in candidate.content.parts:
            if hasattr(part, 'inline_data') and part.inline_data and hasattr(part.inline_data, 'data'):
                return part.inline_data.data
        raise ValueError("No image data found in response.")
    except Exception as e:
        raise Exception(f"Image generation failed: {str(e)}")

def analyze_image_and_get_fixes(image_data, user_concept):
    """
    Uses an LLM to analyze the generated image and return a list of fixes needed.
    The LLM sees the image and the original concept to detect errors.
    """
    try:
        if not st.session_state.client:
            raise ValueError("API client not configured.")

        # Prepare image part for analysis
        image_part = types.Part(
            inline_data=types.Blob(
                mime_type="image/jpeg",
                data=image_data
            )
        )

        # Create analysis prompt
        analysis_prompt = f"""
        You are an expert educational content reviewer specializing in K-12 education.

        STEP 1 - CONCEPT UNDERSTANDING:
        First, understand the core elements of "{user_concept}" that students need to learn:
        - Key principles and components
        - Standard terminology
        - Common misconceptions to avoid

        STEP 2 - IMAGE ANALYSIS:
        Analyze the provided image for these specific aspects:

        1. Scientific Accuracy:
        - Correct representation of processes/concepts
        - Accurate proportions and relationships
        - Valid scientific principles
        - Incorrect spelling should be corrected (e.g., 'photosynthasis' to 'P H O T O S Y N T H E S I S')

        2. Educational Clarity:
        - Age-appropriate explanations
        - Clear visual hierarchy
        - Logical flow of information

        3. Technical Elements:
        - Spelling and grammar in labels/text
        - Proper placement of labels
        - Visibility and readability of text

        4. Character Integration:
        - Character's relevance to concept
        - Proper demonstration of principles
        - Educational engagement level

        RESPONSE FORMAT:
        Return a JSON list of specific, actionable fixes. Each fix should be clear and implementable.
        Examples: 
        ["Fix spelling: 'photosynthasis' to 'P H O T O S Y N T H E S I S'",
         "Add arrow showing energy flow from sun to plant",
         "Make mathematical equation '2+2=5' correct to '2+2=4'",
         "Reposition character to actively demonstrate the concept"]

        IMPORTANT: Return ONLY the JSON list. No other text or explanation.
        If the image is perfect, return an empty list: []
        """

        # Call LLM for analysis
        response = st.session_state.client.models.generate_content(
            model=REVIEW_MODEL,
            contents=[
                types.Content(role="user", parts=[image_part]),
                types.Content(role="user", parts=[types.Part.from_text(text=analysis_prompt)]),
            ],
        )

        if response.candidates and response.candidates[0].content.parts:
            raw_output = response.candidates[0].content.parts[0].text.strip()

            # Try to parse as JSON list
            try:
                # Clean the output to make it valid JSON
                cleaned_output = raw_output.strip()
                if cleaned_output.startswith("```json"):
                    cleaned_output = cleaned_output[7:]
                if cleaned_output.endswith("```"):
                    cleaned_output = cleaned_output[:-3]
                cleaned_output = cleaned_output.strip()

                fixes = json.loads(cleaned_output)
                if isinstance(fixes, list):
                    return fixes
                else:
                    st.warning("LLM returned invalid JSON format. Assuming no fixes needed.")
                    return []
            except json.JSONDecodeError:
                st.warning(f"Could not parse LLM output as JSON: {raw_output}. Assuming no fixes needed.")
                return []
        else:
            st.warning("No response from LLM reviewer.")
            return []

    except Exception as e:
        st.warning(f"Image analysis failed: {str(e)}")
        return []

# --- CHARACTER SETUP ---
with st.expander("Character Setup", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        character_desc = st.text_input(
            "Describe your educational character",
            "A curious 10-year-old student with glasses, wearing blue t-shirt, brown hair",
            help="This character will appear consistently across all educational concepts",
            key="char_desc_input"
        )
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
                            f"Focus on distinctive features that will remain consistent. "
                            f"Style: Bright, clear educational illustration, suitable for children."
                        )
                        img_data = generate_image(prompt)
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
        uploaded_image = st.file_uploader("Upload your own character image", type=["jpg", "jpeg", "png"])
        if uploaded_image is not None:
            try:
                image = Image.open(uploaded_image)
                max_size = (1024, 1024)
                if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                    image.thumbnail(max_size)
                    st.warning("Image was resized to meet potential size requirements")
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                buffered = BytesIO()
                image.save(buffered, format="JPEG")
                img_bytes = buffered.getvalue()
                st.session_state.base_character = img_bytes
                st.session_state.character_description = "Uploaded character image"
                st.success("Character image uploaded successfully!")
                st.image(image, caption="Uploaded Character")
            except Exception as e:
                st.error(f"Error processing image: {str(e)}")
                st.info("Please upload a valid JPG, JPEG, or PNG file")

# --- CONCEPT GENERATION ---
if st.session_state.base_character:
    st.subheader("Generate Educational Concepts")
    concept_options = [
        "Photosynthesis process",
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

    if st.button("Generate Concept Scene", type="primary", key="gen_scene_btn"):
        if not st.session_state.client:
            st.error("Please configure your API key first")
        elif not st.session_state.base_character:
            st.error("Please generate or upload a base character first")
        elif not concept.strip():
            st.error("Please select or enter an educational concept.")
        else:
            with st.spinner(f"🎨 Creating initial {concept} scene..."):
                try:
                    # --- STAGE 1: Generate Initial Image ---
                    initial_prompt = f"""Create an educational illustration showing {concept}.
                    IMPORTANT CHARACTER GUIDELINES:
                    1. Use the provided character image as exact reference.
                    2. Maintain ALL physical features of the character (appearance, clothing, style).
                    3. The character should be prominently featured in the scene.
                    4. Keep the character's proportions and style consistent.
                    SCENE REQUIREMENTS:
                    - Style: Clear educational diagram with bright colors
                    - Make the concept easy to understand for students
                    - Include labeled elements and simple explanations
                    - Ensure the character is actively involved in demonstrating the concept
                    QUALITY CHECK:
                    - Verify all elements accurately represent the concept
                    - Ensure educational accuracy in diagrams and labels"""

                    initial_img_data = generate_image(initial_prompt, st.session_state.base_character)
                    st.session_state.api_calls += 1

                    # --- STAGE 2: Analyze Image for Errors ---
                    with st.spinner("🔍 Reviewing image for errors..."):
                        fixes = analyze_image_and_get_fixes(initial_img_data, concept)

                        if fixes:
                            st.info(f"Found {len(fixes)} issue(s). Applying fixes...")
                            # --- STAGE 3: Re-Generate with Fixes ---
                            with st.spinner("🔄 Fixing errors and re-generating..."):
                                fix_instructions = "\n".join([f"- {fix}" for fix in fixes])
                                fix_prompt = f"""You are an expert educational illustrator.
                                You have been given an image of {concept} that needs corrections.
                                Apply these specific fixes:
                                {fix_instructions}
                                IMPORTANT:
                                1. Keep the main character from the original image (use it as a reference).
                                2. Maintain all physical features of the character.
                                3. Only change what is necessary to fix the listed issues.
                                4. Ensure the final image is a clear, accurate educational diagram."""

                                final_img_data = generate_image(fix_prompt, initial_img_data)
                                st.session_state.concept_images[concept] = final_img_data
                                st.session_state.api_calls += 1
                                st.success("✅ Image reviewed and corrected!")
                        else:
                            st.success("✅ Image is perfect! No corrections needed.")
                            st.session_state.concept_images[concept] = initial_img_data

                    # Display results
                    col1, col2 = st.columns(2)
                    with col1:
                        st.image(st.session_state.base_character, caption="Base Character")
                    with col2:
                        st.image(st.session_state.concept_images[concept], caption=f"{concept} Scene")

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

# --- GALLERY ---
if st.session_state.concept_images:
    st.subheader("Your Generated Concepts Gallery")
    st.markdown("See how your character appears across different concepts:")
    concept_list = []
    for concept in st.session_state.concept_images.keys():
        if concept.startswith("Edited_"):
            original_concept = concept[7:]
            if original_concept not in concept_list:
                concept_list.append(original_concept)
            concept_list.append(concept)
        else:
            if concept not in concept_list:
                concept_list.append(concept)
    for i in range(0, len(concept_list), 2):
        cols = st.columns(2)
        with cols[0]:
            concept = concept_list[i]
            st.image(st.session_state.concept_images[concept], caption=concept)
        if i + 1 < len(concept_list):
            with cols[1]:
                concept = concept_list[i + 1]
                st.image(st.session_state.concept_images[concept], caption=concept)

# --- IMAGE EDITING ---
if st.session_state.concept_images and st.session_state.base_character:
    st.subheader("Edit Your Generated Concept Scene")
    concepts_to_edit = list(st.session_state.concept_images.keys())
    selected_concept_for_edit = st.selectbox(
        "Select a concept scene to edit",
        concepts_to_edit,
        index=0
    )
    current_image_data = st.session_state.concept_images[selected_concept_for_edit]
    col1, col2 = st.columns(2)
    with col1:
        st.image(current_image_data, caption=f"Original {selected_concept_for_edit} Scene")
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
                        full_prompt = f"""You are an expert educational illustrator.
                        You have been given the following image of {selected_concept_for_edit}.
                        Apply these edits to the image:
                        {edit_prompt}
                        IMPORTANT INSTRUCTIONS:
                        1. Keep the main character from the original image (use it as a reference).
                        2. Maintain all physical features of the character (appearance, clothing, style).
                        3. Make the requested changes clearly visible and relevant to the educational concept.
                        4. Ensure the final image remains a clear educational diagram."""
                        edited_img_data = generate_image(full_prompt, current_image_data)
                        st.session_state.concept_images[f"Edited_{selected_concept_for_edit}"] = edited_img_data
                        st.success("Edits applied successfully!")
                        st.image(edited_img_data, caption=f"Edited {selected_concept_for_edit} Scene")
                    except Exception as e:
                        st.error(f"Error applying edits: {str(e)}")

# --- PRE-GENERATED EXAMPLES ---
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
        st.image("./GeneratedImages/GeneratedImage2-2.jpg", caption="Ancient Roman Marketplace")

# --- FOOTER ---
st.markdown("---")
st.caption("Nano Banana Hackathon Submission • Character consistency across educational concepts • AI-Powered Review & Fix")

# Display API call counter in sidebar
st.sidebar.metric("API Calls Used", st.session_state.api_calls)
st.sidebar.info("Free tier: 100 requests/day for gemini-2.5-flash-image-preview")