import logging
import os
import sys
from io import BytesIO
from pathlib import Path
from shutil import copy
from subprocess import run

from logikal_utils.testing import hide_traceback
from PIL import Image, ImageChops

logger = logging.getLogger(__name__)


@hide_traceback
def assert_image_equal(actual: bytes, expected: Path, image_tmp_path: Path) -> None:
    tmp_actual_path = image_tmp_path / 'actual.png'
    tmp_expected_path = image_tmp_path / 'expected.png'
    tmp_diff_path = image_tmp_path / 'diff.png'

    logger.info(f'Checking expected image in "{expected}"')
    if expected.is_file():
        with Image.open(BytesIO(actual)) as actual_image, Image.open(expected) as expected_image:
            if actual_image == expected_image:
                logger.info('The actual image matches the expected image')
                return

            tmp_actual_path.write_bytes(actual)  # saving the temporary actual image
            copy(expected, tmp_expected_path)  # saving the temporary expected image
            diff_image = ImageChops.invert(ImageChops.difference(
                expected_image.convert('RGB'),
                actual_image.convert('RGB'),
            ))
            diff_image.save(str(tmp_diff_path))  # saving the temporary diff image
            save_image_prompt(
                message='Actual image differs from the expected image',
                source=tmp_actual_path, destination=expected, difference=tmp_diff_path,
            )
    else:
        logger.info('Expected image not found')
        tmp_actual_path.write_bytes(actual)  # saving the temporary actual image
        save_image_prompt(
            message='Expected image file does not exist',
            source=tmp_actual_path, destination=expected,
        )


def save_image_prompt(
    message: str,
    source: Path,
    destination: Path,
    difference: Path | None = None,
) -> None:
    if not sys.stdin.isatty():
        error_lines = [
            f'{message} and this is not an interactive session (consider using --live)',
            f'  Actual: {source.as_uri()}',
            f'  Expected: {destination.as_uri()}',
        ]
        if difference:
            error_lines.append(f'  Difference: {difference.as_uri()}')
        raise AssertionError('\n'.join(error_lines))
    try:
        short_destination = destination.relative_to(os.getcwd())
    except ValueError:
        short_destination = destination

    colors = {'red': '\033[31m\033[1m', 'reset': '\033[0m'}
    print(f'\n{colors['red']}{message}!{colors['reset']}')
    print(short_destination)

    prompt = f'{colors['red']}>{colors['reset']} '
    if (opener := Path('/usr/bin/xdg-open')).exists():
        response = input(f'{prompt}Press "enter" to open or type "s" to skip or "c" to cancel: ')
        if response == 's':
            logger.info('Image opening skipped')
        elif not response:
            # This subprocess call is secure as it is not using untrusted input
            run([str(opener), str(source)], check=False)  # nosec
        else:
            raise AssertionError('Image opening canceled')
    else:
        print(f'{prompt}See {source.as_uri()}')

    response = input(f'{prompt}Type "accept" to accept this version or press "enter" to reject: ')
    if response == 'accept':
        destination.parent.mkdir(parents=True, exist_ok=True)
        copy(source, destination)
        logger.info(f'Image saved at "{short_destination}"')
    else:
        raise AssertionError(f'Image rejected ({source.as_uri()})')
