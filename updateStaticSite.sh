#!/usr/bin/bash
# =========================================================================== #
PYTHON_EXE="C:/Python37/python.exe"
PELICAN_EXE="C:/Python37/Scripts/pelican.exe"
CHROME_EXE="C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"
BLOG_DIR="G:/Repos/Blog"
# =========================================================================== #
pushd "${BLOG_DIR}" > /dev/null

"${PELICAN_EXE}" content/ -s pelicanconf.py -o output/ --delete-output-directory --ignore-cache --verbose
wait

if [ -d "output/" ]; then
    echo "output directory successfully created."
    echo "Copying CNAME to generated output directory."
    cp CNAME "./output"
else
    echo "output directory not created. Exiting."
    exit 1
fi

# Launch index.html with Chrome ===============================================]
while test $# -gt 0
do
    if [[ "$1" == "--serve" ]]; then
        pushd "output" > /dev/null

        # Determine whether python server process is currently running.
        SERVER_PID="$(ps -ef | grep "python$" | awk '{ print $2 }')"
        if [ "${#SERVER_PID}" -gt 0 ]; then 
            echo "Killing process ${SERVER_PID}."
            kill -9 "${SERVER_PID}"
			wait
        fi

        echo "Serving static site locally at 127.0.0.1:9999."
        "${PYTHON_EXE}" -m http.server 9999 --bind "127.0.0.1" &
    fi
    if [[ "$1" == "--render" ]]; then
        pushd "output" > /dev/null
        "${CHROME_EXE}" index.html
    fi
    if [[ "$1" == "--github" ]]; then
        echo "Not yet implemented."
    fi
    
    shift
done
