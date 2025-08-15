import time

from huggingface_hub import hf_hub_download
from huggingface_hub.utils import HfHubHTTPError, RepositoryNotFoundError


def download_model_weights(
    repo_id: str,
    filename: str,
    force_download: bool = False,
    max_retries: int = 3,
) -> str:
    """
    Download model weights from HuggingFace Hub.

    Parameters
    ----------
    repo_id : str
        Repository ID on HuggingFace Hub
    filename : str
        Name of the model file to download
    force_download : bool, optional
        Force re-download even if cached, by default False
    max_retries : int, optional
        Maximum number of retry attempts on failure, by default 3

    Returns
    -------
    str : Path to the downloaded model directory
    """
    delay = 1.0

    for attempt in range(max_retries):
        try:
            return hf_hub_download(
                repo_id=repo_id,
                filename=filename,
                force_download=force_download,
            )

        except (HfHubHTTPError, ConnectionError, TimeoutError):
            if attempt == max_retries - 1:
                raise

            print(
                f"Download failed (attempt {attempt + 1}), retrying in {delay:.1f}s..."
            )
            time.sleep(delay)
            delay *= 2

        except RepositoryNotFoundError:
            print(f"Repository not found: {repo_id}")
            raise
