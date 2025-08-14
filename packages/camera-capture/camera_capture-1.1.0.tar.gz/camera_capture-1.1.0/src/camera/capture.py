from datetime import datetime
import logging
from pathlib import Path
import sys
import pandas as pd
from camera.config import CameraConfig
from camera.camera_locations import load_urls_from_file
from camera.kenya_capture import capture
from camera.capture_functions import save_camera_image
from camera.timing_functions import determine_delay_to_next_capture_time, wait_until_next_capture
from camera.timing_functions import EndCaptureException
from camera.cli_parser import cli_parser

CAPTURE_TODAY = 1
NONSTOP_CAPTURE = 2


logger = logging.getLogger(__name__)


def capture_all(all_urls: pd.DataFrame, config: CameraConfig) -> None:
    """Capture images from all cameras in the camera locations file."""
    images_root = config.image_save_path
    for _, row in all_urls.iterrows():
        url = row['url']
        location = row['location']
        logger.info(f"Capturing image for {location} at {url}")
        img_data, img_url = capture(url)
        if img_data:
            save_camera_image(img_data, images_root, location, suffix=Path(img_url).suffix)
        else:
            logger.error(f"No valid image data was captured for {location} at {url}")
        logger.info(f"Finished capturing image for {location}")


def capture_all_repeat(all_urls: pd.DataFrame, config: CameraConfig, capture_mode: int = CAPTURE_TODAY) -> bool:
    target = datetime.now()
    wait_period_length = 600    # 10 minutes, to allow for periodic updates
    day_end = target.replace(hour=config.end.hour, minute=config.end.minute, second=0, microsecond=0)
    success = False
    try:
        while True:
            capture_all(all_urls, config)
            sleep_time, capture_time = determine_delay_to_next_capture_time(config, target)
            if (capture_mode == CAPTURE_TODAY) and capture_time > day_end:
                logger.info("Capture finished for today.")
                success = True
                break
            logger.info(f'Next capture at {capture_time}; Press Ctrl+C to stop.')
            wait_until_next_capture(sleep_time, wait_period_length,
                                    print_func=print if config.verbose else (lambda *a, **k: None))
            target = datetime.now()
    except KeyboardInterrupt:
        logger.info("Stopping repeat capture.")
    except EndCaptureException:
        logger.info("Stopping repeat capture.")

    return success


def main():
    parser = cli_parser()
    args = parser.parse_args()
    if not args.Command:
        parser.print_help()
        sys.exit(1)

    config = CameraConfig()  # Load the configuration

    if str(args.Command).startswith('run'):
        all_urls = load_urls_from_file(config)
        if all_urls.empty:
            logger.error("No camera URLs found. Please check the camera locations file.")
            sys.exit(1)

    if args.verbose:
        config.verbose = True

    if args.Command == 'run':
        logger.info("Capturing once.")
        capture_all(all_urls, config)
    elif args.Command == 'run-repeat':
        logger.info("Capturing in one day repeat mode. Press Ctrl+C to stop.")
        capture_all_repeat(all_urls, config, CAPTURE_TODAY)
    elif args.Command == 'run-repeat-no-limit':
        logger.info("Capturing in continuous repeat mode. Press Ctrl+C to stop.")
        capture_all_repeat(all_urls, config, NONSTOP_CAPTURE)
    else:
        args.func(args)


if __name__ == "__main__":
    main()
