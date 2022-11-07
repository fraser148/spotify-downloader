# Spotify Playlist Downloader

Currently under development. Please work on issues.

## Install

1. Download this repository
2. Create a virtual environment:

    ```bash
    python -m venv env
    env\Scripts\activate
    ```

3. Install requirements via pip

    ```bash
    python -m pip install -r requirements.txt
    ```

4. You must also install FFmpeg to convert the audio files to .mp3 files.
   1. A  good tutorial for this is the [wikihow tutorial](https://www.wikihow.com/Install-FFmpeg-on-Windows).
   2. This tutorial requires you to uncompress a `.7z` file so I downloaded [7-zip](https://www.7-zip.org/) which worked fine.

## Contributors

Select an issue and submit a pull request from your branchfor review.

When adding new packages, make sure to add them to the `requirements.txt` file via the command:

```bash
py -m pip freeze > requirements.txt
```
