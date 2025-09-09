# xscrp

Searching for X posts. This is a wrapper script  for  [twscrape](https://github.com/vladkens/twscrape) that searches a  time span one day at a time.

## Usage

- Make a dedicated environment: `conda create -n xscrp python=3.10 -y && conda activate xscrp`
- Check Python version: `python --version` (must be 3.10+)
- Clone this repository: `git clone <repository-url>`
- Install dependencies: `pip install -r requirements.txt`
- Setup account (one time): `python setup_account.py`
- Run search: `python xscrp.py`


## Search Query Format

Follows X [advanced search syntax](https://github.com/igorbrigadir/twitter-advanced-search).

## Cookie instructions (Firefox)

1. Log into X in Firefox
2. Open *Web Developer Tools* → *Storage* → **Cookies** → **x.com**
3. Copy `auth_token` and `ct0` values
4. Format as this example string: `auth_token=a1b2c3d4e5; ct0=xyz789abc123def`