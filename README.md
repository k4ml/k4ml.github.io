# Python Static Site Generator (Jekyll-Compatible)

A single-file static site generator written in Python that's compatible with Jekyll's structure. Uses only standard library plus a few dependencies managed via PEP 723.

## Features

- **Jekyll-compatible structure**: Works with existing Jekyll sites
  - `_config.yml` configuration
  - `_layouts/` for templates
  - `_posts/` for blog posts
  - `_includes/` for reusable components
  - Collections support (e.g., `_qna/`)
- **Markdown processing**: Full GFM support with syntax highlighting
- **Frontmatter parsing**: YAML frontmatter in both Markdown and HTML files
- **Layout inheritance**: Supports nested layouts (e.g., post → default)
- **Template variables**: Jekyll-style `{{ site.* }}` and `{{ page.* }}` variables
- **Includes**: `{% include file.html %}` support
- **Conditionals**: Basic `{% if %}` statements
- **Permalink generation**: Configurable URL patterns
- **Development server**: Built-in HTTP server for local testing

## Requirements

- Python 3.11+
- uv (for dependency management)

## Installation

No installation needed! The script uses PEP 723 inline metadata to declare dependencies:

```bash
# Just run with uv
uv run ssg.py
```

Dependencies (automatically installed by uv):
- PyYAML >= 6.0
- markdown >= 3.0
- pygments >= 2.0

## Usage

### Basic Generation

```bash
# Generate site from current directory to _site/
uv run ssg.py

# Specify custom directories
uv run ssg.py /path/to/source /path/to/output
```

### Development Server

```bash
# Generate and serve on http://localhost:8000
uv run ssg.py --serve

# Custom port
uv run ssg.py --serve --port 3000
```

## Jekyll Structure

The generator expects this directory structure:

```
.
├── _config.yml          # Site configuration
├── _layouts/            # Layout templates
│   ├── default.html
│   └── post.html
├── _includes/           # Reusable components
│   ├── header.html
│   └── footer.html
├── _posts/              # Blog posts
│   └── 2024-01-01-title.md
├── _qna/                # Custom collection (optional)
├── index.html           # Pages
└── about.md
```

## Configuration (_config.yml)

```yaml
name: Your Site Name
description: Site description
avatar: https://example.com/avatar.jpg
baseurl: ""
permalink: /:title/

collections:
  qna:
    output: true
```

## Frontmatter

Posts and pages use YAML frontmatter:

```markdown
---
layout: post
title: My Post Title
date: 2024-01-01
tags: python, jekyll
---

Post content here...
```

## Template Syntax

### Variables

- `{{ site.name }}` - Site name from config
- `{{ site.description }}` - Site description
- `{{ site.avatar }}` - Avatar URL
- `{{ site.baseurl }}` - Base URL
- `{{ page.title }}` - Page/post title
- `{{ page.date }}` - Post date
- `{{ content }}` - Main content

### Includes

```html
{% include meta.html %}
{% include header.html %}
```

### Conditionals

```html
{% if page.title %}
  <title>{{ page.title }}</title>
{% endif %}
```

## Limitations

This is a simplified Jekyll implementation. Some features are not supported:

- Complex Liquid filters and tags
- Plugins
- Data files (_data/)
- Pagination
- RSS/Sitemap generation (copy static files instead)
- Asset pipeline (Sass, CoffeeScript, etc.)
- Draft posts

## Example

```bash
# Clone a Jekyll site
cd my-jekyll-site

# Generate the site
uv run ssg.py

# View locally
uv run ssg.py --serve

# Open browser to http://localhost:8000
```

## How It Works

1. Loads configuration from `_config.yml`
2. Processes posts from `_posts/` with date extraction from filename
3. Processes pages from root directory
4. Processes collections (e.g., `_qna/`)
5. Renders each file with its layout chain
6. Copies static files (CSS, JS, images)
7. Outputs to `_site/` directory

## Performance

The generator is designed for small to medium sites (100-1000 pages). For very large sites, consider using the official Jekyll or Hugo.

## License

This is a demonstration project. Feel free to use and modify as needed.

## Troubleshooting

### Missing dependencies
```bash
# uv automatically installs them, but if needed:
pip install PyYAML markdown pygments
```

### Layout not found
Check that layout files exist in `_layouts/` and have correct names.

### Content not rendering
Ensure files have proper frontmatter with `---` delimiters.

### Variables not replaced
Check variable syntax: `{{ variable }}` not `{variable}`.
