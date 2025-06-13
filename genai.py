from google import genai
from google.genai import types


def gen_response(instruction, prompt):
    client = genai.Client(api_key="AIzaSyADpqA0aYHK4kzMEsqSDZF_KIezRTPGAck")

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(system_instruction= instruction),
        contents=prompt,
    )

    return response.text

def parse_command(command:str):
    instruction = '''
        You are a command dispatcher. Your task is to analyze user input and identify the intended command and its associated keyword(s).

        **Available Commands and their Functions:**

        * `introduce`: Introduce yourself. Set keyword as null.
        * `foretell`: Tell a fortune based on the user's question.
        * `meme`: Find a meme relevant to the user's request. Note 虾片 means meme. Note user might also want to find some memes without particular topic, in such cases, you should set keyword as random. The keyword for this command should be as simple and accurate as possbile; avoid include adjectives in keyword for this command.
        * `joke`: Tell a joke. Set keyword as null.

        **Keyword Extraction:**

        The keyword is the core search term or question extracted from the user's input that is relevant to the identified command.

        **Output Format:**

        `command ; keyword`

        **Example:**

        **User Input:** "Tell me what my luck will be tomorrow"
        **Your Output:** `foretell ; what my luck will be tomorrow`

        **User Input:** "Say hello"
        **Your Output:** `introduce ; null`

        **User Input:** "Find a funny cat picture"
        **Your Output:** `meme ; funny cat picture`

        Focus on accurately determining the command based on keywords or intent and extracting the most relevant information as the keyword. Ensure a single semicolon separates the command and the keyword in your output.

    '''

    response = gen_response(instruction=instruction,prompt=command)
    part1, part2 = [part.strip() for part in response.split(";")]
    return part1,part2

if __name__ == "__main__":
    instruction = "You are a Tarot reader. Provide a concise general fortune reading based on a single, unspecified Tarot card pull within 100 words. Focus on interpretations associated with the Major or Minor Arcana. Tell the fortune honestly and directly,don't be ambiguous."
    prompt = "say something nice"
    print(gen_response(instruction=instruction,prompt=prompt))