import git
import psutil
import time
import os
from fastapi import FastAPI
from covid19etl.covid19 import Covid19


app = FastAPI()


@app.get("/")
def read_root():
    return {"data": "Running!"}


@app.get("/run")
def run():
    start_time = time.time()
    pipeline = Covid19()
    pipeline.extract()
    pipeline.transform()
    pipeline.load()
    print("Memory usage:", usage())
    print("--- %s seconds ---" % (time.time() - start_time))

    github_covid19_chile = os.environ['GITHUB_COVID19_CHILE']

    if os.path.isdir("./covid19-chile"):
        os.system("rm -rf ./covid19-chile")

    # Check out via HTTPS
    git.Repo.clone_from(github_covid19_chile, 'covid19-chile')
    # repo.index.add('README.md')
    my_repo = git.Repo('covid19-chile')

    # copy files
    os.system('cp ./output/covid19.csv ./covid19-chile/covid19.csv')
    os.system('cp ./output/covid19.json ./covid19-chile/covid19.json')
    os.system('cp ./output/covid19.sql ./covid19-chile/covid19.sql')
    if my_repo.is_dirty(untracked_files=True):

        print('Changes detected.')
        # commit
        from git import Actor
        my_repo.index.add('**')
        author = Actor("Sergio", "sergio@sergiojulio.com")
        committer = Actor("Sergio", "sergio@sergiojulio.com")
        my_repo.index.commit('Commit from Cloud Run', author=author, committer=committer)
        # print(my_repo.remotes.origin.pull())
        print(my_repo.remotes.origin.push('master:master'))

    else:
        print('No changes detected.')

    # kill process system exit 0
    return {"data": "successfully"}


def dump(obj):
    for attr in dir(obj):
        print("obj.%s = %r" % (attr, getattr(obj, attr)))


def usage():
    process = psutil.Process(os.getpid())
    return process.memory_info()[0] / float(2 ** 20)

