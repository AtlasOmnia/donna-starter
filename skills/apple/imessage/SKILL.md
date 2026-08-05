---
name: imessage
description: imessage — Send and receive iMessages/SMS via the imsg CLI on macOS.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms:
- macos
metadata:
 hermes:
 tags:
 - iMessage
 - SMS
 - messaging
 - macOS
 - Apple
prerequisites:
 commands:
 - imsg
---
# iMessage

Use `imsg` to read and send iMessage/SMS via macOS Messages.app.

## Prerequisites

- **macOS** with Messages.app signed in
- Install: `brew install steipete/tap/imsg`
- Grant Full Disk Access for terminal (System Settings → Privacy → Full Disk Access)
- Grant Automation permission for Messages.app when prompted

## When to Use

- User asks to send an iMessage or text message
- Reading iMessage conversation history
- Checking recent Messages.app chats
- Sending to phone numbers or Apple IDs
- Evaluating iMessage bridge/privacy options for Hermes; see before recommending Photon/Spectrum Cloud

## When NOT to Use

- Telegram/Discord/Slack/WhatsApp messages → use the appropriate gateway channel
- **Hermes iMessage gateway integration (live bidirectional channel)** → that's the BlueBubbles platform adapter in the Hermes gateway. The `imsg` CLI here is for one-off scripting, not persistent gateway connections.
- Group chat management (adding/removing members) → not supported
- Bulk/mass messaging → always confirm with user first
- Sensitive/private conversations over third-party iMessage cloud bridges unless retention, logging, employee-access, attachment-cache, and training-use guarantees are verified first

## Privacy Notes

- Prefer local Mac-backed Messages.app/`imsg` workflows for maximum privacy: content stays on the Mac and uses the user's own Messages account.
- Photon/Spectrum iMessage Cloud is a portability bridge, not an end-to-end-private-from-Photon path. Treat it as a trusted third-party message processor unless Photon provides zero-retention/self-hosted guarantees.
- For platform privacy details and due-diligence questions,

## Quick Reference

### List Chats

```bash
imsg chats --limit 10 --json
```

### View History

```bash
# By chat ID
imsg history --chat-id 1 --limit 20 --json

# With attachments info
imsg history --chat-id 1 --limit 20 --attachments --json
```

### Send Messages

```bash
# Text only
imsg send --to "+14155551212" --text "Hello!"

# With attachment
imsg send --to "+14155551212" --text "Check this out" --file /path/to/image.jpg

# Force iMessage or SMS
imsg send --to "+14155551212" --text "Hi" --service imessage
imsg send --to "+14155551212" --text "Hi" --service sms
```

### Watch for New Messages

```bash
imsg watch --chat-id 1 --attachments
```

## Service Options

- `--service imessage` — Force iMessage (requires recipient has iMessage)
- `--service sms` — Force SMS (green bubble)
- `--service auto` — Let Messages.app decide (default)

## Rules

1. **Always confirm recipient and message content** before sending
2. **Never send to unknown numbers** without explicit user approval
3. **Verify file paths** exist before attaching
4. **Don't spam** — rate-limit yourself

## Example Workflow

User: "Text mom that I'll be late"

```bash
# 1. Find mom's chat
imsg chats --limit 20 --json | jq '.[] | select(.displayName | contains("Mom"))'

# 2. Confirm with user: "Found Mom at +1555123456. Send 'I'll be late' via iMessage?"

# 3. Send after confirmation
imsg send --to "+1555123456" --text "I'll be late"
```
