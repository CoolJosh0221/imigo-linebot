#!/usr/bin/env python3
"""
Automatically update LINE webhook URL with ngrok's public URL

This script:
1. Waits for ngrok to be ready
2. Fetches the public HTTPS URL from ngrok's API
3. Updates the LINE Messaging API webhook endpoint
4. Displays the new webhook URL

Usage:
    python scripts/update_line_webhook.py

Requirements:
    - LINE_CHANNEL_ACCESS_TOKEN in .env
    - ngrok running on port 4040 (default)
"""
import os
import sys
import time
import requests
from dotenv import load_dotenv


def get_ngrok_url(max_retries: int = 10, retry_delay: int = 2) -> str:
    """
    Get the public HTTPS URL from ngrok's local API

    Args:
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds

    Returns:
        Public HTTPS URL from ngrok

    Raises:
        RuntimeError: If ngrok URL cannot be retrieved
    """
    ngrok_api_url = "http://localhost:4040/api/tunnels"

    for attempt in range(max_retries):
        try:
            response = requests.get(ngrok_api_url, timeout=5)
            response.raise_for_status()

            tunnels = response.json().get("tunnels", [])

            # Find the HTTPS tunnel
            for tunnel in tunnels:
                if tunnel.get("proto") == "https":
                    public_url = tunnel.get("public_url")
                    if public_url:
                        print(f"✅ Found ngrok URL: {public_url}")
                        return public_url

            print(f"⚠️  No HTTPS tunnel found (attempt {attempt + 1}/{max_retries})")

        except requests.exceptions.RequestException as e:
            print(f"⚠️  Waiting for ngrok to start... (attempt {attempt + 1}/{max_retries})")

        if attempt < max_retries - 1:
            time.sleep(retry_delay)

    raise RuntimeError(
        "Could not get ngrok URL. Make sure ngrok is running on port 4040.\n"
        "Start ngrok with: ngrok http 8000"
    )


def update_line_webhook(webhook_url: str, access_token: str) -> bool:
    """
    Update LINE Messaging API webhook endpoint

    Args:
        webhook_url: The new webhook URL (must be HTTPS)
        access_token: LINE Channel Access Token

    Returns:
        True if update was successful, False otherwise
    """
    line_api_url = "https://api.line.me/v2/bot/channel/webhook/endpoint"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "endpoint": webhook_url
    }

    try:
        print(f"📡 Updating LINE webhook to: {webhook_url}")
        response = requests.put(line_api_url, json=payload, headers=headers)
        response.raise_for_status()

        print("✅ LINE webhook updated successfully!")
        return True

    except requests.exceptions.HTTPError as e:
        print(f"❌ Failed to update LINE webhook: HTTP {e.response.status_code}")
        print(f"   Response: {e.response.text}")
        return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to update LINE webhook: {e}")
        return False


def test_webhook(webhook_url: str, access_token: str) -> bool:
    """
    Test the webhook endpoint by calling LINE's test endpoint

    Args:
        webhook_url: The webhook URL to test
        access_token: LINE Channel Access Token

    Returns:
        True if test was successful, False otherwise
    """
    line_test_url = "https://api.line.me/v2/bot/channel/webhook/test"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "endpoint": webhook_url
    }

    try:
        print(f"🧪 Testing webhook endpoint...")
        response = requests.post(line_test_url, json=payload, headers=headers)
        response.raise_for_status()

        result = response.json()
        success = result.get("success", False)
        status_code = result.get("statusCode")

        if success:
            print(f"✅ Webhook test successful! (Status: {status_code})")
            return True
        else:
            print(f"⚠️  Webhook test returned: {result}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"⚠️  Webhook test failed: {e}")
        return False


def main():
    """Main function to update LINE webhook with ngrok URL"""
    print("=" * 60)
    print("LINE Webhook Auto-Update Script")
    print("=" * 60)

    # Load environment variables
    load_dotenv()

    access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
    if not access_token:
        print("❌ Error: LINE_CHANNEL_ACCESS_TOKEN not found in .env file")
        print("   Please add your LINE Channel Access Token to .env")
        sys.exit(1)

    try:
        # Get ngrok public URL
        print("\n📍 Step 1: Getting ngrok public URL...")
        ngrok_url = get_ngrok_url()

        # Construct webhook endpoint
        webhook_url = f"{ngrok_url}/webhook"

        # Update LINE webhook
        print(f"\n📍 Step 2: Updating LINE webhook...")
        success = update_line_webhook(webhook_url, access_token)

        if not success:
            print("\n⚠️  Webhook update failed. You may need to update it manually.")
            print(f"   Webhook URL: {webhook_url}")
            sys.exit(1)

        # Test the webhook
        print(f"\n📍 Step 3: Testing webhook...")
        test_webhook(webhook_url, access_token)

        # Success message
        print("\n" + "=" * 60)
        print("✅ Setup Complete!")
        print("=" * 60)
        print(f"Webhook URL: {webhook_url}")
        print("\nYour LINE bot is now ready to receive messages!")
        print("=" * 60)

    except RuntimeError as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
