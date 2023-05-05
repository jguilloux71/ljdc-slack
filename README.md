# ljdc-slack
Tool to get and send the last post from "Les joies du code" to a Slack channel

# Requirements

Install these following packages:
```
pip3 install requests
pip3 install coverage
pip3 install bs4
pip3 install slack_sdk
pip3 install aiohttp
pip3 install requests_mock
```

Deactivate the official 'slack' module in your Python modules directory:
```
mv ~/.local/lib/python3.9/site-packages/slack ~/.local/lib/python3.9/site-packages/_slack
```

# Unit tests and coverage
- Run basically: `./test/coverage.sh`
- Results are stored in the directory: `htmlcov`

# Run
- Define the env var `SLACK_BOT_TOKEN`: Token generated from your Slack instance
- Define the env var `SLACK_CHANNEL`: Name of Slack channel where articles will be sent
- Run: `src/main.py`
