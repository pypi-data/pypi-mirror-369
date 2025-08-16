# AI Image Renamer

![PyPI - Version](https://img.shields.io/pypi/v/ai-image-renamer) ![PyPI - Downloads](https://img.shields.io/pypi/dm/ai-image-renamer) ![PyPI - License](https://img.shields.io/pypi/l/ai-image-renamer)

**AI Image Renamer** is a command-line tool that leverages generative artificial intelligence to intelligently rename your image files based on their content. This helps in organizing your photo collection by giving images more descriptive and searchable filenames.

A [free Groq API key](https://console.groq.com/keys) is required for this project. For a full documentation of this tool, please visit https://docs.kolja-nolte.com/ai-image-renamer.

## Installation

1. Install **AI Image Renamer** via the `pip` command:

   ```bash
   pip install ai-image-renamer
   ```

2. Get your [free API key on console.groq.com](https://console.groq.com/keys) and set it as an environment variable in  your user's `.bashrc`, `.bash_profile`, `.zshrc`, `.zprofile`, or whichever you use:

   ```bash
   export GROQ_API_KEY="..."
   ```

## Usage

The `rename-images` command is your entry point to the tool. However, since it's using [Groq and Meta's Llama 4 Maverick](https://console.groq.com/docs/vision) model, some limitations apply.

### Basic Usage

To rename a single image:

```bash
rename-images path/to/your/image.jpg
```

To rename multiple images:

```bash
rename-images image1.png image2.jpg path/to/another/image.webp
```

### File Types

The following image file types are supported:

* `.jpg` / `.jpeg`
* `.png`
* `.webp`
* `.bmp`

## Contributing

I welcome contributions to **AI Image Renamer**! Please see the [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines on how to contribute.

## Author

1. **Kolja Nolte** (kolja.nolte@gmail.com)

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
