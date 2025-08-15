import os
import time
import json
import uuid
import tempfile
import pathlib
import requests
from datetime import datetime, timedelta, timezone

import zarr

from .views import TimeseriesGraph

thisdir = pathlib.Path(__file__).parent.resolve()

FIGPACK_API_BASE_URL = "https://figpack-api.vercel.app"
TEMPORY_BASE_URL = "https://tempory.net/figpack/figures"


def _upload_view(view: TimeseriesGraph) -> str:
    """
    Upload a figpack view to the cloud

    Args:
        view: The figpack view to upload

    Returns:
        str: URL where the uploaded figure can be viewed

    Raises:
        EnvironmentError: If FIGPACK_UPLOAD_PASSCODE is not set
        Exception: If upload fails
    """
    # Check for required environment variable
    passcode = os.environ.get("FIGPACK_UPLOAD_PASSCODE")
    if not passcode:
        raise EnvironmentError(
            "FIGPACK_UPLOAD_PASSCODE environment variable must be set"
        )

    # Generate random figure ID
    figure_id = str(uuid.uuid4())
    print(f"Generated figure ID: {figure_id}")

    with tempfile.TemporaryDirectory(prefix="figpack_upload_") as tmpdir:
        # Prepare the figure bundle (reuse logic from _show_view)
        print("Preparing figure bundle...")
        _prepare_figure_bundle(view, tmpdir)

        # Upload the bundle
        print("Starting upload...")
        _upload_bundle(tmpdir, figure_id, passcode)

        # Return the final URL
        figure_url = f"{TEMPORY_BASE_URL}/{figure_id}/index.html"
        print(f"Upload completed successfully!")
        print(f"Figure available at: {figure_url}")
        return figure_url


def _prepare_figure_bundle(view: TimeseriesGraph, tmpdir: str) -> None:
    """
    Prepare the figure bundle in the temporary directory
    This reuses the same logic as _show_view
    """
    html_dir = thisdir / "figpack-gui-dist"
    if not os.path.exists(html_dir):
        raise SystemExit(f"Error: directory not found: {html_dir}")

    # Copy all files in html_dir recursively to tmpdir
    for item in html_dir.iterdir():
        if item.is_file():
            target = pathlib.Path(tmpdir) / item.name
            target.write_bytes(item.read_bytes())
        elif item.is_dir():
            target = pathlib.Path(tmpdir) / item.name
            target.mkdir(exist_ok=True)
            for subitem in item.iterdir():
                target_sub = target / subitem.name
                target_sub.write_bytes(subitem.read_bytes())

    # Write the graph data to the Zarr group
    zarr_group = zarr.open_group(
        pathlib.Path(tmpdir) / "data.zarr",
        mode="w",
        synchronizer=zarr.ThreadSynchronizer(),
    )
    view._write_to_zarr_group(zarr_group)
    zarr.consolidate_metadata(zarr_group.store)


def _upload_bundle(tmpdir: str, figure_id: str, passcode: str) -> None:
    """
    Upload the prepared bundle to the cloud
    """
    tmpdir_path = pathlib.Path(tmpdir)

    # First, upload initial figpack.json with "uploading" status
    print("Uploading initial status...")
    figpack_json = {
        "status": "uploading",
        "upload_started": datetime.now(timezone.utc).isoformat(),
        "upload_updated": datetime.now(timezone.utc).isoformat(),
        "figure_id": figure_id,
    }
    _upload_small_file(
        figure_id, "figpack.json", json.dumps(figpack_json, indent=2), passcode
    )

    # Collect all files to upload
    all_files = []
    for file_path in tmpdir_path.rglob("*"):
        if file_path.is_file():
            relative_path = file_path.relative_to(tmpdir_path)
            all_files.append((str(relative_path), file_path))

    print(f"Found {len(all_files)} files to upload")

    # Upload files
    uploaded_count = 0
    timer = time.time()
    for relative_path, file_path in all_files:
        # Skip the figpack.json since we already uploaded the initial version
        if relative_path == "figpack.json":
            continue
        file_type = _determine_file_type(relative_path)

        if file_type == "small":
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            _upload_small_file(figure_id, relative_path, content, passcode)
        else:  # large file
            _upload_large_file(figure_id, relative_path, file_path, passcode)

        uploaded_count += 1
        print(f"Uploaded {uploaded_count}/{len(all_files)-1}: {relative_path}")
        elapsed_time = time.time() - timer
        if elapsed_time > 60:
            figpack_json = {
                **figpack_json,
                "status": "uploading",
                "upload_progress": f"{uploaded_count}/{len(all_files)-1}",
                "upload_updated": datetime.now(timezone.utc).isoformat(),
            }
            _upload_small_file(
                figure_id,
                "figpack.json",
                json.dumps(figpack_json, indent=2),
                passcode,
            )
            print(
                f"Updated figpack.json with progress: {uploaded_count}/{len(all_files)-1}"
            )
            timer = time.time()

    # Finally, upload completion status
    print("Uploading completion status...")
    figpack_json = {
        **figpack_json,
        "status": "completed",
        "upload_completed": datetime.now(timezone.utc).isoformat(),
        "expiration": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
        "figure_id": figure_id,
        "total_files": len(all_files),
    }
    _upload_small_file(
        figure_id, "figpack.json", json.dumps(figpack_json, indent=2), passcode
    )


