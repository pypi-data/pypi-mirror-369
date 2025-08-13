import os
from dotenv import load_dotenv, find_dotenv

# --- Recommended Changes ---
# Use find_dotenv() to reliably locate the .env file by searching
# in the current directory and parent directories. This is more robust.
dotenv_path = find_dotenv()

if not dotenv_path:
    print("Warning: .env file not found. Please ensure it is in your project's root directory.")
else:
    # Use override=True to ensure that the variables from your .env file
    # take precedence over any existing system environment variables.
    load_dotenv(dotenv_path=dotenv_path, override=True)
    print(f".env file loaded from: {dotenv_path}")
# --- End of Changes ---

from google.genai import errors
# Import classes from sibling modules (package-style)
from .decompose import DecomposeQuestion, QuestionFilter
from .chunk_extractor import ChunkExtraction
from .reranker import ReRanker
from .final_llm import final_query

#pydantic classes - check for each method of class in all files
# main shd be a python script, not a module
#create new dir
#pip install
# create py scipt
# check for each class functaionaltiy for defined input/output

def run_rag_pipeline(
    user_question: str,
    model: str | None = None,
    base_url: str | None = None
):
    model = os.getenv("model")
    base_url = os.getenv("base_url")

    # For debugging purposes, to confirm variables are loaded
    print(f"Model loaded from .env: {model}")
    print(f"Base URL loaded from .env: {base_url}")

    if not model:
        raise ValueError("OpenAI model name not set. Set the model env var")
    if not base_url:
        raise ValueError("OpenAI base URL not set. Set the base_url env var")

    try:
        print("\n--- Processing your question, please wait... ---")
        # Decomposition
        decomposer = DecomposeQuestion(model=model, base_url=base_url)
        print("\n--- Generating Sub-questions ---")
        sub_questions = decomposer.decompose_function(user_question)

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

    except errors.APIError as e:
        print(e.code)
        print(e.message)

if __name__ == "__main__":
    user_question = "Explain Planck's Quantum Hypothesis."
    answers = run_rag_pipeline(user_question)
