from typing import Optional
import git


git.Repo.clone_from('https://github.com/sergiojulio/covid19-chile', 'covid19-chile')
# repo.index.add('README.md')
my_repo = git.Repo('covid19-chile')
# copy files
if my_repo.is_dirty(untracked_files=True):
    print('Changes detected.')
else:
    print('No changes detected.')
