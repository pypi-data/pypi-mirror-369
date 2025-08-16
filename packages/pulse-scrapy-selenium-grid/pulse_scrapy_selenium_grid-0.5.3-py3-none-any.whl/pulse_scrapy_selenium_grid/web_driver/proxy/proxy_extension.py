import logging
import tempfile
import zipfile
from pathlib import Path
from string import Template

logger = logging.getLogger(__name__)


def generate_proxy_extension(host: str, port: int, username: str, password: str) -> str:
    logger.info(f"Generating proxy extension for {host}:{port} (user {username})")

    current_dir = Path(__file__).parent
    manifest_json: str = (current_dir / "resources" / "manifest.json").read_text(encoding="utf-8")
    background_js_template: str = (current_dir / "resources" / "background.js").read_text(encoding="utf-8")

    background_js = Template(background_js_template).safe_substitute(
        PROXY_HOST=host, PROXY_PORT=port, PROXY_USERNAME=username, PROXY_PASSWORD=password
    )

    temp_file = tempfile.NamedTemporaryFile(suffix=".zip", delete=False)
    with zipfile.ZipFile(temp_file, mode="w", compression=zipfile.ZIP_DEFLATED) as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)
    temp_file.close()
    return temp_file.name


def cleanup_temp_extension_file(file_path: str) -> None:
    """
    Deletes the temporary file if it exists.
    :param file_path: Extension file path
    """
    try:
        if file_path and Path(file_path).exists():
            Path(file_path).unlink()
            logger.info(f"Deleted temporary file {file_path}")
    except Exception as e:
        logger.warning(f"Could not delete temporary file {file_path}: {e}")
