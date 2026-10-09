import os
import uuid
from pathlib import Path

from app.core.config import settings


UPLOAD_DIR = Path(__file__).parent.parent.parent / "public" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

# Magic bytes (file signatures) for validation
MAGIC_SIGNATURES = {
    b'\xFF\xD8\xFF': {
        'ext': '.jpg',
        'mime': 'image/jpeg',
        'description': 'JPEG'
    },
    b'\x89PNG': {
        'ext': '.png',
        'mime': 'image/png',
        'description': 'PNG'
    },
    b'GIF8': {
        'ext': '.gif',
        'mime': 'image/gif',
        'description': 'GIF'
    },
    b'RIFF': {
        'ext': '.webp',
        'mime': 'image/webp',
        'description': 'WebP (RIFF-based)',
        'extended_check': True  # Needs additional verification
    }
}


def _get_file_signature(content: bytes) -> bytes:
    """Extract file signature (magic bytes) from content."""
    if len(content) < 4:
        return content[:len(content)]
    return content[:4]


def _is_webp(content: bytes) -> bool:
    """Verify WebP format (RIFF....WEBP signature)."""
    if len(content) < 12:
        return False

    # RIFF at offset 0
    if content[0:4] != b'RIFF':
        return False

    # WEBP at offset 8
    if content[8:12] != b'WEBP':
        return False

    return True


def validate_file_magic_bytes(file_content: bytes, filename: str) -> bool:
    """
    Validate that file content matches the declared extension.

    Checks magic bytes (file signature) to detect:
    - File with .jpg extension but PNG content
    - Executables or scripts renamed with image extension
    - Truncated or corrupted files

    Returns True if valid, raises ValueError if invalid.
    """
    if len(file_content) == 0:
        raise ValueError("File is empty")

    ext = Path(filename).suffix.lower()
    signature = _get_file_signature(file_content)

    # Check JPEG
    if ext == '.jpg' or ext == '.jpeg':
        if signature.startswith(b'\xFF\xD8\xFF'):
            return True
        raise ValueError(f"File has .jpg extension but content appears to be {signature[:4]} (not JPEG)")

    # Check PNG
    if ext == '.png':
        if signature == b'\x89PNG':
            return True
        raise ValueError(f"File has .png extension but content appears to be {signature[:4]} (not PNG)")

    # Check GIF
    if ext == '.gif':
        if signature.startswith(b'GIF8'):
            return True
        raise ValueError(f"File has .gif extension but content appears to be {signature[:4]} (not GIF)")

    # Check WebP
    if ext == '.webp':
        if _is_webp(file_content):
            return True
        raise ValueError(f"File has .webp extension but content does not match WebP format (signature: {signature[:4]})")

    raise ValueError(f"Unknown file extension: {ext}")


def is_allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    ext = Path(filename).suffix.lower()
    return ext in ALLOWED_EXTENSIONS


def save_upload(file_content: bytes, original_filename: str) -> str:
    """
    Save uploaded file to disk.
    Returns the filename (not full path).

    Validates:
    1. File extension is in whitelist
    2. File size is within limit
    3. File magic bytes match declared extension
    """
    if not is_allowed_file(original_filename):
        raise ValueError(f"File type not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")

    if len(file_content) > MAX_FILE_SIZE:
        raise ValueError(f"File size exceeds maximum of {MAX_FILE_SIZE / 1024 / 1024:.0f}MB")

    # Validate magic bytes match extension
    validate_file_magic_bytes(file_content, original_filename)

    ext = Path(original_filename).suffix.lower()
    filename = f"{uuid.uuid4()}{ext}"
    file_path = UPLOAD_DIR / filename

    file_path.write_bytes(file_content)

    return filename


def generate_public_url(filename: str) -> str:
    """Generate public HTTPS URL for uploaded file."""
    return f"{settings.PUBLIC_BASE_URL}/public/uploads/{filename}"


def delete_file(filename: str) -> None:
    """Delete file from storage."""
    file_path = UPLOAD_DIR / filename
    if file_path.exists():
        file_path.unlink()
