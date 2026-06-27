import argparse
import json
from dataclasses import asdict

from .extractor import HealthSafeOCR


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Safe OCR for healthcare images",
    )
    parser.add_argument("image_path")
    parser.add_argument("--mask-pii", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    extractor = HealthSafeOCR()
    result = extractor.extract(
        args.image_path,
        mask_sensitive=args.mask_pii,
    )

    if args.json:
        print(json.dumps(asdict(result), indent=2))
    else:
        print(result.masked_text if args.mask_pii else result.text)


if __name__ == "__main__":
    main()

