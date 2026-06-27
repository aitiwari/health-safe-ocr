import argparse
import json
from dataclasses import asdict

from .engines import get_easyocr_status
from .extractor import HealthSafeOCR, OcrEngineUnavailableError
from .tesseract import TesseractUnavailableError, get_tesseract_status


def print_doctor() -> int:
    tesseract_status = get_tesseract_status()
    easyocr_status = get_easyocr_status()
    print("health-safe-ocr doctor")
    print()
    print("Python package: OK")
    if tesseract_status.available:
        print("Tesseract binary: OK")
        print(f"Command: {tesseract_status.command}")
        print(f"Version: {tesseract_status.version}")
    else:
        print("Tesseract binary: NOT FOUND")
        print()
        print(tesseract_status.message)

    print()
    if easyocr_status.available:
        print("EasyOCR backend: OK")
    else:
        print("EasyOCR backend: NOT INSTALLED")
        print()
        print(easyocr_status.message)

    return 0 if tesseract_status.available or easyocr_status.available else 1


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Safe OCR for healthcare images",
    )
    parser.add_argument("image_path", nargs="?")
    parser.add_argument("--mask-pii", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--engine",
        choices=["auto", "tesseract", "easyocr"],
        default="auto",
        help="OCR engine to use; auto tries Tesseract first, then EasyOCR",
    )
    parser.add_argument(
        "--doctor",
        action="store_true",
        help="check whether system OCR dependencies are installed",
    )
    args = parser.parse_args()

    if args.doctor or args.image_path == "doctor":
        raise SystemExit(print_doctor())

    if args.image_path is None:
        parser.error("image_path is required unless using --doctor")

    extractor = HealthSafeOCR(engine=args.engine)
    try:
        result = extractor.extract(
            args.image_path,
            mask_sensitive=args.mask_pii,
        )
    except (OcrEngineUnavailableError, TesseractUnavailableError) as exc:
        raise SystemExit(f"OCR failed: {exc}") from exc

    if args.json:
        print(json.dumps(asdict(result), indent=2))
    else:
        print(result.masked_text if args.mask_pii else result.text)


if __name__ == "__main__":
    main()
