# Search OmniFocus Alfred Workflow

## What is this?

This is a workflow for [Alfred 2](http://www.alfredapp.com/) that performs free text searches on [OmniFocus](http://www.omnigroup.com/omnifocus) data.

## Why would I want such a thing?

Well, I want it because I can't quickly search for, say, a task within OmniFocus using OmniFocus' search field. OmniFocus restricts search results to the current perspective or selection. [Other people have noticed this too](https://discourse.omnigroup.com/t/how-to-search-all-content-a-via-changed-perspective/366).

## How to install

[Download the `.workflow` file from the Releases page](https://github.com/rhydlewis/search-omnifocus/releases/).

## How to use

### Searching for tasks

* Search for all tasks within OmniFocus (irrespective of status) with **.s**:

![](search-for-tasks.png)

### Searching the inbox

* Search the OmniFocus inbox with **.i**:

![](search-inbox.png)

### Searching for projects

* Search for projects with **.p**:

![](search-for-project.png)

### Searching for contexts

* Search just for a specific context with **.c**:

![](search-for-context.png)

or just list all contexts with **.lc**:

![](list-contexts.png)

### Narrowing results

* Search just for *active* tasks with **.sa**:

![](search-for-active-tasks.png)

or just for *active* projects with **.pa**:

![](search-for-active-projects.png)

## Thanks to...

* [Dean Jackson](https://github.com/deanishe): the [Python library for Alfred workflows](https://github.com/deanishe/alfred-workflow) does most of the heavy lifting. Excellent stuff, thank you.
* [Marko Kaestner](https://github.com/markokaestner): I used the [in-depth workflow](https://github.com/markokaestner/of-task-actions) to provide some insight into how to search Omnifocus.


