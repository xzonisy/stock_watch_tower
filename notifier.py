import requests
import json
import config
import sys

def send_discord_report(report_text, pin=None, url=None):
    """
    Sends the provided report text to the configured Discord Webhook.
    If pin and url are provided, adds a header with the link and PIN.
    """
    if not config.DISCORD_WEBHOOK_URL:
        print("Discord Webhook URL not configured. Skipping notification.")
        return

    url_webhook = config.DISCORD_WEBHOOK_URL
    
    
    headers = {
        "Content-Type": "application/json"
    }

    # 1. Send Header (if exists) - Raw Text for Clickable Links
    if pin and url:
        header_content = f"🔒 **Weekly Report Updated!**\n"
        header_content += f"🔗 **Link:** {url}\n"
        header_content += f"🔑 **PIN:** `{pin}`\n"
        header_content += "----------------------------------------\n"
        
        try:
            requests.post(url_webhook, json={"content": header_content}, headers=headers).raise_for_status()
        except Exception as e:
            print(f"Failed to send Discord header: {e}")

    # 2. Send Report - Code Block for Monospaced Formatting
    # Discord limit is 2000, we'll slice securely
    chunks = []
    
    while len(report_text) > 1900: # Leave some buffer
        # Find a good split point (newline)
        split_idx = report_text.rfind('\n', 0, 1900)
        if split_idx == -1:
            split_idx = 1900
            
        chunks.append(report_text[:split_idx])
        report_text = report_text[split_idx:]
    chunks.append(report_text)
    
    print(f"Sending report body to Discord ({len(chunks)} chunks)...")
    
    for chunk in chunks:
        payload = {
            "content": f"```text\n{chunk}\n```"
        }
        
        try:
            response = requests.post(url_webhook, json=payload, headers=headers)
            response.raise_for_status()
        except Exception as e:
            print(f"Failed to send Discord notification chunk: {e}")
