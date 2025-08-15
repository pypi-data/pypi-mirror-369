# RobotFrameworkResultsToSlackChannel

A utility to send Robot Framework test results directly to a Slack channel.

## Features

- Parses Robot Framework output files
- Formats test results for Slack
- Sends rsults as notifications to specified Slack channel.

## Requirements

- Python 3.7+
- [Robot Framework](https://robotframework.org/)
- [Slack Webhook URL](https://api.slack.com/messaging/webhooks)

## Installation

```bash
pip install robotframework-results-to-slack-channel
```

## Usage

1. Add the library to the test suite file

```bash
Library    RobotFrameworkResultsToSlackChannel    ${WEBHOOK_URL}    ...
```
2. Run the robot tests as usual 


## Configuration

- Set your Slack webhook URL in the command or via environment variable.

## License

MIT License

## Contributing

Pull requests are welcome! For major changes, please open an issue first.

## Contact

The Author of the code is Tim Lolkema (https://pypi.org/project/robotframework-notifications/) and modified by Lucas Greyhounds to add more details such as Environment and Footer custom text. All credits to the author. 
