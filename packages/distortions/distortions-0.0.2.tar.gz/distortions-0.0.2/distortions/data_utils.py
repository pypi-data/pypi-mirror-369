"""
Utility functions for downloading tutorial data files.
"""
import os
from pathlib import Path
import urllib.request
from urllib.error import URLError

# Base URL for data files on GitHub
GITHUB_DATA_BASE_URL = "https://raw.githubusercontent.com/krisrs1128/distortions/main/docs/tutorials/data/"

def download_tutorial_data(filename, data_dir="data", force_download=False):
    """
    Download tutorial data files from GitHub.
    
    Parameters
    ----------
    filename : str
        Name of the file to download
    data_dir : str, default "data"
        Local directory to save the file
    force_download : bool, default False
        Whether to re-download if file already exists
        
    Returns
    -------
    str
        Path to the downloaded file
    """
    # Create data directory if it doesn't exist
    data_path = Path(data_dir)
    data_path.mkdir(exist_ok=True)
    
    file_path = data_path / filename
    
    # Check if file already exists
    if file_path.exists() and not force_download:
        print(f"File {filename} already exists at {file_path}")
        return str(file_path)
    
    # Download from GitHub
    url = GITHUB_DATA_BASE_URL + filename
    print(f"Downloading {filename} from {url}...")
    
    try:
        urllib.request.urlretrieve(url, file_path)
        print(f"Successfully downloaded {filename} to {file_path}")
        return str(file_path)
    except URLError as e:
        raise RuntimeError(f"Failed to download {filename}: {e}")

def get_tutorial_data_path(filename, data_dir="data"):
    """
    Get path to tutorial data file, downloading if necessary.
    
    Parameters
    ----------
    filename : str
        Name of the data file
    data_dir : str, default "data"
        Local directory containing the file
        
    Returns
    -------
    str
        Path to the data file
    """
    return download_tutorial_data(filename, data_dir)
