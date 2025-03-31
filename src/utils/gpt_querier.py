import os
import base64
import openai
import configparser

def generate_gpt_response(prompt, model="gpt-4o-mini", max_tokens=150):
    """
    Generates a response from OpenAI's GPT model based on the provided prompt.

    Args:
        prompt (str): The input prompt to send to the GPT model.
        model (str): The specific GPT model to use (default is "gpt-4o-mini").
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

def encode_image(image_path):
    """
    Encodes an image to a base64 string.

    Args:
        image_path (str): Path to the image file.

    Returns:
        str: Base64 encoded string of the image.
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def generate_response_with_image(image_path, prompt):
    """
    Generates a response from GPT-4 Vision API based on the provided image and prompt.

    Args:
        image_path (str): Path to the image file.
        prompt (str): Text prompt to guide the model's response.

    Returns:
        str: The generated response from the model.
    """
    config = configparser.ConfigParser()
    config.read('config.ini')
    openai.api_key = config['DEFAULT']['OPENAI_API_KEY']

    # Encode the image to base64
    base64_image = encode_image(image_path)

    # Prepare the payload
    headers = {
        "Authorization": f"Bearer {openai.api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 300
    }

    # Make the API request
    response = openai.ChatCompletion.create(**payload)

    # Extract and return the response content
    return response.choices[0].message.content.strip()
