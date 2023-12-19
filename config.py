#config variables below. 
import os

OPENAI_API_KEY = os.environ.get("OPENAIAPIKEY") #set your openai key as an environment variable, or paste as a string here.
# Bot configuration
BOT_NAME = "Santa"
VOICE = "onyx"  # options: alloy, echo, fable, onyx, shimmer, nova
CUSTOM_COMMAND = "I am Santa Claus. I am here to greet people and spread holiday cheer."