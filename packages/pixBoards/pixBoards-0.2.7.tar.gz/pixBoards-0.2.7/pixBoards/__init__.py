import subprocess


def get_git_version():
    try:
        commit_hash = (
            subprocess.check_output(["git", "rev-parse", "--short", "HEAD"])
            .decode()
            .strip()
        )
        return commit_hash
    except Exception:
        return "untracked"


__version__ = get_git_version()


configTemplate = """
masterDir: "%USERPROFILE%/Desktop"
# csvList:
  # - fileLists/example.csv
  # - fileLists/misc.csv
  # - fileLists/onSsd.csv
  # - fileLists/pinterest.csv
imageLists:
  - imageLists/exampleImageLinks.txt
  - imageLists/bartolomeobari.txt
  - imageLists/loremPicsum.txt
  - imageLists/megumin.txt
  - imageLists/discordNsfwGuildRefs.txt
  - imageLists/filtered.txt
directories:
  - %USERPROFILE%/Pictures
margin: 20
col_count: 5
paginate: True
page_size: 50
padding: 3      # this is padding of the html page numbers, don't change unless you know what you're doing
tableName: image_cache
# remote_url:
gitUsername: boardsSites
"""