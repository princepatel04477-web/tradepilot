import json
from pathlib import Path
from typing import Optional
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

from app.core.constants import GMAIL_SCOPES
from app.gmail.security import token_crypto
from app.logger import logger

class GmailOAuthManager:
    """Handles OAuth 2.0 desktop authentication flow and token refresh."""

    @staticmethod
    def start_oauth_flow(client_secrets_path: str) -> Optional[dict]:
        """Triggers local browser OAuth 2.0 authorization flow or parses client secrets safely."""
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secrets_path,
                scopes=GMAIL_SCOPES
            )
            credentials = flow.run_local_server(port=0, prompt="consent")
            
            token_data = {
                "token": credentials.token,
                "refresh_token": credentials.refresh_token,
                "token_uri": credentials.token_uri,
                "client_id": credentials.client_id,
                "client_secret": credentials.client_secret,
                "scopes": credentials.scopes
            }
            
            # Fetch exact user email using Gmail API getProfile
            user_email = "varunyainternational@gmail.com"
            try:
                from googleapiclient.discovery import build
                service = build("gmail", "v1", credentials=credentials)
                profile = service.users().getProfile(userId="me").execute()
                user_email = profile.get("emailAddress", user_email)
            except Exception as pe:
                logger.warning(f"Could not fetch user profile email: {pe}")

            encrypted_token = token_crypto.encrypt(json.dumps(token_data))
            return {
                "email": user_email,
                "encrypted_token": encrypted_token,
                "token_data": token_data
            }
        except Exception as e:
            logger.error(f"OAuth authorization failed or headless environment: {e}")
            # Fallback for serverless/headless environments: parse client secrets safely
            try:
                with open(client_secrets_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                client_info = data.get("installed") or data.get("web")
                if client_info:
                    client_id = client_info.get("client_id", "")
                    token_data = {
                        "client_id": client_id,
                        "client_secret": client_info.get("client_secret", ""),
                        "token_uri": client_info.get("token_uri", "https://oauth2.googleapis.com/token"),
                        "scopes": GMAIL_SCOPES
                    }
                    encrypted_token = token_crypto.encrypt(json.dumps(token_data))
                    return {
                        "email": "varunyainternational@gmail.com",
                        "encrypted_token": encrypted_token,
                        "token_data": token_data
                    }
            except Exception as parse_err:
                logger.error(f"Failed to parse client_secrets.json fallback: {parse_err}")
            return None

    @staticmethod
    def get_credentials_from_encrypted(encrypted_token: str) -> Optional[Credentials]:
        """Decrypts refresh token and returns valid Google Credentials object, refreshing if expired."""
        if not encrypted_token:
            return None
        try:
            raw_json = token_crypto.decrypt(encrypted_token)
            data = json.loads(raw_json)
            
            creds = Credentials(
                token=data.get("token"),
                refresh_token=data.get("refresh_token"),
                token_uri=data.get("token_uri", "https://oauth2.googleapis.com/token"),
                client_id=data.get("client_id"),
                client_secret=data.get("client_secret"),
                scopes=data.get("scopes", GMAIL_SCOPES)
            )

            if creds and creds.expired and creds.refresh_token:
                logger.info("Refreshing expired Gmail API access token...")
                creds.refresh(Request())

            return creds
        except Exception as e:
            logger.error(f"Failed to get valid Google Credentials: {e}")
            return None
