# CPORT Installation Instructions

_The package is still under development and these instructions will change in the future._

CPORT is a Python package that can be used to predict the interface residues of a protein complex. It does so by interacting with various web services, either with simpler HTTP or via Selenium for JavaScript-based web services.

For Selenium to work the computer running CPORT needs to have **both** [Google Chrome](https://www.google.com/chrome/) and its [WebDriver](https://chromedriver.chromium.org/downloads) installed - `chromedriver` must be in the executable `PATH`.

Once those are in place;

```bash
git clone https://github.com/haddocking/cport.git
cd cport
python setup.py develop
cport
```
