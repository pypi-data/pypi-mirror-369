# AI Subtitle Translator

Advanced subtitle translator with AI support and web API. Converts SRT subtitle files to styled ASS format with bilingual or monolingual translations using OpenAI, Google Gemini, or DeepSeek APIs.

## Features

- **Bazarr Integration**: Direct post-processing hook for automatic subtitle translation
- **Web API**: FastAPI-based REST API for subtitle translation
- **CLI Tool**: Command-line interface for batch processing with subcommands
- **Multiple AI Providers**: OpenAI, Google Gemini, DeepSeek support
- **Fallback Providers**: Automatic failover to secondary AI providers when primary fails
- **Translation Validation**: Statistical analysis tool to detect and report sync/quality issues
- **Adaptive Batching**: Smart sentence-boundary detection prevents mid-sentence cuts
- **Bilingual Mode**: Displays original text on top and translated text below
- **Monolingual Mode**: Replaces original text with translation
- **Monolingual Extraction**: Convert existing bilingual files to monolingual without re-translating
- **Smart Translation**: Full text or selective difficulty translation modes
- **Resumable**: Automatically saves progress and can resume if interrupted
- **Batch Processing**: Processes subtitles in batches for efficient API usage

## Quick Start - Bazarr Integration

### 1. Docker Compose Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yanp/ai-subtitle-translator.git
   cd ai-subtitle-translator
   ```

2. **Set up environment variables:**

   ```bash
   cp .env.example .env
   # Edit .env and add: DEEPSEEK_API_KEY=your_actual_api_key_here
   ```

3. **Start the service:**
   ```bash
   docker-compose up -d
   ```

### 2. Bazarr Hook Configuration

In Bazarr Settings → Subtitles → Custom Post-Processing → Command:

```bash
curl -X POST "http://ai-subtitle-translator:8080/translate" -d input_path="{{subtitles}}";
```

### 3. Integration with Existing Bazarr

If you already have Bazarr running, add the translator to your existing docker-compose:

```yaml
services:
  subtitle-translator:
    build: .
    ports:
      - "8000:8080"
    environment:
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
      - PUID=${PUID:-1000}
      - PGID=${PGID:-1000}
    volumes:
      - /path/to/media:/media/subtitles # Same mount as Bazarr
    restart: unless-stopped
    networks:
      - media-network
```

## Alternative Setup Methods

### Local Development

1. **Install uv:**

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Install dependencies:**

   ```bash
   uv sync --all-extras
   ```

3. **Set environment variables:**

   ```bash
   export DEEPSEEK_API_KEY=your_api_key_here
   ```

4. **Run the API:**
   ```bash
   uv run fastapi dev src/ai_subtitle_translator/app.py
   ```

### CLI Usage

The CLI uses subcommands for different operations:

**Translation:**

```bash
uv run ai-subtitle-translator translate input.srt [options]
```

**Translation Options:**

- `-o, --output`: Output file path
- `--translation-mode`: `bilingual` or `monolingual`
- `--prompt-template`: `full_text` or `selective_difficulty`
- `-p, --provider`: Primary AI provider (`openai`, `gemini`, `deepseek`)
- `--fallback-provider`: Secondary AI provider for automatic failover
- `--batch-size`: Number of lines per API call (default: adaptive)

**Translation Example:**

```bash
uv run ai-subtitle-translator translate movie.srt \
  --translation-mode bilingual \
  --provider deepseek \
  --fallback-provider openai
```

**Validation:**

```bash
uv run ai-subtitle-translator validate input.ass [options]
```

**Validation Options:**

- `--threshold`: MAD threshold for detecting sync issues (default: 2.0)
- `--detailed`: Show detailed analysis per subtitle line

**Validation Example:**

```bash
uv run ai-subtitle-translator validate movie.en-zh.ass --detailed
```

**Extraction from Bilingual Files:**

```bash
# Extract monolingual subtitles from existing bilingual ASS files
uv run ai-subtitle-translator translate movie.en-zh.ass --extract-monolingual
```

This extracts only the translated text with proper monolingual styling and positioning, perfect when you want monolingual versions without re-translating.

## API Usage

### Configuration

The API is configured through environment variables.

### Translate Subtitle File

**POST** `/translate`

Supports two modes: file upload or file path processing.

#### Mode 1: File Upload (Web Interface)

Upload an SRT file and get back a translated ASS file.

**Parameters:**

- `file`: SRT subtitle file to upload

**Example:**

```bash
curl -X POST "http://localhost:8080/translate" \
  -F "file=@subtitle.srt" \
  -o translated_subtitle.ass
