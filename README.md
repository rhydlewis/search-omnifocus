# Search OmniFocus Alfred Workflow

## What is this?

This is a workflow for [Alfred 2](http://www.alfredapp.com/) that performs free text searches on [OmniFocus](http://www.omnigroup.com/omnifocus) data.

## Why would I want such a thing?

Well, I want it because I can't quickly search for, say, a task within OmniFocus using OmniFocus' search field. OmniFocus restricts search results to the current perspective or selection. [Other people have noticed this too](https://discourse.omnigroup.com/t/how-to-search-all-content-a-via-changed-perspective/366).

## How to install

[Download the `.workflow` file from the Releases page](https://github.com/rhydlewis/search-omnifocus/releases/).

## How to use

### Searching for tasks

Show Alfred then type:

    .s <query>

to search for tasks using <query> as the query string. For example, to search for tasks containing the word 'call', type:

    .s call

### Searching the inbox

Show Alfred then type:

    .i <query>

to search for tasks within the OmniFocus inbox. To show all tasks within the Inbox, type:

     .li

### Narrowing results

Show Alfred then type:

    .sa <query>

to search for *active* tasks only.

### Searching for projects

Show Alfred then type:

    .p <query>


