Title: A Python PDF Harvester in 25 LOC                              
Date: 2023-04-23               
Category: Python                        
Tags: Python                      
Authors: James D. Triveri                                    
Summary: A simple, effective PDF harvester in Python          


The goal of this post is to develop a utility that handles the following:

1. Retrieve HTML from the target webpage.    
2. Parse the HTML, extracting all URL references to embedded PDF links.    
3. For each embedded PDF link, download the document and save it locally.    

Plenty of 3rd-party libraries can query and retrieve a webpage’s links in a 
single call. However, the purpose of this post is to highlight the fact that by 
combining elements of the Python Standard Library with the Requests package, we
can create own own, and learn something while we're at it. 

### Step I: Acquire HTML

Before we begin, it's important to mention that if you're attempting to follow 
along on a computer situated behind a firewall or corporate proxy, you’ll need 
to provide the necessary proxy server details as part of the `requests.get` 
call. For example, assume an individual with username "user33" and password 
"Password33" has their web traffic routed through "corporate.proxy.com" via 
port 8080. "user33" would first need to specify their authentication details 
in a dictionary, then pass the dictionary to `requests.get`'s optional proxies 
argument:

```python
"""
NOTE: This step is for individuals working behind a firewall
or corporate proxy. If this does not apply, skip this section.
"""
import requests

# Creating proxies dict to submit along with requests.get.
proxies = {
    'http': 'http://user33:Password33@corporate.proxy.com:8080',
    'https': 'https://user33:Password33@corporate.proxy.com:8080',
    }

# Arbitrary URL from which to harvest PDFs.
URL = "https://en.wikipedia.org/wiki/Conjugate_prior"

# Simplified version of requests.get call for illustration only.
requests.get(URL, proxies=proxies)
```

Note that the `proxies` argument would be required for each subsequent 
invocation of `requests.get`.
For the remainder of the post, I'll assume we are not working behind a proxy, 
and will present all code examples without including the `proxies` argument.

The library that facilitates communication between Python and the target 
webpage is Requests. Retrieving a webpage's HTML is as straightforward as:

```python
import requests
requests.get(<URL>).text   
```

Where `URL` is a string representing the target URL. `requests.get` returns an 
object, and by specifying the `.text` attribute, we're requesting that the 
page content be returned as plain text to allow for parsing with regular 
expressions in the next step.

What follows is the logic comprising step I:

```python
"""
PDF Harvester I of III: Retrieve HTML as plain text.
"""
import requests

URL = "https://en.wikipedia.org/wiki/Conjugate_prior"

# instruct requests object to return HTML as plain text.
html = requests.get(URL).text
```

The HTML has been obtained. Next it will be necessary to identify and extract 
references to all embedded PDF links.


### Step II: Extract PDF URLs from HTML


A cursory review of the HTML from webpages with embedded PDF links revealed the 
following:

- Valid PDF URLs will in almost always be embedded within an `href` tag.    
- Valid PDF URLs will in all cases be preceded by `http` or `https`.      
- Valid PDF URLs will in all cases be enclosed by a trailing `>`.   
- Valid PDF URLs cannot contain whitespace.        

After some trial and error, the following regular expression was found to have 
acceptable performance for our test cases:

```
"(?=href=).*(https?://\S+.pdf).*?>"
```

