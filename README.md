# ResumeAI-Parser+

Recruiters today face the overwhelming task of filtering through thousands, sometimes hundreds of thousands, of resumes from platforms like LinkedIn and Naukri. With the sheer volume of applications, manually reviewing every PDF or DOCX file to identify top candidates becomes not only time-consuming but prone to human error, often resulting in missing out on great talent.

ResumeAI-Parser+ solves this problem by automating the extraction of key resume details, turning resume files into actionable data. With ResumeAI-Parser+, recruiters can quickly analyze candidates based on critical factors like education, years of experience, current company, and skills—presented neatly in an Excel sheet. This allows for efficient sorting and filtering, enabling teams to identify the most qualified candidates in minutes rather than days.

Whether you're hiring for a single role or filling numerous positions across departments, ResumeAI-Parser+ acts as the bridge between endless resumes and the best talent, streamlining the recruitment process, saving time, and ensuring that no great candidate is overlooked. Let AI handle the resume grunt work while you focus on what matters—finding the perfect fit for your team.

## Overview

The **ResumeAI-Parser+** is a Streamlit-based application that allows users to upload multiple resumes in PDF or DOCX format and automatically extracts key details such as the candidate's name, education, work experience, and skills using OpenAI's GPT-3.5-turbo model. The extracted information is presented in a structured table format and can be exported to an Excel file for further analysis.

## Features

- **Supports Multiple File Formats**: Users can upload resumes in PDF and DOCX formats.
- **Automatic Information Extraction**: Uses OpenAI’s GPT-3.5-turbo model to extract information like name, education, work experience, and skills.
- **Structured Output**: Parsed and structured information is displayed in a user-friendly table format.
- **Excel Export**: Extracted resume data can be exported to an Excel file.
- **Downloadable Summary**: The generated Excel summary can be downloaded directly from the app.

## Requirements

- Python 3.7+
- Streamlit
- OpenAI Python package
- PyPDF2
- python-docx
- Pandas
- An OpenAI API key

### Installation

1. **Clone the repository**

    ```bash
    https://github.com/umang-algo/ResumeAI_Parser.git
    cd resumeai_parser
    ```

2. **Create a virtual environment and activate it**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. **Install the required libraries**

    ```bash
    pip install -r requirements.txt
    ```

4. **Run the application**

    ```bash
    streamlit run resumeai_parser.py
    ```

## Features

1. **Upload Resumes**: Click the “Upload multiple resume files” button to upload PDF or DOCX files.
2. **Enter API Key**: Provide your OpenAI API key to access the GPT-3.5-turbo model.
3. **Extract Information**: The application will automatically process each uploaded resume, extract key information, and display it.
4. **Download Summary**: After processing, download the structured data as an Excel file by clicking the “Download Excel File” button.

## Functions Overview

### `extract_text_from_pdf(pdf_file)`
Extracts text from PDF files using the `PyPDF2` library.

### `extract_text_from_docx(docx_file)`
Extracts text from DOCX files using the `python-docx` library.

### `get_completion(prompt, api_key)`
Sends a prompt to the OpenAI API and retrieves the completion based on the GPT-3.5-turbo model.

### `extract_resume_info(resume_text, api_key)`
Generates a prompt to extract key resume information and sends it to OpenAI for processing.

### `parse_extracted_info(extracted_info)`
Parses the extracted text and structures it into a DataFrame with the fields: Name, Education, Work Experience, and Skills.

## Exporting Data

After all resumes have been processed, the app provides the option to export the summarized data as an Excel file. This file includes all the extracted information from the uploaded resumes.

## Error Handling

- The app handles incorrect file types and errors during file reading gracefully, showing appropriate error messages.
- If no API key is provided or invalid files are uploaded, the app displays instructions to rectify the issue.

## License

This project is licensed under the MIT License.
