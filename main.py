import streamlit as st
import PyPDF2
import google.generativeai as genai
from io import BytesIO
import logging
import re

# logging is very imp ! dont u dare to remove it dear contributor!
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

class SyllabusQuestionGenerator:
    def __init__(self, api_key):
        logging.info("Initializing Syllabus Question Generator")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-pro")
        logging.info("Gemini Pro model initialized successfully")

    def extract_text_from_pdf(self, pdf_file):
        """Extract text from uploaded PDF"""
        try:
            st.info("Extracting text from the uploaded PDF file...")
            logging.info(f"Starting PDF text extraction for file: {pdf_file.name}")
            
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            total_pages = len(pdf_reader.pages)
            logging.info(f"Total pages in PDF: {total_pages}")
            
            text = ''.join([page.extract_text() for page in pdf_reader.pages])
            
            # print 500 chars of extracted text (logging it for making me believe that it works)
            logging.info("Extracted Text Preview (first 500 characters):")
            logging.info(text[:500] + "..." if len(text) > 500 else text)
            
            logging.info(f"Total extracted text length: {len(text)} characters")
            st.success("Text extraction completed successfully!")
            return text
        except Exception as e:
            logging.error(f"Failed to extract text from PDF. Error: {e}")
            st.error(f"Failed to extract text from PDF. Error: {e}")
            return ""

    def generate_questions(self, syllabus_text, difficulty="moderate", num_questions=10):
        """Generate theoretical questions based on syllabus content"""
        logging.info(f"Starting theoretical question generation - Difficulty: {difficulty}, Number of Questions: {num_questions}")
        
        prompt = f"""You are an expert in generating educational theoretical questions.
        Create {num_questions} {difficulty} difficulty theoretical questions 
        based on this syllabus content:

        {syllabus_text}

        Guidelines:
        - Generate thought-provoking theoretical questions
        - Each question should be unique and directly related to the syllabus
        - Provide the syllabus unit for each question
        - Ensure questions encourage deep thinking and analysis

        Format your response as:
        Q1: [Question Text]
        Syllabus Unit: [Relevant Unit]

        Q2: [Question Text]
        Syllabus Unit: [Relevant Unit]

        Continue this pattern for all questions.
        """
        
        try:
            st.info("Generating theoretical questions using AI...")
            logging.info("Sending prompt to Gemini Pro model...")
            
            response = self.model.generate_content(prompt)
            
            logging.info("Questions generation completed")
            logging.info(f"Full response text: {response.text}")
            
            st.success("Theoretical questions generated successfully!")
            return self._parse_questions(response.text)
        except Exception as e:
            logging.error(f"Error generating questions: {e}")
            st.error(f"Error generating questions: {e}")
            return []

    def _parse_questions(self, response_text):
        """Parse generated questions into structured format"""
        logging.info("Starting question parsing")
        questions = []
        
        # parsing using regex (spent 2 hours understanding this logic aah !! AI took my brain lol)
        question_pattern = re.compile(r'Q(\d+):\s*(.+?)\nSyllabus Unit:\s*(.+?)(?=\n\n|$)', re.DOTALL)
        matches = question_pattern.findall(response_text)
        
        logging.info(f"Number of question matches found: {len(matches)}")

        for match in matches:
            try:
                question_number, question_text, syllabus_unit = match
                
                # Clean up 
                question_text = question_text.strip()
                syllabus_unit = syllabus_unit.strip()
                
                questions.append({
                    "text": question_text,
                    "section": syllabus_unit,
                    "difficulty": "Moderate"  # for testing purposes only
                })
                logging.info(f"Successfully parsed Question {question_number}")
            
            except Exception as e:
                logging.warning(f"Could not parse a question: {e}")

        logging.info(f"Total valid questions parsed: {len(questions)}")
        return questions


def main():
    st.set_page_config(
        page_title="Syllabus Theoretical Question Generator",
        page_icon="📚",
        layout="wide",
    )

    st.title("📚 Syllabus Theoretical Question Generator")
    st.markdown(
        "Upload your syllabus and generate **thought-provoking theoretical questions** tailored to its content."
    )

    st.sidebar.header("Configuration")
    api_key = st.sidebar.text_input(
        "Enter Google Gemini API Key",
        type="password",
        help="Get an API key from Google AI Studio",
    )
    difficulty = st.sidebar.selectbox(
        "Question Difficulty", ["Easy", "Moderate", "Hard"]
    )
    num_questions = st.sidebar.slider(
        "Number of Questions", min_value=5, max_value=50, value=10
    )

    uploaded_file = st.file_uploader(
        "Upload Syllabus PDF",
        type="pdf",
        help="Upload a syllabus PDF to generate questions"
    )

    # this generates questions (more stuff to do in this logic!!)
    if uploaded_file and api_key:
        try:
            generator = SyllabusQuestionGenerator(api_key)
            syllabus_text = generator.extract_text_from_pdf(uploaded_file)

            if st.button("Generate Theoretical Questions"):
                with st.spinner("Generating theoretical questions..."):
                    questions = generator.generate_questions(
                        syllabus_text, difficulty.lower(), num_questions
                    )

                st.subheader("Generated Theoretical Questions")
                if questions:
                    for i, question in enumerate(questions, 1):
                        st.markdown(f"**{i}. {question['text']}**")
                        st.markdown(f"*Syllabus Unit:* {question['section']}")
                        st.markdown("---")  # Divider between questions
                else:
                    st.warning("No questions generated. Check the syllabus content or API key.")
        except Exception as e:
            st.error(f"Error processing PDF: {e}")


if __name__ == "__main__":
    main()