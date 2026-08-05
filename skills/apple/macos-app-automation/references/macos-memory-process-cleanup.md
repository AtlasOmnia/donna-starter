# macOS Memory and Process Cleanup

Use this when the user asks what is consuming RAM or asks to close unnecessary processes.

## Read-only audit

Check live state rather than inferring from installed apps:

```bash
memory_pressure
top -l 1 -n 0
sysctl vm.swapusage
ps -axo pid,ppid,user,%cpu,%mem,rss,etime,state,comm
```

Interpret **memory pressure** before raw “unused” RAM. macOS intentionally fills RAM with cache; compressed memory and swap history alone do not prove current distress. Report uptime because a long-running system can accumulate compressed memory and swap even when current pressure is healthy.

Aggregate related helper processes by application or service instead of reporting only the largest PID. Useful families include Safari/WebKit, Chrome/CDP, Hermes, Playwright, Electron apps, Xcode/Simulator, local-model apps, and temporary test workers. Sum RSS and process count deterministically with Python rather than mental arithmetic.

Before recommending termination, distinguish:

- user-facing apps that may contain unsaved work;
- intentional background services required by Hermes or automation;
- clearly orphaned temporary/test processes;
- negligible helpers that are not worth disabling.

Do not quit user-facing applications without explicit scope. Explain which capability a background service provides before proposing to stop it.

## Safe cleanup sequence

1. Gracefully terminate exact orphaned worker processes with `SIGTERM`.
2. Quit explicitly authorized GUI apps through AppleScript:

 ```bash
 osascript -e 'tell application "App Name" to quit'
 ```

3. Wait briefly for graceful shutdown.
4. Verify every target independently.
5. Re-read memory and swap state; report measured change without promising that macOS will immediately release every page.

## Exact-process matching pitfall

Avoid broad `pkill -f` patterns when the pattern text can appear in the cleanup shell’s own command line. Enumerate `ps` output in Python, require the expected executable and full argument shape, then signal the resulting PIDs.

Likewise, verification that searches full command lines can falsely match the verification shell itself because the target strings are embedded in its script. For GUI apps, compare the exact `comm` executable path, for example:

```text
/Applications/Xcode.app/Contents/MacOS/Xcode
/Applications/ChatGPT.app/Contents/MacOS/ChatGPT
/Applications/LM Studio.app/Contents/MacOS/LM Studio
```

For temporary Node workers, require both an executable ending in `/node` and the expected temporary-script path. A generic substring match is not sufficient evidence.

## Docker check

“Is Docker running?” means engine reachability, not merely whether a privileged helper is loaded. Check the Docker API/socket and active engine processes. A lightweight `com.docker.vmnetd` helper by itself does **not** mean Docker Desktop or Docker Engine is running, and its tiny memory footprint usually is not worth disabling.
