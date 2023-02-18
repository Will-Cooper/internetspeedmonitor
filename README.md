# Internet Speed Monitor
A script to query the speedtest service at set intervals
and plot these to a live updating step graph in your browser.

## Installation
### Downloading:
```bash
git clone git@github.com:Will-Cooper/internetspeedmonitor.git
cd internetspeedmonitor/
```
To keep updated:
```bash
git pull
```
### Set-up:
#### Conda
The best way of setting up a clean environment with this
package is to use `conda`.
```bash
conda env create -f environment.yml
conda activate internet
conda deactivate # to leave environment
```
#### Venv (pip)
Alternatively, to create a `pip` environment:
```bash
# if venv isn't installed:
python3 -m pip install --user virtualenv
# then / otherwise
python3 -m venv env  # creates directory called 'env'
source env/bin/activate
python3 -m pip install -r requirements.txt
deactivate  # to leave
```
## Usage
Call the following command to create a plot which 
will automatically update in your browser.
```
bokeh serve --show internetcheck.py
```
It should appear in a new tab on your browser with the
url something like `localhost:5006/internetcheck`.
