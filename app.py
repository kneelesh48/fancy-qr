import io
import os
import time

import qrcode
import replicate
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="QR Code Generator", page_icon=None, layout="wide")

with open("static/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.header("Fancy QR Code Generator")

col1, col2 = st.columns(2)

with col1:
    data = st.text_input(
        "Enter the text you want to encode into QR Code",
        value="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    )

    if data:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG")
        st.image(buffer, caption="QR Code", width=300)

# @st.cache_data
def generate_fancy_qr(data, image_prompt, batch_size=1):
    model = replicate.models.get("nateraw/qrcode-stable-diffusion")
    version = model.versions.get("9cdabf8f8a991351960c7ce2105de2909514b40bd27ac202dba57935b07d29d4")
    prediction = replicate.predictions.create(
        version=version,
        input={
            "prompt": image_prompt,
            "qr_code_content": data,
            "batch_size": batch_size,
            }
    )

    with expander:
        time_counter = 0
        container = st.empty()
        while prediction.status == "starting":
            container.code("Model is starting up...", language=None)
            if time_counter > 60:
                container.code("Model is starting up...\nThis can sometimes take around 5 to 10 minutes while the model boots up.", language=None)

            time_counter += 1
            prediction.reload()
            time.sleep(1)
        
        while prediction.status == "processing":
            container.code(prediction.logs, language=None)

            time_counter += 1
            prediction.reload()
            time.sleep(1)

    return prediction.output


with col2:
    prompts = [
        "interior of luxury condominium with minimalist furniture and lush house plants and abstract wall paintings",
        "The french countryside, green pastures, lush environment, vivid colors, animation by studio ghibli"
        "traditional village, thatched roofs, mountains",
        "a cubism painting of a town with a lot of houses in the snow with a sky background, Andreas Rocha, matte painting concept art, a detailed matte painting",
        "Japanese painting, mountains, 1girl",
        "A photo-realistic rendering of a busy market, ((street vendors, fruits, vegetable, shops)), (Photorealistic:1.3), (Highly detailed:1.2), (Natural light:1.2), art inspired by Architectural Digest, Vogue Living, and Elle Decor",
    ]

    image_prompt = st.text_area(
        "Enter the prompt for the image you want to generate",
        value=prompts[2]
    )

    with st.expander("Prompt Examples"):
        for prompt in prompts:
            st.markdown(f"- {prompt}")

    # batch_size = st.number_input(
    #     "Enter the batch size",
    #     value=1,
    #     min_value=1,
    #     max_value=4,
    #     step=1
    # )

    # replicate_api_key = st.text_input(
    #     "Replicate API Key (optional)",
    #     value="",
    #     type="password"
    # )

    # if replicate_api_key:
    #     os.environ["REPLICATE_API_TOKEN"] = replicate_api_key

    gen_button = st.button("Generate Fancy QR Code")

    image_container = st.container()

    if gen_button and image_prompt:
        st.session_state['is_expanded'] = True
        expander = st.expander("Show Logs", expanded=st.session_state['is_expanded'])

        output = generate_fancy_qr(data, image_prompt)

        st.session_state['is_expanded'] = False # not working

        for url in output:
            image_container.image(url, caption="Fancy QR Code", width=300)
