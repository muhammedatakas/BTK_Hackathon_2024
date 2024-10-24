import os
import google.generativeai as genai

# API KEY 
genai.configure(api_key= os.environ["API_KEY"])

# Model yapılandırması
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro-002",
    generation_config=generation_config,
    system_instruction="Summarize the following text:",
)

# Metin özetleme fonksiyonu
def create_summary(obj):
    for item in obj:
        prompt = f"Summarize the following text: {item['text']}"
        chat_session = model.start_chat(history=[])
        response = chat_session.send_message(prompt)
        item["summary"] = response.text.strip()  # Özetlenen metni al ve temizle
    return obj

# Örnek veri
obj = [
    {
        "name": "Lost Lilly",
        "text": """In the heart of a bustling city, amidst towering skyscrapers and endless traffic, lived a young woman named Lily. Unlike her city-dwelling peers, Lily harbored a deep yearning for nature. She dreamed of verdant forests, babbling brooks, and the sweet scent of wildflowers. Every weekend, she would escape the urban jungle, venturing into the nearby countryside to find solace in the tranquility of nature.

        One sunny afternoon, Lily decided to explore a new hiking trail she had heard about. The trail led her through a dense forest, the towering trees forming a canopy overhead that blocked out the sunlight. The air was filled with the sweet scent of pine needles and damp earth, and the only sound was the chirping of birds and the rustling of leaves.

        As Lily hiked deeper into the forest, she came across a hidden clearing. A small, crystal-clear pond shimmered in the sunlight, surrounded by a vibrant array of wildflowers. Lily was captivated by the beauty of the scene. She sat down on a fallen log and gazed at the pond, lost in thought.

        Suddenly, Lily heard a faint rustling sound. She looked up and saw a small, furry creature emerging from the undergrowth. It was a fawn, its large, brown eyes filled with curiosity. Lily watched as the fawn approached the pond, taking a cautious sip of water.

        As the fawn drank, Lily noticed a small, delicate flower growing near its hooves. It was a white lily, its petals glistening in the sunlight. The flower was so rare and beautiful that Lily couldn't resist picking it. She carefully plucked the lily and held it up to her nose, inhaling its sweet fragrance.

        As Lily admired the lily, she felt a sense of peace wash over her. She had found the perfect place to escape the hustle and bustle of the city, and she knew she would return to this hidden clearing again and again.

        As the sun began to set, Lily decided it was time to head back. She thanked the fawn for its company and continued her journey through the forest. As she walked, she held the lily close to her heart, a reminder of her peaceful encounter with nature.
        """
    },
    {
        "name": "The Whispering Willow",
        "text": """ **The Whispering Willow**

        In a small, secluded village nestled among rolling hills, there lived an elderly woman named Anya. She was known throughout the village for her wisdom and her love of nature. Her home was surrounded by a garden filled with vibrant flowers and towering trees, and she spent most of her days tending to her plants.

        Among the trees in Anya's garden was a particularly ancient and majestic willow. Its branches, gnarled and twisted, reached towards the sky, and its leaves rustled gently in the breeze. The villagers believed that the willow held secrets of the forest and that it could communicate with the spirits of nature.

        One day, a young boy named Ivan wandered into Anya's garden. He was drawn to the willow tree and sat down beneath its shade. As he gazed up at the towering branches, he heard a faint whisper. At first, he thought it was just the wind, but then he heard it again, clearer this time.

        "Come closer," the willow whispered.

        Ivan hesitated, but his curiosity overcame his fear. He moved closer to the tree and listened.

        "I have a story to tell you," the willow continued. "Long ago, this land was covered in a vast, ancient forest. The trees were tall and strong, and the animals roamed freely. But then came the humans, and they cut down the trees to build their homes and villages. Many of my friends were lost, and the forest was forever changed."

        As the willow spoke, Ivan felt a pang of sadness. He had never thought about the impact humans had on the environment.

        "But there is hope," the willow continued. "If we work together, we can protect the remaining forests and ensure that future generations can enjoy their beauty."

        Ivan nodded, feeling a sense of determination. He knew that he wanted to help protect the natural world.

        From that day forward, Ivan became a passionate environmentalist. He planted trees, cleaned up litter, and educated his friends and family about the importance of protecting the planet. And whenever he felt overwhelmed, he would visit the whispering willow and remember the story it had told him.
        """
    }
]
summarized_obj = create_summary(obj)
print(summarized_obj)


