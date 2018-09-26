import subprocess

INBOX = 'Inbox'
PROJECTS = 'Projects'
CONTEXTS = 'Contexts'
TAGS = 'Tags'
FORECAST = 'Forecast'
FLAGGED = 'Flagged'
REVIEW = 'Review'

DEFAULT_OF_VERSION = '2'

DEFAULT_OF2_PERSPECTIVES = [INBOX, PROJECTS, CONTEXTS, FORECAST, FLAGGED, REVIEW]
DEFAULT_OF3_PERSPECTIVES = [INBOX, PROJECTS, TAGS, FORECAST, FLAGGED, REVIEW]

PERSPECTIVE_SEARCH_SCRIPT = '''
        tell application "OmniFocus"
            try
                return every perspective's name
            end try
        end tell
    '''
LOCATION_SCRIPT = 'tell application "Finder" to get (POSIX path of (path to application "OmniFocus"))'


def list_perspectives(version):
    results = run_script(PERSPECTIVE_SEARCH_SCRIPT)
    results = [result.rstrip("\n").decode('utf-8', 'ignore') for result in results if result != "missing value"]

    if version == DEFAULT_OF_VERSION:
        names = DEFAULT_OF2_PERSPECTIVES + results
    else:
        names = DEFAULT_OF3_PERSPECTIVES + results

    return names


def search_perspectives(query, version):
    return [perspective for perspective in list_perspectives(version) if query.lower() in perspective.lower()]


# see suggestion from deanishe at:
# http://www.alfredforum.com/topic/5934-search-omnifocus-free-text-search-your-omnifocus-data
def find_install_location():
    results = run_script(LOCATION_SCRIPT)
    return results[0].rstrip("\n")


def run_script(query):
    # thanks Dr Drang: http://www.leancrew.com/all-this/2013/03/combining-python-and-applescript/
    osa = subprocess.Popen(['osascript', '-'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    return osa.communicate(query)[0].split(', ')