def _determine_file_type(file_path: str) -> str:
    """
    Determine if a file should be uploaded as small or large
    Based on the validation logic in the API
    """
    # Check exact matches first
    if file_path == "figpack.json" or file_path == "index.html":
        return "small"

    # Check zarr metadata files
    if (
        file_path.endswith(".zattrs")
        or file_path.endswith(".zgroup")
        or file_path.endswith(".zarray")
        or file_path.endswith(".zmetadata")
    ):
        return "small"

    # Check HTML files
    if file_path.endswith(".html"):
        return "small"

    # Check data.zarr directory
    if file_path.startswith("data.zarr/"):
        file_name = file_path[len("data.zarr/") :]
        # Check if it's a zarr chunk (numeric like 0.0.1)
        if _is_zarr_chunk(file_name):
            return "large"
        # Check for zarr metadata files in subdirectories
        if (
            file_name.endswith(".zattrs")
            or file_name.endswith(".zgroup")
            or file_name.endswith(".zarray")
            or file_name.endswith(".zmetadata")
        ):
            return "small"

    # Check assets directory
    if file_path.startswith("assets/"):
        file_name = file_path[len("assets/") :]
        if file_name.endswith(".js") or file_name.endswith(".css"):
            return "large"

    # Default to large file
    return "large"


def _is_zarr_chunk(file_name: str) -> bool:
    """
    Check if filename consists only of numbers and dots (zarr chunk pattern)
    """
    for char in file_name:
        if char != "." and not char.isdigit():
            return False
    return (
        len(file_name) > 0
        and not file_name.startswith(".")
        and not file_name.endswith(".")
    )


def _upload_small_file(
    figure_id: str, file_path: str, content: str, passcode: str
) -> None:
    """
    Upload a small file by sending content directly
    """
    destination_url = f"{TEMPORY_BASE_URL}/{figure_id}/{file_path}"

    try:
        content.encode("utf-8")
    except Exception as e:
        raise Exception(f"Content for {file_path} is not UTF-8 encodable: {e}")
    payload = {
        "destinationUrl": destination_url,
        "passcode": passcode,
        "content": content,
    }
    # check that payload is json serializable
    try:
        json.dumps(payload)
    except Exception as e:
        raise Exception(f"Payload for {file_path} is not JSON serializable: {e}")

    response = requests.post(f"{FIGPACK_API_BASE_URL}/api/upload", json=payload)

    if not response.ok:
        try:
            error_data = response.json()
            error_msg = error_data.get("message", "Unknown error")
        except:
            error_msg = f"HTTP {response.status_code}"
        raise Exception(f"Failed to upload {file_path}: {error_msg}")


def _upload_large_file(
    figure_id: str, file_path: str, local_file_path: pathlib.Path, passcode: str
) -> None:
    """
    Upload a large file using signed URL
    """
    destination_url = f"{TEMPORY_BASE_URL}/{figure_id}/{file_path}"
    file_size = local_file_path.stat().st_size

    # Get signed URL
    payload = {
        "destinationUrl": destination_url,
        "passcode": passcode,
        "size": file_size,
    }

    response = requests.post(f"{FIGPACK_API_BASE_URL}/api/upload", json=payload)

    if not response.ok:
        try:
            error_data = response.json()
            error_msg = error_data.get("message", "Unknown error")
        except:
            error_msg = f"HTTP {response.status_code}"
        raise Exception(f"Failed to get signed URL for {file_path}: {error_msg}")

    response_data = response.json()
    if not response_data.get("success"):
        raise Exception(
            f"Failed to get signed URL for {file_path}: {response_data.get('message', 'Unknown error')}"
        )

    signed_url = response_data.get("signedUrl")
    if not signed_url:
        raise Exception(f"No signed URL returned for {file_path}")

    # Upload file to signed URL
    content_type = _determine_content_type(file_path)
    with open(local_file_path, "rb") as f:
        upload_response = requests.put(
            signed_url, data=f, headers={"Content-Type": content_type}
        )

    if not upload_response.ok:
        raise Exception(
            f"Failed to upload {file_path} to signed URL: HTTP {upload_response.status_code}"
        )


def _determine_content_type(file_path: str) -> str:
    """
    Determine content type for upload based on file extension
    """
    file_name = file_path.split("/")[-1]
    extension = file_name.split(".")[-1] if "." in file_name else ""

    content_type_map = {
        "json": "application/json",
        "html": "text/html",
        "css": "text/css",
        "js": "application/javascript",
        "png": "image/png",
        "zattrs": "application/json",
        "zgroup": "application/json",
        "zarray": "application/json",
        "zmetadata": "application/json",
    }

    return content_type_map.get(extension, "application/octet-stream")
