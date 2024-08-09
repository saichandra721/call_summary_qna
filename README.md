## To Test APIs
   Hosted server on AWS EC2 
   Access using following FastAPI Docs
   http://43.205.255.16:8000/docs

# Here we have two APIs
1. /process_pdfs
2. /top5_questions



## Setup
1. Clone the repository
2. Create a virtual environment
   ```sh
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   pip3 install -r requirements.txt
   uvicorn main:app --reload
   