An excellent site to practice building and testing regular expressions is 
[Pythex](https://pythex.org/) . The app allows you to construct regular 
expressions and determine how they match against the target text. I find myself 
using it on a regular basis. Highly recommended!  

Here is the logic associated with steps I and II:

```python
"""
PDF Harvester II of III: Extract PDF URL's from HTML.
"""
import requests
import re

# Specify URL for webpage of interest.
URL  = "https://en.wikipedia.org/wiki/Conjugate_prior"
html = requests.get(URL).text

# Search html and compile PDF URLs in a list.
pdf_urls = re.findall(r"(?=href=).*(https?://\S+.pdf).*?>", html)
```


Note that the regular expression is preceded with an `r` when passed to 
`re.findall`. This instructs the Python virtual machine to interpret what 
follows as a raw string and to ignore escape sequences`.

`re.findall` returns a list of matches extracted from the source text. In our 
case, it returns a list of URLs referencing our target PDF documents.

For our last step we need to retrieve the documents associated with our 
collection of links and write them to file locally. We introduce another module 
from the Python Standard Library, `os.path`, which facilitates the partitioning 
of absolute filepaths into components in order to retain filenames when saving 
documents to disk.

For example, consider the following well-formed URL:

```
"http://Statistical_Modeling/Fall_2017/Lectures/Lecture11.pdf"
```

To capture *Lecture11.pdf*, we pass the absolute URL to `os.path.split`, which 
returns a tuple of everything preceding the filename as the first element, 
along with the filename and extension as the second element:

```python
In [1]: import os.path
In [2]: url = "http://Statistical_Modeling/Fall_2017/Lectures/Lecture11.pdf"
In [3]: os.path.split(url)
Out[1]:('http://Statistical_Modeling/Fall_2017/Lectures', 'Lecture11.pdf')
```

This will be used to preserve the filename of the documents we save locally.


### Step III: Write PDFs to File


This step differs from the initial HTML retrieval in that we need to request 
the content as bytes, not text. By calling `requests.get(url).content`, we're 
accessing the raw bytes that comprise the PDF, then writing those bytes to file. 
Here's the logic for the third and final step:

```python
"""
PDF Harvester III of III: Write PDF(s) to file.
"""
import os
import os.path
import re
import requests

URL = "https://en.wikipedia.org/wiki/Conjugate_prior"
html = requests.get(URL).text
pdf_urls = re.findall(r"(?=href=).*(https?://\S+.pdf).*?>", html)

# Set working directory to desired location.
os.chdir("C:\\user33\\")

# Request PDF content and write to file for all entries.
for pdf in pdf_urls:

    # Get filename from url for naming file locally.
    pdfname = os.path.split(pdf)[1].strip()

    # Get retrieved html as bytes.
    r = requests.get(pdf).content

    try:
        with open(pdfname, "wb") as f: f.write(r)
    except:
        print("Unable to download {}.".format(pdfname))
        
print("\nProcessing complete!")
```


Notice that we surround `with open(pdfname, "wb")...` in a try-except block: 
This handles situations that would prevent our code from downloading a 
document, such as broken redirects or invalid links.

All-in we end up with 24 lines, including comments and imports.
We next present the full implementation of the PDF Harvester after a little 
reorganization:

```python
"""
PDF Harvester.
"""
import datetime
import os
import os.path
import re
import requests


def pdf_harvester(url, loc=None, proxies=None):
    """
    Retrieve URLs html and extract references to PDFs. Download PDFs, 
    writting to `loc`. If `loc` is None, save to current working 
    directory.
    """
    pdfdir = os.getcwd() if loc is None else loc
    html = requests.get(url, proxies=proxies).text
    pdf_urls = re.findall(r"(?=href=).*(https?://\S+.pdf).*?>", html)

    for pdf_url in pdf_urls:
        timestamp_ = datetime.datetime.now().strftime("%c")
        print("[{}] Retrieving {}".format(timestamp_, pdf_url))
        pdfname = os.path.split(pdf)[1]
        pdfpath = os.path.join(pdfdir, pdfname)
        req = requests.get(pdf).content
        try:
            with open(pdfname, "wb") as f: f.write(req)   
        except:
            print("Unable to download {}.".format(pdfname))

    print("\nProcessing complete!")




# example calling `pdf_harvester` =>
>>> URL = "https://en.wikipedia.org/wiki/Poisson_point_process"
>>> pdf_harvester(URL, proxies, loc="C:\\user33\\")
Processing complete!
```


