# Findings

- Main working tree was clean before this task.
- Config and .env use Qwen-SEA-LION-v4-32B-IT-4BIT; .env.example and README use obsolete settings.
- models/sealion-model contains Llama-SEA-LION-v3.5-8B-R; all four weight shards exist.
- AI service limits history to four messages and truncates history messages to 500 characters.
- Current Qwen model remains listed by AI Singapore. Qwen-SEA-LION-v4.5-27B-IT is an available newer candidate; hardware fit and quality need evaluation.
- RTX 4090 with 24 GB VRAM available. No bot containers were running; cached backend/vLLM/ngrok images enabled immediate deployment.
- Podman compose references a missing Dockerfile.llm. Docker's model ID is hard-coded independently from MODEL_NAME.
- TranslationService bypasses resolved config for base URL and returns unchecked reasoning/truncated output.
- Local v3.5 tokenizer defaults to thinking mode. Its switch is thinking_mode='off'; Qwen uses enable_thinking=false. Both can be set through explicit vLLM chat-template kwargs.
- Official WDA source confirms 1955 free 24-hour support in Indonesian, Vietnamese, English, Thai, Chinese. NIA page identifies 1990 for foreign residents' inquiries. Sources are stored in services/official_resources.py.
- Model server context defaults increased to 8192 for improved branch; bounded chat content defaults to 6000 UTF-8 bytes. Live old deployment retains its original 4096 context.
