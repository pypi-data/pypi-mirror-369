import os
from dotenv import load_dotenv
load_dotenv()
from google.genai import errors
import json

# Import classes from sibling modules (package-style)
from .decompose import DecomposeQuestion, QuestionFilter
from .chunk_extractor import ChunkExtraction
from .reranker import ReRanker
from .final_llm import final_query

base_url = os.getenv('base_url')
model = os.getenv('model')

def run_rag_pipeline(
    user_question: str,
    model: str = model,
    base_url: str = base_url
):  
    
    if not model:
        raise ValueError("OpenAI model name not set. "
                         "Set the MODEL env var or pass model='gpt-4o', etc.")
    if not base_url:
        raise ValueError("OpenAI base URL not set. "
                         "Set the BASE_URL env var or pass base_url='https://api.openai.com/v1'")
    
    try:

        print("\n--- Processing your question, please wait... ---")

        # Decomposition
        decomposer = DecomposeQuestion(model=model, base_url=base_url)
        print("\n--- Generating Sub-questions ---")
        sub_questions = decomposer.decompose_function(user_question)
        # print("Generated Sub-questions:\n", sub_questions)

        # Filter sub-questions
        question_filter = QuestionFilter(model=model, base_url=base_url)
        print("\n--- Filtering Sub-questions ---")
        filtered_questions = question_filter.filter_subquestions_function(user_question, sub_questions)
        print("Filtered Top 5 Sub-questions:\n", filtered_questions)

        # Sub-questions chunk extractors
        ChunkExtactorInstance = ChunkExtraction()
        print("\n--- Embedding Sub-questions and Extracting Chunks ---")
        filtered_questions_chunks = ChunkExtactorInstance.chunker_function(filtered_questions)
        print("\n--- Chunks Found ---")

        # Chunk re-ranking
        Ranker = ReRanker()
        print("\n--- Re Ranking ---")
        final_ranked_list = Ranker.reranker_function(filtered_questions_chunks)
        print("\n--- Re Ranking Done ---")

        # Feed to LLM
        llm_caller = final_query(model=model, base_url=base_url)
        print("\n--- Querying LLM --- \n")
        FinalAnswers = llm_caller.caller_function(final_ranked_list)
        print(FinalAnswers)

    except  errors.APIError as e:
        print(e.code)
        print(e.message)

if __name__ == "__main__":
    user_question = "Explain Planck's Quantum Hypothesis."
    answers = run_rag_pipeline(user_question)
