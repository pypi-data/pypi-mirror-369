from openai import OpenAI
from google.genai import errors

class chunk_summarizer():

    def __init__(self,base_url, model):
        self.base_url = base_url
        self.model = model
        self.client = OpenAI(base_url = self.base_url)
    
    def summarize_chunks(self,final_ranked_list):
        summaries = []

        for result_item in final_ranked_list:
            index = result_item['index']
            question = result_item['question']
            search_results = result_item['search_results']

            if search_results and isinstance(search_results[0], tuple):
                # Extract only the text chunks, ignore scores
                chunks_text = [chunk for chunk, score in search_results]
            else:
                chunks_text = search_results
            
            # Combine all chunks into one text for summarization
            combined_text = "\n\n".join(chunks_text)

            prompt_filled = f"""
You are a concise summarizer for a retrieval-augmented generation (RAG) system.

Your task:
- Summarize the given text chunk so it preserves all important facts relevant to the user's query.
- Remove any unrelated or redundant information.
- Be concise, clear, and factual.
- Avoid adding new interpretations or assumptions.

Text chunk:
{combined_text}

Output format:
- A short paragraph or 3 to 5 bullet points containing only the key information from the chunk relevant to the query.

    """
        try:
                response = self.client.chat.completions.create(
                    model= self.model,
                    messages=[
                        {"role": "system", "content": prompt_filled},
                        {"role": "user", "content": question},
                    ]
                )
                summary = response.choices[0].message.content
                result_item = {
                    "index": index,
                    "question": question,
                    "search_results": [summary]
                }
                summaries.append(result_item)

        except errors.APIError as e:
                print(e.code)
                print(e.message)

        return summaries