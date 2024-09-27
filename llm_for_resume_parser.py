import streamlit as st
import openai
import pandas as pd
from PyPDF2 import PdfReader
import docx

# Function to extract text from a PDF
def extract_text_from_pdf(pdf_file):
    try:
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""  # Safely handle None values
        return text.strip()
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return ""

# Function to extract text from a DOCX file
def extract_text_from_docx(docx_file):
    try:
        doc = docx.Document(docx_file)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text.strip()
    except Exception as e:
        st.error(f"Error reading DOCX: {e}")
        return ""

# Function to get completion from OpenAI
def get_completion(prompt, api_key):
    try:
        openai.api_key = api_key
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant that extracts information from resumes."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        st.error(f"Error communicating with OpenAI API: {e}")
        return ""

# Function to extract resume information
def extract_resume_info(resume_text, api_key):
    prompt = f"""
    Please extract the following information from the resume:

    1. Name
    2. Education (Institution, Degree, Major, Duration)
    3. Work Experience (Company, Role, Duration)
    4. Skills (Languages, Frameworks, Tools)

    Format the output like this:

    Name: <Name>
    Education:
        - Institution: <Institution>
          Degree: <Degree>
          Major: <Major>
          Duration: <Duration>
    Work Experience:
        - Company: <Company>
          Role: <Role>
          Duration: <Duration>
    Skills:
        - <Skill1>
        - <Skill2>
        - <Skill3>

    Resume Text:
    {resume_text}
    """
    return get_completion(prompt, api_key)

# Function to parse extracted information into structured format
def parse_extracted_info(extracted_info):
    lines = extracted_info.splitlines()
    data = {
        'Name': 'Not available',
        'Education': 'Not available',
        'Work Experience': 'Not available',
        'Skills': 'Not available'
    }

    current_section = None
    education_list = []
    work_experience_list = []
    skills_list = []

    for line in lines:
        line = line.strip()
        if line.startswith("Name:"):
            data['Name'] = line.split(":", 1)[1].strip()
        elif line.startswith("Education:"):
            current_section = "Education"
        elif line.startswith("Work Experience:"):
            current_section = "Work Experience"
        elif line.startswith("Skills:"):
            current_section = "Skills"
        elif current_section == "Education" and line.startswith("-"):
            education_list.append(line[1:].strip())
        elif current_section == "Work Experience" and line.startswith("-"):
            work_experience_list.append(line[1:].strip())
        elif current_section == "Skills" and line.startswith("-"):
            skills_list.append(line[1:].strip())

    if education_list:
        data['Education'] = "\n".join(education_list)
    if work_experience_list:
        data['Work Experience'] = "\n".join(work_experience_list)
    if skills_list:
        data['Skills'] = "\n".join(skills_list)

    return pd.DataFrame([data])

# Streamlit app
st.title("Resume Information Extractor")

# Collect OpenAI API key
openai_api_key = st.text_input("Enter your OpenAI API key:", type="password")

# Upload multiple resume files
uploaded_files = st.file_uploader("Upload multiple resume files", type=["pdf", "docx"], accept_multiple_files=True)

# Initialize an empty DataFrame to store all resume information
all_resumes_data = pd.DataFrame()

# Process resume files
if uploaded_files and openai_api_key:
    for uploaded_file in uploaded_files:
        if uploaded_file.type == "application/pdf":
            resume_text = extract_text_from_pdf(uploaded_file)
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            resume_text = extract_text_from_docx(uploaded_file)
        else:
            st.error(f"Unsupported file type for {uploaded_file.name}. Please upload a PDF or DOCX file.")
            continue

        # Extract information from each resume
        if resume_text:
            extracted_info = extract_resume_info(resume_text, openai_api_key)

            if extracted_info:
                st.write(f"Extracted Information for {uploaded_file.name}:")
                st.write(extracted_info)

                # Parse the extracted information into a DataFrame
                df = parse_extracted_info(extracted_info)

                # Add the parsed data to the main DataFrame
                all_resumes_data = pd.concat([all_resumes_data, df], ignore_index=True)
            else:
                st.warning(f"No information could be extracted from {uploaded_file.name}.")
else:
    if not uploaded_files:
        st.write("Please upload one or more resume files.")
    if not openai_api_key:
        st.write("Please enter your OpenAI API key.")

# Display the combined data
if not all_resumes_data.empty:
    st.write("Summary Table:")
    st.write(all_resumes_data)

    # Export all resume data to Excel
    output_file = "multiple_resumes_summary_data.xlsx"
    all_resumes_data.to_excel(output_file, index=False)

    st.write(f"Resume summary data saved to Excel file: {output_file}")

    # Provide download link for the Excel file
    with open(output_file, "rb") as f:
        st.download_button(
            label="Download Excel File",
            data=f,
            file_name="multiple_resumes_summary_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.warning("No structured data was extracted from the resumes.")
