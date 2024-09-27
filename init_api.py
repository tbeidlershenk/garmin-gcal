from garminconnect import Garmin, GarminConnectAuthenticationError
from garth.exc import GarthHTTPError
import os
import requests
from logger import logger


def get_mfa():
    """Get MFA."""

    return input("MFA one-time code: ")


def init_api(email, password, tokenstore, tokenstore_base64):
    """Initialize Garmin API with your credentials."""

    try:
        logger.info(
            f"Trying to login to Garmin Connect using token data from directory '{tokenstore}'...")

        garmin = Garmin()
        garmin.login(tokenstore)

    except (FileNotFoundError, GarthHTTPError, GarminConnectAuthenticationError):
        # Session is expired. You'll need to log in again
        logger.info(
            f"Login tokens not present, login with your Garmin Connect credentials to generate them. They will be stored in '{tokenstore}' for future use.")
        try:
            garmin = Garmin(email=email, password=password,
                            is_cn=False, prompt_mfa=get_mfa)
            garmin.login()
            # Save Oauth1 and Oauth2 token files to directory for next login
            garmin.garth.dump(tokenstore)
            logger.info(
                f"Oauth tokens stored in '{tokenstore}' directory for future use. (first method)")
            # Encode Oauth1 and Oauth2 tokens to base64 string and safe to file for next login (alternative way)
            token_base64 = garmin.garth.dumps()
            dir_path = os.path.expanduser(tokenstore_base64)
            with open(dir_path, "w") as token_file:
                token_file.write(token_base64)
            logger.info(
                f"Oauth tokens encoded as base64 string and saved to '{dir_path}' file for future use. (second method)"
            )
        except (FileNotFoundError, GarthHTTPError, GarminConnectAuthenticationError, requests.exceptions.HTTPError) as err:
            logger.info("Error occurred during Garmin Connect login.")
            return None

    return garmin
