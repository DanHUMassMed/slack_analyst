# Steps to create EndNote 21 Bib Import file

### On Slack
1. Invite `Slack_Analyst` to the Channel you want to get papers from
2. Execute /collect_paper_urls in the Channel you want to get papers from

This will populate the Slack Analysts with a list of URLs

### On Laptop (Mac or PC)
1. Create a Download Directory for the pdfs on your local machine 
    * for Example `mkdir -p /Users/dan/Downloads/papers_mito`
    * If using Chrome set the download directory to above location
        * `chrome://settings/downloads`
2. Goto URL below providing the channel name as the last part of url
    * For Example with `papers_mito` channel the URL is:
    * https://slackbot1.danhiggins.org/urls-to-process/papers_mito
3. Download each paper and capture the name of the file
    * Update the webpage with the download file name
        * _NOTE:_ The saved file name can be changed as desired 
4. In EndNote Export all references using Output Style "Show All Fields"
    * Select _All References_ on Left Tab
    * <ctrl> a (Select all)
    * On menu Select _File_ -> __Export__
    * On Popup "Export File Name"
        * __Save As:__           "My_EndNote_Library.txt"
        * __Where:__             Downloads
        * __Save File as Type:__ Text Only
        * __Output Style:__      Show All Fields
        * __Export selected References:__ Checked
        * __Save__
5. Copy `My_EndNote_Library.txt` to Waston
    * FileZilla `/media/data1/Code/Python/Slack/slack_analyst/notebooks`




### On Watson
1. Create a directory to server pdf files
    * `mkdir -p /var/www/danhiggins.org/data/papers_mito`
2. Copy papers from local Laptop to Watson
    * `cd /Users/dan/Downloads/papers_mito`
    * `scp *.pdf 192.168.1.101:/var/www/danhiggins.org/data/papers_mito/`
3. Run Jupyter Notebook `make_endnote.ipynb`
    * `cd /home/dan/Code/Python/Slack/slack_analyst/notebooks`
    * In the notebook set the directory(s) to process
        * `directory_paths = ['/var/www/danhiggins.org/data/papers_mito/']`
        * Start grobid server to get references
            * `cd Code/Java/grobid`
            * `./gradlew run`
