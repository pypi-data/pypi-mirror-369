from setuptools import setup

setup(
    name="grabby-cli",
    version="1.0.0",
    py_modules=["grabby"],
    install_requires=[
        "yt-dlp",
        "browser-cookie3"
    ],
    entry_points={
        "console_scripts": [
            "grabby=grabby:main"
        ]
    },
    author="Ranveer",
    description="A YouTube video/audio downloader with exact titles using yt-dlp.",
    url="https://github.com/ranveerkavale/grabby",
    python_requires='>=3.7',
)
