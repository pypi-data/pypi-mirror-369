import os

DEFAULT_MODEL = "openai/gpt-4o-mini"
MAX_RETRIES = 3
BASE_IAI_URL = os.getenv("BASE_IAI_URL", "https://irona-ai")
DEFAULT_API_URL = os.getenv("DEFAULT_API_URL", "https://api.openai.com/v1/chat/completions")
GIST_URL = os.getenv("GIST_URL", "https://gist.githubusercontent.com/tshrjn/f55b3ebd90eda8a0e65bf8435419edff/raw/")
MODEL_SELECT_ENDPOINT = os.getenv("MODEL_SELECT_ENDPOINT", f"{BASE_IAI_URL}--model-select.modal.run")
DEFAULT_TIMEOUT=15