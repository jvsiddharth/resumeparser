import os
import textract
import pandas as pd
import re
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

def extract_text_from_resumes(directory):
    """
    Extract text from resumes in a directory.
    """
    file_paths = []
    for file_name in os.listdir(directory):
        if file_name.endswith('.docx'):
            file_path = os.path.join(directory, file_name)
            text = textract.process(file_path).decode('utf-8')
            file_paths.append(text)
    return pd.DataFrame(data=file_paths, columns=['Raw_Details'])

def preprocess_text(text):
    """
    Preprocess raw text data.
    """
    # Convert to lowercase
    text = text.lower()
    
    # Remove HTML tags
    text = re.sub('<.*?>', '', text)
    
    # Remove URLs
    text = re.sub(r'http\S+', '', text)
    
    # Remove numeric characters
    text = re.sub(r'\d+', '', text)
    
    # Tokenize text
    tokenizer = RegexpTokenizer(r'\w+')
    tokens = tokenizer.tokenize(text)
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [word for word in tokens if word not in stop_words]
    
    return ' '.join(filtered_tokens)

def calculate_score(job_requirements, candidate_skills, weights):
    """
    Calculate a matching score between job requirements and candidate skills.
    """
    # Split job requirements and candidate skills into words
    job_req_words = job_requirements.lower().split()
    candidate_skills_words = candidate_skills.lower().split()
    
    # Initialize match count
    match_count = 0
    
    # Calculate match count based on weighted keywords
    for word in job_req_words:
        if word in candidate_skills_words:
            match_count += weights.get(word, 1)  # Default weight is 1 if not specified
    
    return match_count

def find_resume_matches(df, job_requirements, weights):
    """
    Find matching scores for all resumes in the DataFrame.
    """
    # Create a new column 'Resume_Details' with preprocessed text
    df['Resume_Details'] = df['Raw_Details'].apply(preprocess_text)
    
    # Calculate match score for each resume
    df['Match_Score'] = df['Resume_Details'].apply(lambda x: calculate_score(job_requirements, x, weights))
    
    return df

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get job requirements, resumes directory, and weights from form submission
        job_requirements = request.form['job_requirements']
        resumes_directory = request.form['resumes_directory']
        weights = request.form['weights']
        weights = dict(map(str.strip, item.split(':')) for item in weights.split(','))  # Parse weights

        # Convert weights to appropriate types
        weights = {key: int(value) for key, value in weights.items()}

        # Process resumes
        df = preprocess_resumes(resumes_directory, job_requirements, weights)

        # Sort by match score
        df = df.sort_values(by='Match_Score', ascending=False)

        # Convert DataFrame to JSON and return
        return jsonify(df.to_dict(orient='records'))
    else:
        return render_template('index.html')

def preprocess_resumes(directory, job_requirements, weights):
    """
    Preprocess resumes and find matches.
    """
    # Extract text from resumes
    df = extract_text_from_resumes(directory)

    # Find matches
    df = find_resume_matches(df, job_requirements, weights)

    return df

if __name__ == '__main__':
    app.run(debug=True)
