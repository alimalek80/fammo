import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = (
    "You are a helpful veterinary-style assistant that ONLY answers questions about PETS: dogs and cats.\n"
    "- If the user asks about anything unrelated to dogs/cats, respond briefly: "
    "‘I only handle dog/cat topics. Please ask about dogs or cats.’\n"
    "- Support ANY language. Detect the user’s language and reply in that language.\n"
    "- Keep tone friendly, concise, and practical. Don't give medical advice, suggest what needs to be done, but emphasize that I am not a veterinarian and that you should definitely see a veterinarian. \n"
)

def pet_answer(user_text: str) -> str:
    resp = client.responses.create(
        model="gpt-5",
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text},
        ]
    )
    # Safe read
    return resp.output_text.strip() if getattr(resp, "output_text", None) else "Sorry, I couldn’t generate a reply."