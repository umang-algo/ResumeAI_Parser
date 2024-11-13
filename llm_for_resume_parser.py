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

# Function to parse extracted information into structured format with durations and separate columns
def parse_extracted_info(extracted_info):
    lines = extracted_info.splitlines()
    data = {
        'Name': 'Not available',
        'Institution': [],
        'Degree': [],
        'Major': [],
        'Education Duration': [],
        'Company': [],
        'Role': [],
        'Work Duration': [],
        'Skills': []
    }

    current_section = None
    current_education = {}
    current_experience = {}

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
        elif current_section == "Education" and line.startswith("- Institution:"):
            if current_education:
                data['Institution'].append(current_education.get('Institution', ''))
                data['Degree'].append(current_education.get('Degree', ''))
                data['Major'].append(current_education.get('Major', ''))
                data['Education Duration'].append(current_education.get('Duration', ''))
            current_education = {"Institution": line.split(":", 1)[1].strip()}
        elif current_section == "Education" and line.startswith("Degree:"):
            current_education["Degree"] = line.split(":", 1)[1].strip()
        elif current_section == "Education" and line.startswith("Major:"):
            current_education["Major"] = line.split(":", 1)[1].strip()
        elif current_section == "Education" and line.startswith("Duration:"):
            current_education["Duration"] = line.split(":", 1)[1].strip()
        elif current_section == "Work Experience" and line.startswith("- Company:"):
            if current_experience:
                data['Company'].append(current_experience.get('Company', ''))
                data['Role'].append(current_experience.get('Role', ''))
                data['Work Duration'].append(current_experience.get('Duration', ''))
            current_experience = {"Company": line.split(":", 1)[1].strip()}
        elif current_section == "Work Experience" and line.startswith("Role:"):
            current_experience["Role"] = line.split(":", 1)[1].strip()
        elif current_section == "Work Experience" and line.startswith("Duration:"):
            current_experience["Duration"] = line.split(":", 1)[1].strip()
        elif current_section == "Skills" and line.startswith("-"):
            data['Skills'].append(line[1:].strip())

    # Add the last education and work experience entries
    if current_education:
        data['Institution'].append(current_education.get('Institution', ''))
        data['Degree'].append(current_education.get('Degree', ''))
        data['Major'].append(current_education.get('Major', ''))
        data['Education Duration'].append(current_education.get('Duration', ''))
    if current_experience:
        data['Company'].append(current_experience.get('Company', ''))
        data['Role'].append(current_experience.get('Role', ''))
        data['Work Duration'].append(current_experience.get('Duration', ''))

    # Pad lists to the same length
    max_len = max(
        len(data['Institution']),
        len(data['Company']),
        len(data['Degree']),
        len(data['Major']),
        len(data['Education Duration']),
        len(data['Role']),
        len(data['Work Duration'])
    )

    for key in ['Institution', 'Degree', 'Major', 'Education Duration', 'Company', 'Role', 'Work Duration']:
        while len(data[key]) < max_len:
            data[key].append('')

    # Pad the Skills list to match the length
    data['Skills'] = [", ".join(data['Skills'])] * max_len

    # Convert the data into a DataFrame
    df = pd.DataFrame({
        'Name': [data['Name']] * max_len,
        'Institution': data['Institution'],
        'Degree': data['Degree'],
        'Major': data['Major'],
        'Education Duration': data['Education Duration'],
        'Company': data['Company'],
        'Role': data['Role'],
        'Work Duration': data['Work Duration'],
        'Skills': data['Skills']
    })

    return df



# Streamlit app
st.title("Data Talk")

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
