from fastapi import FastAPI
from utils.main_util import main

app = FastAPI()

@app.post('/query')
async def ask_llm(message):
    return main(message)
