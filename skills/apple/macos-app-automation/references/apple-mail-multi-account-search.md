# Apple Mail multi-account search fallback

## Trigger

Use when a user says a message exists but a CLI mail search does not find it, especially when the expected provider/account is not configured in the CLI client.

## Reusable lesson

A mailbox search result is scoped evidence. In the observed case, Himalaya exposed only an iCloud account while Apple Mail also had a Google account. Repeated iCloud searches could never resolve a Google Search Console notification.

## Bounded workflow

1. List CLI mail accounts and state the actual coverage.
2. If the expected account is absent, list Apple Mail accounts with a read-only AppleScript probe.
3. Start with a bounded Inbox probe. This direct object path is reliable when the mailbox exists:

 ```applescript
 tell application "Mail" to get count of messages of mailbox "INBOX" of account "Google"
 ```

4. Read recent Inbox metadata before searching bodies. Return only message ID, subject, sender, received date, and read status; use a cutoff such as the last 7–14 days.
5. Search likely subject and sender tokens independently. An empty successful result means no match in that account/mailbox/predicate—not global absence.
6. Do not assume a mailbox displayed as `All Mail` is addressable by the literal AppleScript expression `mailbox "All Mail" of account ...`. On `-1728`, iterate the mailbox objects instead:

 ```applescript
 tell application "Mail"
 set rows to {}
 repeat with b in every mailbox of account "Google"
 try
 set hits to every message of b whose subject contains "index"
 repeat with m in hits
 set end of rows to {name of b, id of m, subject of m, sender of m, date received of m, read status of m}
 end repeat
 end try
 end repeat
 return rows
 end tell
 ```

7. If object iteration identifies the target label but the literal name remains unaddressable, use an ordinal only as a runtime-discovered object handle:

 ```applescript
 tell application "Mail" to get {name, count of messages} of mailbox 3 of account "Google"
 ```

 First enumerate the account's mailbox names in order, then probe the candidate ordinal and require the returned `name` to equal the intended mailbox (for example, `All Mail`) before querying messages. Never persist or assume `mailbox 3`; label order can change. Once verified, combine a date cutoff with a sender or subject predicate before reading bodies.
8. Avoid `content contains ...` across every mailbox until narrowed by account, mailbox, and date. Broad body searches can time out.
9. Before the final absence conclusion, force a sync with `check for new mail`, wait briefly, and rerun the bounded recent-metadata query.
10. If GUI fallback is needed, first confirm Mail has a capturable window. A running Mail process may have no on-screen window; create a message viewer through AppleScript, then recapture. Do not loop zero-size captures.
11. Open and read the matching message before diagnosing the reported site problem. An independent live-site check can establish current indexability, but it does not identify the URL or historical reason named in the notification.
12. Keep alert evidence and current-state evidence separate. For an indexing notice, independently check the affected URL, HTTP status/headers, robots policy, sitemap, canonical and `noindex` directives, plus current search visibility. Current homepage indexing does not prove that every URL is indexed, and a stale/property-specific notice does not outweigh a verified current recovery.

## Search terms for indexing notices

Run independent searches for:

- sender variants: Google, search-console, sc-noreply
- subject variants: index, indexing, pages, Search Console, new reason
- exact domain name

Do not report “not found” globally unless every relevant configured account and likely folder was actually searched.