import fal_client
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Your test prompt
test_prompt = "Brett_memecoin Brett, the legendary character, dancing with exaggerated moves in a vibrant digital space. His expression is full of joy and excitement, showcasing his love for video games. Around him are vivid symbols of partnership and growth, like interlinking circuit nodes and upward arrows, symbolizing the thriving ecosystem. The backdrop is a blue-themed, futuristic cityscape to represent the Base blockchain. Text overlay reads 'Dance through Crypto!' at the top and 'Join the BASE Revolution!' at the bottom"

# Define the Lora configuration
LORA_PATH = "https://storage.googleapis.com/fal-flux-lora/bb6ec5438d5c4ca7897cbf0df40fb051_pytorch_lora_weights.safetensors"

def generate_image(prompt):
    try:
        # Make the API call with Lora configuration
        result = fal_client.subscribe(
            "fal-ai/flux-lora",
            arguments={
                "prompt": prompt,
                "loras": [
                    {
                        "path": LORA_PATH,
                        "scale": 1
                    }
                ],
                "embeddings": [],
                "image_size": "portrait_16_9",
                "num_inference_steps": 28,
                "guidance_scale": 3.5,
                "enable_safety_checker": True
            }
        )

        # Extract the image URL from the result
        if result and result.get('images') and len(result['images']) > 0:
            return result['images'][0]['url']
        else:
            return "No image URL found in the response"

    except Exception as e:
        return f"Error generating image: {str(e)}"

if __name__ == "__main__":
    # Generate image using the test prompt
    image_url = generate_image(test_prompt)
    print(f"Generated image URL: {image_url}")
