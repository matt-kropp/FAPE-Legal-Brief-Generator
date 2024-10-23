import os
from openai import OpenAI

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def summarize_text(text):
    if not text.strip():
        return "No readable text content found in document."
        
    prompt = f"""Summarize the following text, extracting key events and dates. Format the output in markdown:
    - Use '##' for main sections
    - Use bullet points for events
    - Use bold text for dates
    - Use italics for important names or terms
    
    Text to summarize:
    {text}"""
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        summary = response.choices[0].message.content
        return summary
    except Exception as e:
        print(f"Error in GPT-4 API call: {str(e)}")
        return "Error in summarization"

def generate_narrative(timeline_content, pdf_contents):
    try:
        # First, summarize all PDF contents
        summaries = []
        for pdf_content in pdf_contents:
            # Extract text from PDF content
            from utils.pdf_processor import extract_text_from_pdf
            text = extract_text_from_pdf(pdf_content)
            if text.strip():
                summary = summarize_text(text)
                summaries.append(summary)
        
        # Combine timeline and summaries for narrative generation
        combined_content = f"Timeline:\n{timeline_content}\n\nSupporting Documents:\n"
        for i, summary in enumerate(summaries, 1):
            combined_content += f"\nDocument {i}:\n{summary}\n"
        
        prompt = f"""Generate a coherent legal brief narrative based on the following timeline and supporting documents. Format the output in markdown:
        - Use '##' for main sections (Background, Analysis, Conclusion)
        - Use '###' for subsections
        - Use bullet points for key events
        - Use bold text for dates and important terms
        - Use italics for case citations or party names
        - Use blockquotes for direct quotes from documents
        
        Content to process:
        {combined_content}
        
        Write a clear and professional narrative that incorporates all relevant information chronologically."""
        
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000
        )
        narrative = response.choices[0].message.content
        return narrative
    except Exception as e:
        print(f"Error generating narrative: {str(e)}")
        return f"Error generating narrative: {str(e)}"
