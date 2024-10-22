import os
from openai import OpenAI

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def summarize_text(text):
    prompt = f"Summarize the following text, extracting key events and dates:\n\n{text}"
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        summary = response.choices[0].message.content
        return summary
    except Exception as e:
        print(f"Error in GPT-4 API call: {str(e)}")
        return "Error in summarization"

def generate_narrative():
    try:
        with open('timeline.md', 'r') as timeline_file:
            timeline_content = timeline_file.read()
        
        prompt = f"Generate a coherent narrative based on the following timeline of events:\n\n{timeline_content}"
        
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        narrative = response.choices[0].message.content
        
        with open('narrative.md', 'w') as narrative_file:
            narrative_file.write(narrative)
    except Exception as e:
        print(f"Error generating narrative: {str(e)}")
