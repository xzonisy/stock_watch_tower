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
    
    # Construct Message
    message_content = ""
    if pin and url:
        message_content += f"🔒 **Weekly Report Updated!**\n"
        message_content += f"🔗 **Link:** {url}\n"
        message_content += f"🔑 **PIN:** `{pin}`\n"
        message_content += "----------------------------------------\n"
    
    message_content += report_text
    
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
    
    print(f"Sending report to Discord ({len(chunks)} chunks)...")
    
    headers = {
        "Content-Type": "application/json"
    }
    
    for chunk in chunks:
        payload = {
            "content": f"```text\n{chunk}\n```"
        }
        
        try:
            response = requests.post(url_webhook, json=payload, headers=headers)
            response.raise_for_status()
        except Exception as e:
            print(f"Failed to send Discord notification: {e}")
