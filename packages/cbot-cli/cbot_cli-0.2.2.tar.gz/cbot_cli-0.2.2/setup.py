from setuptools import setup, find_packages

setup(
    name="cbot-cli",
    version="0.2.2",
    packages=find_packages(),
    install_requires=[
        "requests",
        "pyperclip",
        "openai",
        "python-dotenv"
    ],
    entry_points={
        "console_scripts": [
            "cbot = cbot.__main__:main",
        ],
    },
)
