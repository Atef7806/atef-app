from transformers import pipeline

# نموذج تحليل الجمل الجاهز من HuggingFace
nlp = pipeline("feature-extraction", model="bert-base-uncased")

def analyze_cv_against_keywords(cv_text, keywords):
    if not cv_text or not keywords:
        return 0.0

    cv_text_lower = cv_text.lower()
    matched_keywords = [kw for kw in keywords if kw.lower() in cv_text_lower]
    
    match_percentage = (len(matched_keywords) / len(keywords)) * 100
    return round(match_percentage, 2)
