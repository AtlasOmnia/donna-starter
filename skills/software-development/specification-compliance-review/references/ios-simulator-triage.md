# iOS Simulator Destination & Toolchain Triage

Use this when a specification review requires XCTest evidence on iOS:

1. Discover available destinations first:
   - `cd ios`
   - `xcodebuild -project SpanishTranslator.xcodeproj -scheme SpanishTranslator -showdestinations`

2. Run tests on a concrete simulator destination from that list:
   - `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer xcodebuild -project SpanishTranslator.xcodeproj -scheme SpanishTranslator -configuration Debug -destination "platform=iOS Simulator,name=<device>,OS=<version>" -parallel-testing-enabled NO test`

3. If verification fails before running tests due toolchain utility errors:
   - `xcrun: error: unable to find utility "simctl"` usually means command-line tool path is not bound to expected Xcode.
   - Re-point CLI tools to an active Xcode installation and rerun discovery:
     - `sudo xcode-select -s /Applications/Xcode.app/Contents/Developer`
   - If multiple Xcodes are installed, use the active bundle path in `DEVELOPER_DIR` and retry.

4. If destinations are genuinely absent in CI/host, classify verification as **unverified (environmental)** and continue with source-level proof. Do not convert this into a source defect.

5. Keep failure reporting explicit:
   - attempted destination
   - actual command that failed
   - exact error text
   - resulting verification status (`verified` / `unverified`)