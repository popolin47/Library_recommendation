# Using GenAI for Library Recommendations: Initial Results from the NPM Ecosystem

This project investigates the use of **Large Language Models (LLMs)** (OpenAI’s ChatGPT 3.5-turbo) for two tasks:

- **RQ1:** Recommending JavaScript libraries given a task description  
- **RQ2:** Generating concise descriptions for JavaScript libraries given their names  

We evaluate the model under different **temperature settings** and multiple runs to measure accuracy, consistency, and semantic similarity with ground-truth GitHub descriptions.

## Methodology

### RQ1: Library Recommendation
- **Input:** Task description (from GitHub project descriptions in `task_list.csv`)
- **Prompt:**  
  > You are a JavaScript backend developer. Recommend an npm library based on the given task. Return only the library name.
- **Temps tested:** `0`, `0.2`, `0.5`  
- **Runs:** Each temperature repeated **5 times**  
- **Evaluation:**  
  - Exact Match: matches the true library  
  - In List: library exists in dataset but not the expected one  
  - Not in List: library not in dataset  

### RQ2: Library Description
- **Input:** Library name (from `lib_name.csv`)  
- **Prompt:**  
  > You are a JavaScript backend developer. Provide a concise description for the JavaScript library named '{lib}'.
- **Temps tested:** `0.2`, `0.5`, `0.7`  
- **Runs:** Each temperature repeated **5 times**  
- **Evaluation:** Semantic similarity via `all-MiniLM-L6-v2` SentenceTransformer  
  - Cosine similarity between generated and GitHub description  
  - Per-library average across 5 runs  

---

## 📊 Results (Summary)

- **RQ1:**  
  - Lower temperatures (0.2) yielded more consistent and accurate recommendations.  
  - Accuracy highest for **Top-tier** libraries, lowest for **Bottom-tier**, reflecting popularity bias.  

- **RQ2:**  
  - Higher temperatures (0.7) produced slightly more natural and semantically closer descriptions.  
  - Averaging across 5 runs stabilized scores, reducing randomness.  

---

## 🚀 How to Reproduce

1. Install dependencies:
   ```bash
   pip install openai pandas sentence-transformers scikit-learn python-dotenv
2. Add your OpenAI API key to .env:
  OPENAI_API_KEY=your_api_key_here
3. Run notebooks:
  - github_description_fetcher.ipynb → fetch GitHub repo descriptions  
  - RQ12.ipynb → run experiments for RQ1 and RQ2
