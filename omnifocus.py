import applescript
import objc

INBOX = u'Inbox'
PROJECTS = u'Projects'
CONTEXTS = u'Contexts'
FORECAST = u'Forecast'
FLAGGED = u'Flagged'
REVIEW = u'Review'

PERSPECTIVE_SEARCH_SCRIPT = '''
        on search_for_perspectives()
            tell application "OmniFocus"
                try
                    return every perspective's name
                end try
            end tell
        end run
    '''


def list_perspectives():
    scpt = applescript.AppleScript(PERSPECTIVE_SEARCH_SCRIPT)
    results = scpt.call('search_for_perspectives')
    names = [INBOX, PROJECTS, CONTEXTS, FORECAST, FLAGGED, REVIEW]

    for result in results:
        if type(result) == objc.pyobjc_unicode:
            names.append(result)

    return names


def search_perspectives(query):
    results = []
    for perspective in list_perspectives():
        if query in perspective:
            results.append(perspective)
    return results
