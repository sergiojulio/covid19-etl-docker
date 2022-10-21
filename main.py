from typing import Optional
from fastapi import FastAPI
from covid19etl.covid19 import Covid19
import psutil
import time
import os

app = FastAPI()


@app.get("/")
def read_root():
    return {"data": "none"}


@app.get("/run")
def run():
    start_time = time.time()
    pipeline = Covid19()
    pipeline.extract()
    pipeline.transform()
    pipeline.load()
    print("Memory usage:", usage())
    print("--- %s seconds ---" % (time.time() - start_time))
    return {"data": "successfully"}


def dump(obj):
    for attr in dir(obj):
        print("obj.%s = %r" % (attr, getattr(obj, attr)))


def usage():
    process = psutil.Process(os.getpid())
    return process.memory_info()[0] / float(2 ** 20)

