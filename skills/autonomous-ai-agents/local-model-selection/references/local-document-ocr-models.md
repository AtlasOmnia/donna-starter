# Local document OCR / PDF parsing models

Use this reference when the user asks about local models that convert PDFs/images into structured outputs for RAG, extraction, or downstream JSON.

## Fast identification pattern

If the user says a "local model" that "strips PDFs down to JSON" or outputs Markdown/HTML/JSON, the likely answer is:

- **Chandra OCR 2** — `datalab-to/chandra-ocr-2`
 - HF: https://huggingface.co/datalab-to/chandra-ocr-2
 - GitHub: https://github.com/datalab-to/chandra
 - Outputs Markdown, HTML, and JSON with layout information.
 - Handles PDFs/images locally; vLLM recommended, Hugging Face Transformers supported.
 - Good for complex tables, forms, handwriting, math, layout, image captions, and multilingual OCR.
 - Quick commands:
 ```bash
 pip install chandra-ocr
 chandra_vllm
 chandra input.pdf ./output
 ```

Close alternatives to distinguish:

- **OCRFlux-3B** — `ChatDOC/OCRFlux-3B`
 - HF: https://huggingface.co/ChatDOC/OCRFlux-3B
 - Converts PDFs/images into clean Markdown; pipeline stores intermediate JSONL and can generate final Markdown.
 - Fine-tuned from Qwen2.5-VL-3B-Instruct; local vLLM/Docker workflow.
 - Best clue: user says "clean Markdown" or cross-page table/paragraph merging, not direct JSON output.

- **Baidu Unlimited-OCR** — `baidu/Unlimited-OCR`
 - HF: https://huggingface.co/baidu/Unlimited-OCR
 - One-shot long-horizon PDF/image document parsing; outputs structured parsing text/Markdown-style content.
 - Best clue: user mentions DeepSeek-OCR successor, long-horizon parsing, vLLM/SGLang, or Baidu.

- **GLM-OCR** — `zai-org/GLM-OCR`
 - Local/open OCR model; some deployments expose JSON-schema style APIs through wrappers.
 - Best clue: user mentions Z.ai/GLM or Replicate examples returning JSON objects.

## Answering style for recall questions

When the user asks "what was that model?":
1. Give the best candidate first, not a long comparison.
2. Add one sentence explaining why it matches the clue.
3. Include the model link and a minimal install/run snippet only if useful.
4. Mention close alternatives only after the main answer, clearly labeled.

Example:

"You’re thinking of Chandra OCR 2 (`datalab-to/chandra-ocr-2`). It’s the local/open OCR model that converts PDFs/images into Markdown, HTML, and JSON while preserving layout information."
