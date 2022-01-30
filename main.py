from indicators import *
from fastapi import FastAPI

app = FastAPI()

@app.get("/api/v1/indicators/{pair}/")
async def get_indicators(pair: str):
    pair = '/'.join(pair.split('-')).upper()
    timeframe = '1h'
    return {f"{main(pair, timeframe)}"}