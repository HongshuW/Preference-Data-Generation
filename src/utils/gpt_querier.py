import openai
import configparser

def generate_gpt_response(prompt, model="gpt-4o-mini", max_tokens=150):
    """
    Generates a response from OpenAI's GPT model based on the provided prompt.

    Args:
        prompt (str): The input prompt to send to the GPT model.
        model (str): The specific GPT model to use (default is "gpt-3.5-turbo").
        max_tokens (int): The maximum number of tokens to generate in the response.

    Returns:
        str: The generated response from the GPT model.
    """
    try:
        config = configparser.ConfigParser()
        config.read('config.ini')
        openai.api_key = config['DEFAULT']['OPENAI_API_KEY']

        # Create a completion request
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens
        )

        # Extract and return the generated text
        return response.choices[0].message["content"].strip()

    except Exception as e:
        return f"An error occurred: {e}"
