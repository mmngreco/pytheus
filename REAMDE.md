# Pytheus


## Installation

```bash
pipx install git+https://github.com/mmngreco/pytheus
```


## Usage

```bash
export PYTHEUS_API_URL="https://prometheus/api/v1"
pytheus --start "2024-02-04 00:05" --end "2024-03-05 00:00" --query "sum (rate(metrics{group='g1'}[60m]))" --cookie ./cookie --silent
```
