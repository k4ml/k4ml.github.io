#!/usr/bin/env python3
# /// script
# dependencies = [
#     "PyYAML>=6.0",
#     "markdown>=3.0",
#     "pygments>=2.0"
# ]
# ///

"""
Python static site generator compatible with Jekyll structure
Usage: uv run ssg.py [input_dir] [output_dir]
"""

import os
import re
import sys
import json
import yaml
import shutil
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

try:
    import markdown
    from markdown.extensions import codehilite, toc
except ImportError:
    print("Error: markdown package required. Run: uv run ssg.py")
    sys.exit(1)


class JekyllSSG:
    def __init__(self, source_dir: str = ".", output_dir: str = "_site"):
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        self.config = self.load_config()
        self.posts = []
        self.pages = []
        self.collections = {}

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from _config.yml"""
        config_file = self.source_dir / "_config.yml"
        if config_file.exists():
            with open(config_file, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        return {}

    def parse_frontmatter(self, content: str) -> tuple[Dict[str, Any], str]:
        """Parse YAML frontmatter from content"""
        if content.startswith("---\n") or content.startswith("---\r\n"):
            try:
                # Handle both \n and \r\n line endings
                lines = content.split("\n")

                # Find the closing ---
                end_line = None
                for i in range(1, len(lines)):
                    if lines[i].strip() == "---":
                        end_line = i
                        break

                if end_line:
                    frontmatter_lines = lines[1:end_line]
                    content_lines = lines[end_line + 1 :]

                    frontmatter_str = "\n".join(frontmatter_lines)
                    content_body = "\n".join(content_lines)

                    # Handle empty frontmatter
                    if frontmatter_str.strip():
                        frontmatter = yaml.safe_load(frontmatter_str) or {}
                    else:
                        frontmatter = {}

                    return frontmatter, content_body
            except yaml.YAMLError:
                pass
        return {}, content

    def render_template(self, template_path: Path, context: Dict[str, Any]) -> str:
        """Simple template rendering with Jekyll-like variables"""
        if not template_path.exists():
            return context.get("content", "")

        with open(template_path, "r", encoding="utf-8") as f:
            template = f.read()

        # Process includes first
        template = self.process_includes(template)

        # Process conditionals
        template = self.process_conditionals(template, context)

        # Replace Jekyll template variables
        template = template.replace("{{ site.name }}", self.config.get("name", ""))
        template = template.replace(
            "{{ site.description }}", self.config.get("description", "")
        )
        template = template.replace("{{ site.avatar }}", self.config.get("avatar", ""))
        template = template.replace(
            "{{ site.baseurl }}", self.config.get("baseurl", "")
        )
        template = template.replace("{{ content }}", context.get("content", ""))
        template = template.replace("{{ page.title }}", context.get("title", ""))
        template = template.replace("{{ page.date }}", context.get("date", ""))

        return template

    def process_includes(self, template: str) -> str:
        """Process {% include %} tags"""
        import re

        def replace_include(match):
            include_file = match.group(1)
            include_path = self.source_dir / "_includes" / include_file
            if include_path.exists():
                with open(include_path, "r", encoding="utf-8") as f:
                    return f.read()
            return ""

        return re.sub(r"{%\s*include\s+([^%]+)\s*%}", replace_include, template)

    def process_conditionals(self, template: str, context: Dict[str, Any]) -> str:
        """Process simple {% if %} conditionals"""
        import re

        def replace_conditional(match):
            condition = match.group(1).strip()
            content = match.group(2)

            # Simple condition evaluation
            if condition == "page.title":
                if context.get("title"):
                    return content
            elif condition == "site.google_analytics":
                if self.config.get("google_analytics"):
                    return content

            return ""

        # Pattern for {% if condition %}...{% endif %}
        pattern = r"{%\s*if\s+([^%]+)\s*%}(.*?){%\s*endif\s*%}"
        return re.sub(pattern, replace_conditional, template, flags=re.DOTALL)

    def process_markdown(self, file_path: Path) -> Dict[str, Any]:
        """Process markdown file with frontmatter"""
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        frontmatter, content_body = self.parse_frontmatter(content)

        # Convert markdown to HTML
        md = markdown.Markdown(
            extensions=["codehilite", "toc", "fenced_code", "tables"],
            extension_configs={
                "codehilite": {"css_class": "highlight", "use_pygments": True}
            },
        )
        html_content = md.convert(content_body)

        return {
            "frontmatter": frontmatter,
            "content": html_content,
            "toc": getattr(md, "toc", ""),
            "toc_tokens": getattr(md, "toc_tokens", []),
        }

    def process_html(self, file_path: Path) -> Dict[str, Any]:
        """Process HTML file with frontmatter"""
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        frontmatter, content_body = self.parse_frontmatter(content)

        return {"frontmatter": frontmatter, "content": content_body}

    def process_posts(self):
        """Process all posts in _posts directory"""
        posts_dir = self.source_dir / "_posts"
        if not posts_dir.exists():
            return

        for file_path in posts_dir.glob("*.md"):
            post_data = self.process_markdown(file_path)
            frontmatter = post_data["frontmatter"]

            # Extract date from filename if not in frontmatter
            if "date" not in frontmatter:
                date_match = re.match(r"(\d{4}-\d{2}-\d{2})-", file_path.name)
                if date_match:
                    frontmatter["date"] = datetime.strptime(
                        date_match.group(1), "%Y-%m-%d"
                    )

            # Set title from filename if not in frontmatter
            if "title" not in frontmatter:
                title = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", file_path.stem)
                frontmatter["title"] = title.replace("-", " ").title()

            post = {
                "filename": file_path.stem,
                "url": self.generate_permalink(frontmatter, file_path),
                **post_data,
                **frontmatter,
            }

            self.posts.append(post)

        # Sort posts by date
        self.posts.sort(key=lambda x: x.get("date", datetime.now()), reverse=True)

    def process_pages(self):
        """Process all pages (HTML files with frontmatter)"""
        processed_stems = set()

        for file_path in self.source_dir.glob("*.html"):
            if file_path.name.startswith("_"):
                continue

            page_data = self.process_html(file_path)
            frontmatter = page_data["frontmatter"]

            # Use permalink from frontmatter or generate directory-style URL
            if "permalink" in frontmatter:
                url = frontmatter["permalink"]
                # If permalink ends with /, make it a directory with index.html
                if url.endswith("/"):
                    url = url + "index.html"
            elif file_path.stem == "index":
                url = "/index.html"
            else:
                # Create directory-style URL: /page-name/
                url = f"/{file_path.stem}/index.html"

            page = {
                "filename": file_path.stem,
                "url": url,
                **page_data,
                **frontmatter,
            }

            self.pages.append(page)
            processed_stems.add(file_path.stem)

        # Process markdown pages (skip if HTML version exists)
        for file_path in self.source_dir.glob("*.md"):
            if file_path.name.startswith("_"):
                continue

            # Skip if we already processed an HTML file with the same name
            if file_path.stem in processed_stems:
                continue

            page_data = self.process_markdown(file_path)
            frontmatter = page_data["frontmatter"]

            # Use permalink from frontmatter or generate directory-style URL
            if "permalink" in frontmatter:
                url = frontmatter["permalink"]
                # If permalink ends with /, make it a directory with index.html
                if url.endswith("/"):
                    url = url + "index.html"
            else:
                # Create directory-style URL: /page-name/
                url = f"/{file_path.stem}/index.html"

            page = {
                "filename": file_path.stem,
                "url": url,
                **page_data,
                **frontmatter,
            }

            self.pages.append(page)
            processed_stems.add(file_path.stem)

    def process_collections(self):
        """Process Jekyll collections"""
        collections_config = self.config.get("collections", {})

        for collection_name, collection_config in collections_config.items():
            if not isinstance(collection_config, dict):
                collection_config = {}

            collection_dir = self.source_dir / f"_{collection_name}"
            if not collection_dir.exists():
                continue

            self.collections[collection_name] = []

            for file_path in collection_dir.glob("*.md"):
                item_data = self.process_markdown(file_path)
                frontmatter = item_data["frontmatter"]

                item = {
                    "filename": file_path.stem,
                    "url": f"/{collection_name}/{file_path.stem}.html",
                    **item_data,
                    **frontmatter,
                }

                self.collections[collection_name].append(item)

            # Sort collection items
            self.collections[collection_name].sort(
                key=lambda x: x.get("date", datetime.now()), reverse=True
            )

    def generate_permalink(self, frontmatter: Dict[str, Any], file_path: Path) -> str:
        """Generate URL based on permalink configuration"""
        permalink_style = self.config.get(
            "permalink", "/:categories/:year/:month/:day/:title/"
        )

        # Extract date info
        date_val = frontmatter.get("date", "")
        if isinstance(date_val, datetime):
            date_obj = date_val
        elif isinstance(date_val, str):
            try:
                date_obj = datetime.strptime(date_val, "%Y-%m-%d")
            except ValueError:
                date_obj = datetime.now()
        else:
            date_obj = datetime.now()

        year, month, day = (
            str(date_obj.year),
            f"{date_obj.month:02d}",
            f"{date_obj.day:02d}",
        )

        # Extract title from filename
        title = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", file_path.stem)

        # Replace placeholders
        url = permalink_style
        url = url.replace(":title", title)
        url = url.replace(":year", year)
        url = url.replace(":month", month)
        url = url.replace(":day", day)
        url = url.replace(":categories", "")  # Simplified

        # If URL ends with /, make it a directory with index.html
        if url.endswith("/"):
            url = url + "index.html"

        return url

    def render_page(self, page_data: Dict[str, Any]) -> str:
        """Render a complete page with layout"""
        content = page_data["content"]
        current_layout = page_data.get("layout", "default")

        context = {
            "page": page_data,
            "site": self.config,
            "title": page_data.get("title", ""),
            "date": str(page_data.get("date", "")),
        }

        # Process loops and variables in the content first
        content = self.process_loops(content, context)
        content = self.process_conditionals(content, context)

        # Process layout chain
        while current_layout:
            layout_path = self.source_dir / "_layouts" / f"{current_layout}.html"
            if not layout_path.exists():
                break

            # Read and parse layout file
            with open(layout_path, "r", encoding="utf-8") as f:
                layout_content = f.read()

            # Check for layout frontmatter
            layout_frontmatter = {}
            if layout_content.startswith("---\n"):
                try:
                    end_index = layout_content.find("\n---\n", 4)
                    if end_index != -1:
                        frontmatter_str = layout_content[4:end_index]
                        layout_frontmatter = yaml.safe_load(frontmatter_str) or {}
                        layout_content = layout_content[end_index + 5 :]
                except yaml.YAMLError:
                    pass

            # Render current layout with content
            context["content"] = content
            content = self.render_template_string(layout_content, context)

            # Move to parent layout if exists
            current_layout = layout_frontmatter.get("layout")

        return content

    def render_template_string(self, template: str, context: Dict[str, Any]) -> str:
        """Render a template string"""
        # Process includes
        template = self.process_includes(template)

        # Process loops
        template = self.process_loops(template, context)

        # Process conditionals
        template = self.process_conditionals(template, context)

        # Replace variables
        template = template.replace("{{ site.name }}", self.config.get("name", ""))
        template = template.replace(
            "{{ site.description }}", self.config.get("description", "")
        )
        template = template.replace("{{ site.avatar }}", self.config.get("avatar", ""))
        template = template.replace(
            "{{ site.baseurl }}", self.config.get("baseurl", "")
        )
        template = template.replace("{{ content }}", context.get("content", ""))
        template = template.replace("{{ page.title }}", context.get("title", ""))
        template = template.replace("{{ page.date }}", context.get("date", ""))

        return template

    def process_loops(self, template: str, context: Dict[str, Any]) -> str:
        """Process {% for %} loops"""
        import re

        def replace_loop(match):
            loop_var = match.group(1).strip()
            collection_expr = match.group(2).strip()
            loop_body = match.group(3)

            # Handle site.posts
            if collection_expr == "site.posts":
                output = []
                for post in self.posts:
                    # Replace loop variables in the body
                    rendered_body = loop_body

                    # Replace site variables first
                    rendered_body = rendered_body.replace(
                        "{{ site.baseurl }}", self.config.get("baseurl", "")
                    )
                    rendered_body = rendered_body.replace(
                        "{{ site.name }}", self.config.get("name", "")
                    )

                    # Get clean URL (without index.html for display)
                    post_url = post.get("url", "")
                    if post_url.endswith("/index.html"):
                        post_url = post_url[:-10]  # Remove "index.html"

                    # Replace post variables
                    rendered_body = rendered_body.replace(
                        f"{{{{ {loop_var}.title }}}}", post.get("title", "")
                    )
                    rendered_body = rendered_body.replace(
                        f"{{{{ {loop_var}.url }}}}", post_url
                    )
                    rendered_body = rendered_body.replace(
                        f"{{{{ {loop_var}.date }}}}", str(post.get("date", ""))
                    )
                    rendered_body = rendered_body.replace(
                        f"{{{{ {loop_var}.excerpt }}}}",
                        post.get("content", "")[:200] + "...",
                    )
                    # Also handle without spaces around variable
                    rendered_body = rendered_body.replace(
                        f"{{{{{loop_var}.title}}}}", post.get("title", "")
                    )
                    rendered_body = rendered_body.replace(
                        f"{{{{{loop_var}.url}}}}", post_url
                    )
                    rendered_body = rendered_body.replace(
                        f"{{{{{loop_var}.date}}}}", str(post.get("date", ""))
                    )
                    rendered_body = rendered_body.replace(
                        f"{{{{{loop_var}.excerpt}}}}",
                        post.get("content", "")[:200] + "...",
                    )

                    output.append(rendered_body)
                return "".join(output)

            return match.group(0)  # Return unchanged if not recognized

        # Pattern for {% for var in collection %}...{% endfor %}
        pattern = r"{%\s*for\s+(\w+)\s+in\s+([^%]+)\s*%}(.*?){%\s*endfor\s*%}"
        return re.sub(pattern, replace_loop, template, flags=re.DOTALL)

    def process_scss_files(self):
        """Process SCSS files with frontmatter and convert to CSS"""
        for scss_file in self.source_dir.glob("*.scss"):
            with open(scss_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Check if it has frontmatter
            if not content.startswith("---\n"):
                continue

            frontmatter, scss_content = self.parse_frontmatter(content)

            # Remove any leading whitespace from the SCSS content
            scss_content = scss_content.lstrip()

            # Simple SCSS processing - expand @import statements
            css_content = self.process_scss_imports(scss_content)

            # Output as .css file
            output_path = self.output_dir / scss_file.stem
            output_path = output_path.with_suffix(".css")

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(css_content)
            print(f"Generated: {output_path}")

    def process_scss_imports(self, scss_content: str) -> str:
        """Process @import statements in SCSS"""
        import re

        def replace_import(match):
            import_file = match.group(1).strip("\"'")
            # Look in _sass directory
            sass_path = self.source_dir / "_sass" / f"_{import_file}.scss"
            if sass_path.exists():
                with open(sass_path, "r", encoding="utf-8") as f:
                    return f.read()
            return f"/* Import not found: {import_file} */"

        # Replace @import statements
        return re.sub(r'@import\s+["\']([^"\']+)["\'];?', replace_import, scss_content)

    def generate_site(self):
        """Generate the complete static site"""
        print(f"Building site from {self.source_dir} to {self.output_dir}")

        # Clean output directory
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)
        self.output_dir.mkdir(parents=True)

        # Process content
        self.process_posts()
        self.process_pages()
        self.process_collections()

        # Process SCSS files
        self.process_scss_files()

        # Copy static files
        self.copy_static_files()

        # Generate posts
        for post in self.posts:
            html = self.render_page(post)
            output_path = self.output_dir / post["url"].lstrip("/")
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"Generated: {output_path}")

        # Generate pages
        for page in self.pages:
            html = self.render_page(page)
            output_path = self.output_dir / page["url"].lstrip("/")

            # Create parent directories if needed
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"Generated: {output_path}")

        # Generate collections
        for collection_name, items in self.collections.items():
            collection_dir = self.output_dir / collection_name
            collection_dir.mkdir(exist_ok=True)

            # Generate individual collection items
            for item in items:
                html = self.render_page(item)
                output_path = self.output_dir / item["url"].lstrip("/")
                output_path.parent.mkdir(parents=True, exist_ok=True)

                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(html)
                print(f"Generated: {output_path}")

            # Generate collection index if needed
            if (
                self.config.get("collections", {})
                .get(collection_name, {})
                .get("output", True)
            ):
                self.generate_collection_index(collection_name, items)

        # Generate index page if not exists
        if not any(page["url"] == "/index.html" for page in self.pages):
            self.generate_index()

        print(f"Site generated successfully in {self.output_dir}")

    def copy_static_files(self):
        """Copy static files to output directory"""
        static_extensions = {
            ".css",
            ".js",
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".svg",
            ".ico",
            ".txt",
            ".xml",
        }

        for item in self.source_dir.rglob("*"):
            if item.is_file() and item.suffix.lower() in static_extensions:
                if not any(part.startswith("_") for part in item.parts):
                    relative_path = item.relative_to(self.source_dir)
                    output_path = self.output_dir / relative_path
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, output_path)

    def generate_index(self):
        """Generate main index page with posts list"""
        index_content = "<h1>Latest Posts</h1>\n"

        for post in self.posts[:10]:  # Show latest 10 posts
            index_content += f"""
            <article class="post">
                <h2><a href="{post["url"]}">{post.get("title", "Untitled")}</a></h2>
                <div class="date">{post.get("date", "")}</div>
                <div class="excerpt">
                    {post.get("content", "")[:200]}...
                </div>
            </article>
            """

        page_data = {"title": "Home", "content": index_content, "layout": "default"}

        html = self.render_page(page_data)
        output_path = self.output_dir / "index.html"

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Generated: {output_path}")

    def generate_collection_index(
        self, collection_name: str, items: List[Dict[str, Any]]
    ):
        """Generate index page for a collection"""
        index_content = f"<h1>{collection_name.title()}</h1>\n"

        for item in items:
            index_content += f"""
            <article class="post">
                <h2><a href="{item["url"]}">{item.get("title", "Untitled")}</a></h2>
                <div class="date">{item.get("date", "")}</div>
            </article>
            """

        page_data = {
            "title": collection_name.title(),
            "content": index_content,
            "layout": "default",
        }

        html = self.render_page(page_data)
        output_path = self.output_dir / collection_name / "index.html"

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Generated: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Python Jekyll-compatible static site generator"
    )
    parser.add_argument(
        "source", nargs="?", default=".", help="Source directory (default: current)"
    )
    parser.add_argument(
        "output", nargs="?", default="_site", help="Output directory (default: _site)"
    )
    parser.add_argument("--serve", action="store_true", help="Serve the generated site")
    parser.add_argument(
        "--port", type=int, default=8000, help="Port for development server"
    )

    args = parser.parse_args()

    ssg = JekyllSSG(args.source, args.output)
    ssg.generate_site()

    if args.serve:
        try:
            import http.server
            import socketserver

            os.chdir(args.output)
            with socketserver.TCPServer(
                ("", args.port), http.server.SimpleHTTPRequestHandler
            ) as httpd:
                print(f"Serving at http://localhost:{args.port}")
                httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped")


if __name__ == "__main__":
    main()
