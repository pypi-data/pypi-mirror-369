import pathlib
from setuptools import setup

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

setup(
    name="robotframework-results-to-slack-channel",
    version="1.0.1",
    description="Send Robot Framework Results Notifications to specific Slack channel. Forked from tlolkema/RobotNotifications and all credits from the creator tlolkema. Added some details to fit for the organisation by Lucas Greyhounds.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/lucasgreyhounds/robotframework-results-to-slack-channel",
    author="Lucas Greyhounds",
    author_email="lucasgreyhounds@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    packages=["RobotFrameworkResultsToSlackChannel"],
    include_package_data=True,
    install_requires=["requests"],
)