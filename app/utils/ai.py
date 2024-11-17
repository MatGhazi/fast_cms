
import os
from dotenv import load_dotenv
env_path = os.path.join(os.path.dirname(__file__), '..', '..', 'env', '.env.api')
print(f"Loading .env file from: {env_path}")
load_dotenv(env_path)
# load_dotenv('env/.env.api')
from openai import OpenAI
# /mnt/d/Projects/fast_cms/app/utils/../env/.env.api
# /mnt/d/Projects/fast_cms/env/.env.api
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)
def get_completion(word, model="gpt-4o-mini"):

    # model="gpt-4o-mini"
    # word = 'manipulate'
    # client = OpenAI()

    completion = client.chat.completions.create(
        model= model,
        messages=[{"role": "user", 
                   "content": f'''Generate 3 simple sentences for english learner using 
                    the word {word}. First, give the most prevalent Persian meaenings and 
                    then give examples by using possible None and verb in the sentence. Give the output in the structure of Meaning: ..., and examples: ...'''
                    }], # and put persion meaening beside}]
        temperature=1,
        max_tokens=50,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        response_format={"type": "text"}
    )
    result = completion.choices[0].message
    print(result)
    # return markdown.markdown(result.content)
    return result.content

def GenerateStory(words, count, model="gpt-4o-mini"):
    completion = client.chat.completions.create(
        model= model,
        messages=[{"role": "user", 
                   "content": f'''Generate a short meaningful story for english learner using  {words}. Try to use at least {count} of these words in the story. 
                   Try to use simple words and finish the story in less than 80 words.'''
                    }], # and put persion meaening beside}]
        temperature=1,
        max_tokens=200,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        response_format={"type": "text"}
    )
    result = completion.choices[0].message
    print(result)
    # return markdown.markdown(result.content)
    return result.content

def GenerateVoice(audio_path, story_text):

    # speech_file_path = Path(__file__).parent / "speech.mp3"
    response = client.audio.speech.create(
    model="tts-1",
    voice="alloy",
    input=f"{story_text}"
    )
    response.stream_to_file(audio_path)