```

#### Mode 2: File Path (For Bazarr Integration)

Process files on the server filesystem using file paths.

**Parameters:**

- `input_path`: Path to SRT subtitle file on server
- `output_path`: Output path for translated file (optional, defaults to same directory with .en-zh.ass extension)

**Example:**

```bash
curl -X POST "http://localhost:8000/translate" \
  -F "input_path=/media/subtitles/movie.srt"
```

**Response:**

```json
{
  "success": true,
  "message": "✅ Translation completed successfully",
  "output_filename": "/media/subtitles/movie.en-zh.ass"
}
```

### Get Available Providers

**GET** `/providers`

Returns available AI providers and their configuration status.

## Configuration

### Environment Variables

#### API Keys (Required)

| Variable           | Description                    | Required            |
| ------------------ | ------------------------------ | ------------------- |
| `DEEPSEEK_API_KEY` | DeepSeek API key (recommended) | Yes                 |
| `OPENAI_API_KEY`   | OpenAI API key                 | For OpenAI provider |
| `GEMINI_API_KEY`   | Google Gemini API key          | For Gemini provider |

#### API Server Defaults (Optional)

| Variable                   | Description                      | Default   |
| -------------------------- | -------------------------------- | --------- |
| `DEFAULT_PROVIDER`         | Default AI provider              | deepseek  |
| `FALLBACK_PROVIDER`        | Default fallback provider        | None      |
| `DEFAULT_MODEL`            | Default model name               | None      |
| `DEFAULT_TRANSLATION_MODE` | Default translation mode         | bilingual |
| `DEFAULT_PROMPT_TEMPLATE`  | Default prompt template          | full_text |
| `DEFAULT_BATCH_SIZE`       | Default batch size for API calls | 80        |

#### System Configuration (Optional)

| Variable | Description                   | Default |
| -------- | ----------------------------- | ------- |
| `PUID`   | User ID for file permissions  | 1000    |
| `PGID`   | Group ID for file permissions | 1000    |

**API Server Configuration Example:**

```bash
# .env file for API server defaults
DEFAULT_PROVIDER=deepseek
FALLBACK_PROVIDER=openai
DEEPSEEK_API_KEY=your_deepseek_key
OPENAI_API_KEY=your_openai_key
```

**Note**: Set PUID/PGID to match your host user to avoid permission issues:

```bash
# Find your user/group IDs
id

# Set in .env file
PUID=1001
PGID=1001
```

### Translation Modes

- **Bilingual**: Shows original text on top, translation below
- **Monolingual**: Replaces original text with translation

### Prompt Templates

- **Full Text**: Translates every subtitle line
- **Selective Difficulty**: Only translates complex phrases, slang, or cultural references

## Development

### Setup

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync --all-extras --dev
```

### Code Quality

```bash
# Format code
uv run black .

# Lint code
uv run ruff check .

# Type checking
uv run mypy .
```

### Testing

```bash
# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=src
```

## Health Monitoring

Check service health:

```bash
curl http://localhost:8080/health
```

Check available providers:

```bash
curl http://localhost:8080/providers
```

## Performance

- **Translation Speed**: ~5-30 seconds per file (depends on length)
- **API Costs**: ~$0.001-0.01 per subtitle file with DeepSeek
- **Batch Processing**: Optimized for efficiency

## Docker Build

### Build locally

```bash
docker build -t ai-subtitle-translator .
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

- Open an issue on GitHub
- Check the API documentation at `/docs` when running the server
- Review the example files in the repository
