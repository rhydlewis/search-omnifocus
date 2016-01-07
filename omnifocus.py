import subprocess

INBOX = 'Inbox'
PROJECTS = 'Projects'
CONTEXTS = 'Contexts'
FORECAST = 'Forecast'
FLAGGED = 'Flagged'
REVIEW = 'Review'

DEFAULT_PERSPECTIVES = [INBOX, PROJECTS, CONTEXTS, FORECAST, FLAGGED, REVIEW]

PERSPECTIVE_SEARCH_SCRIPT = '''
        tell application "OmniFocus"
            try
                return every perspective's name
            end try
        end tell
    '''


def list_perspectives():
    # thanks Dr Drang: http://www.leancrew.com/all-this/2013/03/combining-python-and-applescript/
    osa = subprocess.Popen(['osascript', '-'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    results = osa.communicate(PERSPECTIVE_SEARCH_SCRIPT)[0].split(', ')
    results = [result.rstrip("\n").decode('utf-8', 'ignore') for result in results
               if result != "missing value"]
    names = DEFAULT_PERSPECTIVES + results
    return names


def search_perspectives(query):
    return [perspective for perspective in list_perspectives()
            if query.lower() in perspective.lower()]
