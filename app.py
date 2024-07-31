import streamlit as st
from ai71 import AI71
import os
from dotenv import load_dotenv
import logging
import uuid

# Force Streamlit to rerun the script
st.cache_data.clear()
st.cache_resource.clear()

# Set up logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()

# Initialize AI71 client
AI71_API_KEY = os.getenv("AI71_API_KEY")
client = AI71(AI71_API_KEY)

# UI configurations
st.set_page_config(page_title="Marmar", page_icon="💊")
custom_css = """
<style>
    h1 {
        font-size: 24px;
        color: #033F3C;
        padding: 0px 0px 40px 0px;
    }
    .stButton > button {
        background-color: #033F3C;
        color: #ffffff;
    }
    .stButton > button:hover {
        background-color: white;
        color: #033F3C;
    }
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

# Display an Image Banner
st.image('img/banner.png', use_column_width=True)

# Streamlit app interface 
st.title('Empowering you with the knowledge to safely manage your medications.')
st.write('Welcome to Marmar. Check potential drug interactions and get tailored advice. Please provide the details below to get started.')

# Input fields
medications = st.text_area('Enter the names of the medications you are currently taking, separated by commas:', help='Please enter the names of the medications you are currently taking, separated by commas.')
health_history = st.text_area('Enter your health history or describe any ailments:', help='Please include any chronic conditions, recent illnesses, or relevant health issues.')

options = ['Male', 'Female']
gender = st.selectbox('Choose your gender:', options)
age = st.text_input('Enter your age (Optional):', '')
weight = st.text_input('Enter your weight in kg (Optional):', '')
height = st.text_input('Enter your height in cm (Optional):', '')

def display_copyable_text(text):
    st.text_area("Marmar's Analysis:", value=text, height=300)
    st.button("Copy to clipboard", on_click=lambda: st.write("Text copied to clipboard!"))

# function to check drug interactions
def check_drug_interactions(medications, health_history, gender="", age="", weight="", height="", max_tokens=1000):
    try:
        prompt = f"""Given the health history: {health_history}, provide a detailed explanation of the potential risks and interactions among these medications: {medications}.
        Focus on any increased risks, specific side effects, and the mechanism by which these interactions might occur, also considering the health history.
        Include any relevant studies or findings that have implicated these drugs in such conditions.
        Ensure the explanation is comprehensive, covering the pharmacological aspects and clinical implications for patients.
        Then, based on gender: {gender}, age: {age}, weight: {weight}, height: {height}, and health history: {health_history}, offer tailored advice.
        Classify the overall interaction risk as either SEVERE, MODERATE, or MILD.
        If the interaction risk is SEVERE, suggest alternative medications that could be considered.
        Format your response as follows:
        Risk Level: [SEVERE/MODERATE/MILD]
        Explanation: [Your detailed explanation]
        Tailored Advice: [Your advice]
        Alternative Medications (if SEVERE): [Your suggestions]
        """
        
        response = client.chat.completions.create(
            model="tiiuae/falcon-180B-chat",
            messages=[
                {"role": "system", "content": "You are a knowledgeable pharmacist assistant."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=1000,  # Increased max tokens for more detailed response
        )
        
        if response.choices and response.choices[0].message:
            return response.choices[0].message.content, str(response)
        else:
            return "Marmar did not provide a response. Please try again.", "No content in response"
    except Exception as e:
        return f"An error occurred: {str(e)}", str(e)

# Button to initiate the drug interaction check
if st.button('Check Interactions'):
    warning_users = "<p style='color: #BABABA; opacity:.7;'>We appreciate you choosing MarMar for your medication management needs. Please note, MarMar is designed to support, not substitute, the guidance of healthcare professionals. For advice specific to your health concerns, make sure to consult with your doctor or healthcare provider.</p>" 
    st.markdown(warning_users, unsafe_allow_html=True)
    
    if medications and health_history:
        with st.spinner('Analyzing interactions...'):
            response, raw_response = check_drug_interactions(medications, health_history, gender, age, weight, height, max_tokens=1000)
        
        if response.startswith("An error occurred"):
            st.error(response)
        elif response == "Marmar did not provide a response. Please try again.":
            st.warning(response)
        else:
            st.subheader("Marmar's Analysis:")
            display_copyable_text(response)  # Display full response with copy button
    else:
        st.warning('Please enter the required information to continue.')

# Footer
footer="""<style>
a:link , a:visited{
color: #BADEDC;
background-color: transparent;
text-decoration: underline;
}

a:hover,  a:active {
color: #033F3C;
background-color: transparent;
text-decoration: underline;
}

.footer {
position: fixed;
left: 0;
bottom: 0;
width: 100%;
background-color: transparent;
color: #64928F;
text-align: center;
}
</style>
<div class="footer">
<p>  <a>Thank you for using MARMAR for safer medication management!</a> <a style='display: block; text-align: center;' href="https://ahruf.notion.site/About-Marmar-6e1c9dc286e84884bd7a62e6ec76cca4?pvs=4" target="_blank">About marmar</a></p>
</div>
"""
st.markdown(footer,unsafe_allow_html=True)