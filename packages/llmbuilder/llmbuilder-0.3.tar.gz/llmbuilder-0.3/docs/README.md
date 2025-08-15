# LLMBuilder Documentation

This directory contains the complete documentation for the LLMBuilder package, built with MkDocs and Material theme.

## 🚀 Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Serve locally with live reload
mkdocs serve

# Open http://127.0.0.1:8000 in your browser
```

### Build Documentation

```bash
# Build static site
mkdocs build

# Output will be in 'site' directory
```

### Deploy to GitHub Pages

```bash
# Deploy to GitHub Pages
mkdocs gh-deploy

# Or use the deployment script
./deploy_docs.bat  # Windows
```

## 📁 Documentation Structure

```
docs/
├── index.md                    # Homepage
├── getting-started/            # Getting started guides
│   ├── installation.md
│   ├── quickstart.md
│   └── first-model.md
├── user-guide/                 # Comprehensive user guides
│   ├── configuration.md
│   ├── data-processing.md
│   ├── tokenization.md
│   ├── training.md
│   ├── fine-tuning.md
│   ├── generation.md
│   └── export.md
├── cli/                        # CLI reference
│   └── overview.md
├── api/                        # Python API reference
│   └── core.md
├── examples/                   # Working examples
│   └── basic-training.md
├── reference/                  # Reference materials
│   ├── migration.md
│   └── faq.md
└── requirements.txt            # Documentation dependencies
```

## 🎨 Features

- **Material Design**: Beautiful, responsive theme
- **Search**: Full-text search across all pages
- **Code Highlighting**: Syntax highlighting for all languages
- **Interactive Elements**: Tabs, admonitions, diagrams
- **Mobile Responsive**: Perfect on all devices
- **Dark/Light Mode**: User preference toggle
- **Auto-generated API Docs**: From docstrings
- **Git Integration**: Last updated timestamps

## 🔧 Configuration

The documentation is configured in `mkdocs.yml` in the project root. Key settings:

- **Theme**: Material Design with custom colors
- **Plugins**: Search, git dates, API documentation
- **Extensions**: Code blocks, admonitions, diagrams
- **Navigation**: Hierarchical structure

## 📝 Writing Documentation

### Markdown Features

The documentation supports enhanced Markdown with:

- **Admonitions**: `!!! tip`, `!!! warning`, etc.
- **Code blocks**: With syntax highlighting
- **Tabs**: For multiple examples
- **Diagrams**: Mermaid diagrams
- **Math**: LaTeX math expressions

### Example Admonitions

```markdown
!!! tip "Pro Tip"
    This is a helpful tip for users.

!!! warning "Important"
    This is a warning about potential issues.

!!! example "Example"
    This shows how to do something.
```

### Code Blocks

```markdown
```python
import llmbuilder as lb
config = lb.load_config(preset="cpu_small")
```
```

### Tabs

```markdown
=== "Python"
    ```python
    import llmbuilder as lb
    ```

=== "CLI"
    ```bash
    llmbuilder --help
    ```
```

## 🚀 Deployment

### GitHub Pages (Automatic)

The documentation automatically deploys to GitHub Pages when you push to the main branch, thanks to the GitHub Action in `.github/workflows/docs.yml`.

### Manual Deployment

```bash
# Deploy to GitHub Pages
mkdocs gh-deploy --clean

# Or use the deployment script
./deploy_docs.bat
```

### Custom Domain

To use a custom domain:

1. Add a `CNAME` file to the `docs/` directory
2. Configure your domain's DNS settings
3. Update the `site_url` in `mkdocs.yml`

## 🔍 Troubleshooting

### Common Issues

**Build Fails:**
- Check for broken links in markdown files
- Ensure all referenced files exist
- Validate `mkdocs.yml` syntax

**Missing Dependencies:**
```bash
pip install -r docs/requirements.txt
```

**Slow Build:**
- Disable git plugin for faster builds during development
- Use `mkdocs serve --dev-addr=127.0.0.1:8000` for development

### Development Tips

- Use `mkdocs serve` for live reload during development
- Check the browser console for JavaScript errors
- Validate links with `mkdocs build --strict`
- Test on mobile devices for responsive design

## 📊 Analytics

To add Google Analytics:

1. Get your GA tracking ID
2. Add to `mkdocs.yml`:
```yaml
extra:
  analytics:
    provider: google
    property: G-XXXXXXXXXX
```

## 🤝 Contributing

To contribute to the documentation:

1. Fork the repository
2. Create a new branch for your changes
3. Edit the relevant markdown files
4. Test locally with `mkdocs serve`
5. Submit a pull request

### Style Guide

- Use clear, concise language
- Include working code examples
- Add screenshots for UI elements
- Use consistent formatting
- Test all examples before submitting

---

For more information about MkDocs, visit: https://www.mkdocs.org/