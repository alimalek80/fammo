import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

BASE_SYSTEM_PROMPT = (
    "You are a helpful veterinary-style assistant that ONLY answers questions about PETS: dogs and cats.\n"
    "- If the user asks about anything unrelated to dogs/cats, respond briefly: "
    "'I only handle dog/cat topics. Please ask about dogs or cats.'\n"
    "- Support ANY language. Detect the user's language and reply in that language.\n"
    "- Keep tone friendly, concise, and practical. Don't give medical advice; suggest what needs to be done, "
    "  emphasize you are not a veterinarian, and recommend seeing a vet when needed.\n"
    "- IMPORTANT: Do NOT greet with 'Hi [name]' in every message. Only use casual greetings in the FIRST message. "
    "  In subsequent messages, address the user naturally by their first name when relevant (e.g., 'Great question, [name]!' "
    "  or '[name], based on your pet's profile...') without repeating 'Hi' each time.\n"
    "- If the user has NO name: address them as 'Dear user' and politely suggest: "
    "  'If you complete your profile, I can address you by your name!' Then answer their question.\n"
)

def pet_answer(user_text: str, user_name: str | None = None, pet_profiles: str | None = None, is_first_message: bool = False) -> str:
    """Answer a user question with optional personalization.

    user_name: first name for friendly addressing (optional)
    pet_profiles: a plain-text summary of the user's pet(s). If multiple pets are present,
                  include all and specify their names. The assistant should use this data
                  when the question refers to "my pet" or a specific name. If ambiguous,
                  ask which pet the user means.
    is_first_message: True if this is the first message in the conversation (allows greeting)
    """
    system_parts = [BASE_SYSTEM_PROMPT]
    if user_name:
        greeting_note = " (This is the first message, so you may greet them with 'Hi [name]!')" if is_first_message else " (Use their name naturally in responses, not as a greeting)"
        system_parts.append(f"User first name: {user_name}{greeting_note}\n")
    else:
        system_parts.append("No user name available. Address as 'Dear user' and suggest profile completion.\n")
    
    if pet_profiles:
        system_parts.append(
            "Use the following pet profile data to tailor your answers. If information is missing, "
            "ask a brief clarifying question before giving detailed guidance.\n" + pet_profiles
        )

    system_prompt = "\n".join(system_parts)

    resp = client.responses.create(
        model="gpt-5",
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text},
        ]
    )
    # Safe read
    return resp.output_text.strip() if getattr(resp, "output_text", None) else "Sorry, I couldn’t generate a reply."