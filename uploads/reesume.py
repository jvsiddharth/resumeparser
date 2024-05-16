import os
import subprocess
import docx2txt

def convert_to_txt(doc_file):
    txt_file = os.path.splitext(doc_file)[0] + ".txt"
    subprocess.run(["antiword", doc_file, "-t", "plain", "-w", "0", ">", txt_file], shell=True)
    return txt_file

def parse_doc(doc_file):
    txt_file = convert_to_txt(doc_file)
    with open(txt_file, "r") as f:
        text = f.read()
    os.remove(txt_file)  # Remove the temporary .txt file
    return text

def score_resume(resume_text, keywords_weights):
    print("Resume Text:\n", resume_text)
    resume_tokens = resume_text.lower().split()
    matched_keywords = []
    score = 0
    for keyword, weight in keywords_weights.items():
        if keyword.lower() in resume_tokens:
            matched_keywords.append(keyword)
            score += weight
    print("Matched Keywords:", matched_keywords)
    return score

def main():
    # Define keywords and their weights
    keywords_weights = {
        "PeopleSoft": 10,
        "java": 8,
        "communication": 5,
        "teamwork": 5,
        # Add more keywords and weights as needed
    }

    # Score resumes
    scores = {}
    for file_name in os.listdir("."):
        if file_name.endswith(".doc"):
            resume_text = parse_doc(file_name)
            resume_num = os.path.splitext(file_name)[0]  # Extract resume number from file name
            scores[f"Resume_{resume_num}"] = score_resume(resume_text, keywords_weights)

    # Sort resumes by score
    sorted_resumes = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    # Print or save sorted resumes with scores
    for resume, score in sorted_resumes:
        print(f"{resume}: Score {score}")

if __name__ == "__main__":
    main()
