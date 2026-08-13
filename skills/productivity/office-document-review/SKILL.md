---
name: office-document-review
description: office-document-review — Review and proofread office documents in OneDrive or local file trees, including batch folder discovery, document text extraction, and spelling/grammar cleanup workflows.
version: 1.0.0
author: Hermes
license: MIT
platforms:
- linux
- macos
- windows
metadata:
 hermes:
 tags:
 - OneDrive
 - Word
 - document review
 - proofreading
 - spellcheck
 - grammar
 - file trees
---
# Office Document Review

Use this skill when the user wants you to inspect a OneDrive/SharePoint-style folder tree, locate a subfolder by name/date, and proofread all documents in it for spelling and grammar.

This is a workflow skill, not a single-app skill: it covers local file-system browsing, document text extraction, and batch proofreading notes.

## Triggers

- "go to the OneDrive folder"
- "look in folder X and then folder Y"
- "proofread all those documents"
- "check for spelling/grammar errors in the docs"
- "review the files in this folder"

## Core workflow

1. **Resolve the real path first**
 - Prefer a filesystem path over guessing from the user’s wording.
 - Folder names in casual speech may not match the actual on-disk name exactly.
 - If the exact folder cannot be found, list the visible folder names and state what is missing before asking for clarification.

2. **Search the tree recursively**
 - Use the live file tree to locate the target folder and confirm the actual path.
 - When the user gives a date-like folder name, search for variant spellings and punctuation (`6-2-26`, `6.2.26`, `6_2_26`, `6-2-2026`) before assuming it does not exist.

3. **Inventory the documents**
 - Identify all files in the target folder.
 - Group by extension and prioritize editable office docs (`.docx`, `.doc`, `.odt`, `.rtf`, `.txt`) before PDFs or spreadsheets.

4. **Extract readable text**
 - For Word/Office files, extract the text in a way that preserves headings and paragraphs as much as possible.
 - If the file-reading tool rejects `.docx` as binary, do not classify the document as unreadable and do not repeat the same call across the batch. A DOCX is a ZIP package: validate it with Python `zipfile`, then use `python-docx` when available or extract `word/document.xml` and convert paragraph/table XML to bounded text. Record package validity, paragraph/table counts, and extraction method. Use native Word or PDF rendering separately when layout—not just text—is under review.
 - When validating generated fixtures, compare extracted text against the fixture specification or authoritative `.txt` source before opening Word. A valid ZIP alone does not prove the fixture contains the intended content.
 - For scanned or image-based files, use OCR or an extraction tool first.
 - If a file is not meaningfully text-reviewable after at least one appropriate format-specific fallback, say so explicitly instead of pretending to proofread it.

5. **Proofread for two passes**
 - Pass 1: spelling, grammar, punctuation, capitalization.
 - Pass 2: obvious clarity issues, duplicated words, inconsistent dates/names, and broken formatting that would change meaning.
 - Keep business wording intact unless the user asked for rewriting.

6. **Report findings file-by-file**
 - Summarize each document with:
 - file name
 - issue count
 - short list of fixes or concerns
 - If no issues are found, say that clearly.

7. **Do not silently modify files unless asked**
 - The default action is review/report.
 - If the user wants edits, confirm the target files and whether they want tracked wording changes or a clean rewrite.

## Pitfalls

- Casual folder names may be approximate; always verify the actual folder names seen in the tree.
- A folder search that returns the parent tree but not the exact folder is not a success; say what was found and what was not.
- If the user says they downloaded the files, re-inventory the local download folder first; do not assume the original folder contents or the original extension set survived the move.
- Do not claim “everything is fine” for a batch until each file was actually inspected.
- If a document is large, inspect enough of it to make a real proofreading judgment rather than sampling one paragraph and extrapolating.
- Keep the user informed if the folder path is ambiguous instead of asking generic questions.

## Verification

Before closing the task, confirm:

- the folder path was resolved,
- every target document was identified,
- each document was reviewed or explicitly excluded with a reason,
- and the final report separates true findings from non-reviewable files.

## Session note file


## Practical notes

- Always verify the exact business OneDrive root before drilling into a dated subfolder.
- If the user says "OneDrive" in a work/document-review context and does not qualify which account, default to the work tenant first (`OneDrive - <work tenant>`) rather than the personal OneDrive. Keep the two trees mentally separate and say which root you are using when ambiguity could matter.
- If folder recursion on a synced OneDrive tree is unstable, list the parent first and narrow the search in smaller steps instead of forcing a full tree walk.
- When direct recursion throws `Resource deadlock avoided`, try a shallow parent `find`/inventory pass and then inspect the exact subfolder file-by-file.
- If the user says they downloaded the files, re-inventory the local download folder first; do not assume the original folder contents or extensions survived the move.
- Keep the final review file-by-file so the user can see what was actually checked.

## Session reference


- When the user asks for "edits needed," separate true spelling/grammar fixes from OCR or extraction artifacts and label each file accordingly.
