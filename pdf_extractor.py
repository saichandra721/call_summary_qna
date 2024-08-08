import re
import pdfplumber

def extract_text_from_pdf(pdf_path):
    print(f"Extracting pdf text from {pdf_path}")
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

def parse_transcript(transcript):
    # Regular expression pattern to match the time, speaker, and message
    pattern = r'(\d{1,2}:\d{2}) \| (\w+)\n(.+?)(?=\n\d{1,2}:\d{2} \| |\Z)'
    # Find all matches in the transcript
    matches = re.findall(pattern, transcript, re.DOTALL)
    # Format the output as a list of tuples
    result = [(time, speaker, message.strip()) for time, speaker, message in matches]
    return result

def get_questions(modified_transcript):
    question = ''
    questions_dict = {}
    for timestamp,person,text in modified_transcript:
        if question:
            if question not in questions_dict:
                questions_dict[question] = []
            questions_dict[question].append(text) #answer
            question = ''
        if '?' in text and person=='Nathan': #person=='seller':
            question = text
    if question and question not in questions_dict:
        questions_dict[question] = []
    return questions_dict

def extract_seller_from_transcript(transcript):
    # Look for "Participants" section to identify the seller
    print("Extracting seller from transcript")
    participants_section = re.search(r"Participants\s*(.*?)(?=Transcript)", transcript, re.DOTALL)
    if participants_section:
        participants_text = participants_section.group(1).strip()
        # Assume that the first name mentioned after 'xyz' is the seller
        seller_match = re.search(r"xyz\s*(\w+)", participants_text)
        if seller_match:
            return seller_match.group(1)
    return None


def extract_questions_by_speaker(transcript, speaker):
    speaker_questions = []
    lines = transcript.splitlines()

    for line in lines:
        # Identify the speaker's name in the format `timestamp | speaker`
        match = re.match(r"\d{1,2}:\d{2} \| (\w+)", line)
        if match:
            current_speaker = match.group(1)
            if current_speaker == speaker:
                # Extract all sentences that are questions
                questions = re.findall(r'[^.?!]*(?:\?|!)', line)
                for question in questions:
                    # Only keep the sentence if it ends with a question mark
                    if question.strip().endswith('?'):
                        speaker_questions.append(question.strip())

    return speaker_questions