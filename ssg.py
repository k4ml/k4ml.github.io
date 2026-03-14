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
            include_file = match.group(1).strip()
            include_path = self.source_dir / "_includes" / include_file
            if include_path.exists():
                with open(include_path, "r", encoding="utf-8") as f:
                    included_content = f.read()
                # Recursively process includes within includes
                included_content = self.process_includes(included_content)
                return included_content
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
                    # Process variables in the content before returning
                    content = self.replace_variables_in_text(content, context)
                    return content
            elif condition == "page.excerpt":
                page_data = context.get("page", {})
                if page_data.get("content"):
                    # Process variables in the content
                    content = self.replace_variables_in_text(content, context)
                    return content
            elif condition == "site.google_analytics":
                if self.config.get("google_analytics"):
                    content = self.replace_variables_in_text(content, context)
                    return content

            return ""

        # Pattern for {% if condition %}...{% endif %}
        # Handle {% else %} as well
        pattern = r"{%\s*if\s+([^%]+)\s*%}(.*?)(?:{%\s*else\s*%}(.*?))?{%\s*endif\s*%}"

        def replace_with_else(match):
            condition = match.group(1).strip()
            if_content = match.group(2)
            else_content = match.group(3) if match.group(3) else ""

            # Evaluate condition
            result = False
            if condition == "page.title":
                result = bool(context.get("title"))
            elif condition == "page.excerpt":
                page_data = context.get("page", {})
                result = bool(page_data.get("content"))
            elif condition == "site.google_analytics":
                result = bool(self.config.get("google_analytics"))

            # Return appropriate content
            content = if_content if result else else_content
            return self.replace_variables_in_text(content, context)

        return re.sub(pattern, replace_with_else, template, flags=re.DOTALL)

    def replace_variables_in_text(self, text: str, context: Dict[str, Any]) -> str:
        """Replace variables in text"""
        page_data = context.get("page", {})

        # Handle {{ page.excerpt | strip_html }}
        excerpt = page_data.get("content", "")[:200]
        # Simple strip_html - remove HTML tags
        import re

        excerpt = re.sub(r"<[^>]+>", "", excerpt)
        text = re.sub(r"{{\s*page\.excerpt\s*\|\s*strip_html\s*}}", excerpt, text)

        # Replace simple variables
        text = text.replace("{{ page.title }}", context.get("title", ""))
        text = text.replace("{{ site.name }}", self.config.get("name", ""))
        text = text.replace(
            "{{ site.description }}", self.config.get("description", "")
        )

        return text

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
                # Match YYYY-M-D or YYYY-MM-DD format
                date_match = re.match(r"(\d{4})-(\d{1,2})-(\d{1,2})-", file_path.name)
                if date_match:
                    year, month, day = date_match.groups()
                    # Pad month and day to 2 digits for parsing
                    date_str = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                    frontmatter["date"] = datetime.strptime(date_str, "%Y-%m-%d")

            # Set title from filename if not in frontmatter
            if "title" not in frontmatter:
                # Remove date prefix (handles both YYYY-MM-DD and YYYY-M-D)
                title = re.sub(r"^\d{4}-\d{1,2}-\d{1,2}-", "", file_path.stem)
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

        # Extract title from filename (handle both YYYY-MM-DD and YYYY-M-D)
        title = re.sub(r"^\d{4}-\d{1,2}-\d{1,2}-", "", file_path.stem)

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
            "date": page_data.get("date", ""),  # Keep as datetime object
        }

        # Process loops and variables in the content first
        content = self.process_loops(content, context)
        content = self.process_conditionals(content, context)
        # Also replace site variables in content (like site.baseurl in images)
        content = content.replace("{{ site.baseurl }}", self.config.get("baseurl", ""))

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

        # Process filters first (like date formatting) before simple replacements
        template = self.process_filters(template, context)

        # Replace page.date without filter (fallback)
        page_date = context.get("date", "")
        if isinstance(page_date, datetime):
            page_date = page_date.strftime("%Y-%m-%d")
        template = template.replace("{{ page.date }}", str(page_date))

        return template

    def process_filters(self, template: str, context: Dict[str, Any]) -> str:
        """Process Liquid filters like {{ variable | filter: args }}"""
        import re
        from datetime import datetime

        def format_date(match):
            var_name = match.group(1).strip()
            date_format = match.group(2).strip().strip("\"'")

            # Get the date value
            date_val = None
            if var_name == "page.date":
                date_val = context.get("date")

            if not date_val:
                return ""

            # Convert to datetime if it's a string
            if isinstance(date_val, str):
                try:
                    date_val = datetime.strptime(date_val, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    try:
                        date_val = datetime.fromisoformat(date_val.replace(" ", "T"))
                    except:
                        return ""

            if not isinstance(date_val, datetime):
                return ""

            # Format the date
            # Convert Jekyll/Liquid format to Python strftime format
            python_format = date_format
            python_format = python_format.replace(
                "%e", "%d"
            )  # Day of month (no leading zero)

            formatted = date_val.strftime(python_format)
            # Remove leading zero from day if %e was used
            if "%e" in date_format:
                formatted = formatted.replace(" 0", " ")

            return formatted

        # Pattern for {{ variable | date: "format" }}
        # Use [^}|] to ensure we don't match across }} boundaries
        pattern = r'{{\s*([^}|]+)\s*\|\s*date:\s*["\']([^"\']+)["\']\s*}}'
        return re.sub(pattern, format_date, template)

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
        """Process @import statements in SCSS and replace variables"""
        import re

        # First, collect all variables and mixins from imported files
        variables = {}
        mixins = {}

        def collect_variables(content: str):
            """Collect SCSS variables from content"""
            var_pattern = r"\$([a-zA-Z0-9_-]+)\s*:\s*([^;]+);"
            for match in re.finditer(var_pattern, content):
                var_name = match.group(1)
                var_value = match.group(2).strip()
                variables[var_name] = var_value

        def collect_mixins(content: str):
            """Collect SCSS mixins from content"""
            # Pattern: @mixin name { @media ... { @content; } }
            mixin_pattern = r"@mixin\s+([a-zA-Z0-9_-]+)\s*{([^}]*@media[^}]+{[^}]*@content;[^}]*}[^}]*)}"
            for match in re.finditer(mixin_pattern, content, re.DOTALL):
                mixin_name = match.group(1)
                mixin_body = match.group(2).strip()
                mixins[mixin_name] = mixin_body

        def replace_import(match):
            import_file = match.group(1).strip("\"'")
            # Look in _sass directory
            sass_path = self.source_dir / "_sass" / f"_{import_file}.scss"
            if sass_path.exists():
                with open(sass_path, "r", encoding="utf-8") as f:
                    imported_content = f.read()
                # Collect variables and mixins from this import
                collect_variables(imported_content)
                collect_mixins(imported_content)
                return imported_content
            return f"/* Import not found: {import_file} */"

        # Replace @import statements and collect variables/mixins
        scss_content = re.sub(
            r'@import\s+["\']([^"\']+)["\'];?', replace_import, scss_content
        )

        # Collect variables from main content too
        collect_variables(scss_content)
        collect_mixins(scss_content)

        # Now replace all variable references with their values
        # Handle nested variables (variables that reference other variables)
        max_iterations = 10
        for _ in range(max_iterations):
            changed = False
            for var_name, var_value in list(variables.items()):
                # Check if this variable value contains other variables
                var_refs = re.findall(r"\$([a-zA-Z0-9_-]+)", var_value)
                if var_refs:
                    # Replace variable references in the value
                    for ref in var_refs:
                        if ref in variables and ref != var_name:
                            old_value = var_value
                            var_value = var_value.replace(f"${ref}", variables[ref])
                            if var_value != old_value:
                                changed = True
                    variables[var_name] = var_value
            if not changed:
                break

        # Replace all variable usages in the content
        def replace_variable(match):
            var_name = match.group(1)
            return variables.get(var_name, match.group(0))

        scss_content = re.sub(r"\$([a-zA-Z0-9_-]+)", replace_variable, scss_content)

        # Process nesting - convert & references to parent selector
        def expand_nested_rules(content):
            """Expand nested SCSS rules to flat CSS"""
            lines = content.split("\n")
            result = []
            selector_stack = []
            brace_count = 0
            current_selector = ""
            current_block = []

            for line in lines:
                stripped = line.strip()

                # Count braces to track nesting level
                open_braces = line.count("{")
                close_braces = line.count("}")

                # Check if this is a selector line (ends with { and doesn't start with @media)
                if (
                    "{" in line
                    and not stripped.startswith("@media")
                    and not stripped.startswith("@include")
                ):
                    selector = line.split("{")[0].strip()

                    if brace_count > 0:
                        # We're nested - need to expand &
                        if "&" in selector:
                            # Replace & with parent selector
                            parent = selector_stack[-1] if selector_stack else ""
                            selector = selector.replace("&", parent)
                        else:
                            # Descendant selector
                            parent = selector_stack[-1] if selector_stack else ""
                            if parent:
                                selector = f"{parent} {selector}"

                    selector_stack.append(selector)
                    current_selector = selector
                    brace_count += open_braces
                    result.append(f"{selector} {{")

                elif "}" in line:
                    brace_count -= close_braces
                    if selector_stack:
                        selector_stack.pop()
                    result.append(line)

                else:
                    # Regular line
                    brace_count += open_braces - close_braces
                    result.append(line)

            return "\n".join(result)

        scss_content = expand_nested_rules(scss_content)

        # Process @include statements for mixins
        def replace_include(match):
            mixin_name = match.group(1).strip()
            include_content = match.group(2) if match.lastindex >= 2 else ""

            if mixin_name in mixins:
                mixin_body = mixins[mixin_name]
                # Replace @content with the actual content
                result = mixin_body.replace("@content;", include_content.strip())
                return result
            return f"/* Mixin not found: {mixin_name} */"

        # Pattern: @include mixin-name { content }
        scss_content = re.sub(
            r"@include\s+([a-zA-Z0-9_-]+)\s*{([^}]*)}",
            replace_include,
            scss_content,
            flags=re.DOTALL,
        )

        # Remove mixin declarations
        scss_content = re.sub(
            r"@mixin\s+[a-zA-Z0-9_-]+\s*{[^}]*@media[^}]+{[^}]*@content;[^}]*}[^}]*}",
            "",
            scss_content,
            flags=re.DOTALL,
        )

        # Remove variable declarations (lines starting with $variable: value;)
        scss_content = re.sub(
            r"^\s*\$[a-zA-Z0-9_-]+\s*:[^;]+;\s*$", "", scss_content, flags=re.MULTILINE
        )

        # Remove SCSS comments (// ...)
        scss_content = re.sub(r"//.*$", "", scss_content, flags=re.MULTILINE)

        return scss_content

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
