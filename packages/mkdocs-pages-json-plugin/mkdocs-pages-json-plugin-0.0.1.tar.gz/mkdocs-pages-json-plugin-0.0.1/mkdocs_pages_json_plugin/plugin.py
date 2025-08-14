import json
import logging
import os
from pathlib import Path
from mkdocs.plugins import BasePlugin
from mkdocs.config import config_options
import datetime

# Create a logger for this plugin
log = logging.getLogger("mkdocs.plugins.pagesjson")

# A custom JSON encoder to handle date and datetime objects
class DateAwareJSONEncoder(json.JSONEncoder):
    """
    Custom JSONEncoder to handle date and datetime objects by converting them
    to ISO 8601 formatted strings.
    """
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        return super().default(obj)

class PagesJsonPlugin(BasePlugin):
    """
    An MkDocs plugin that generates a JSON file with page metadata.
    """

    config_scheme = (
        ("output_file", config_options.Type(str, default="pages.json")),
    )

    def on_files(self, files, config, **kwargs):
        """
        Store a reference to the documentation pages during the 'on_files' stage.
        """
        self.doc_pages = [page for page in files.documentation_pages()]
        return files

    def on_post_build(self, config, **kwargs):
        """
        Generates the pages.json file after the MkDocs build process,
        using the page data stored during the `on_files` stage.
        """
        if not hasattr(self, 'doc_pages'):
            log.warning("pagesjson: No documentation pages found. Skipping file generation.")
            return

        pages_data = []
        base_url = config.get("site_url", "")

        for page_file in self.doc_pages:
            page = page_file.page
            if page:
                page_url = os.path.join(base_url, page.url) if base_url else page.url

                # Retrieve the value for the 'reviewdate' key from the page's metadata.
                review_by_value = page.meta.get("reviewdate")

                # Append the data to the list. The custom encoder will handle date objects.
                pages_data.append({
                    "title": page.title,
                    "url": page_url,
                    "review_by": review_by_value
                })

        output_path = Path(config["site_dir"]) / self.config["output_file"]
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                # Use the custom encoder to handle date objects automatically.
                json.dump(pages_data, f, indent=2, cls=DateAwareJSONEncoder)
            log.info(f"pagesjson: Successfully created '{output_path}'.")
        except IOError as e:
            log.error(f"pagesjson: Failed to write to '{output_path}': {e}")