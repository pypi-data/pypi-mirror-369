import re
import xml.etree.ElementTree as etree

from markdown.blockprocessors import BlockProcessor
from markdown.extensions import Extension

from . import utils


class CaptionedFigureProcessor(BlockProcessor):

    START_PATTERN = re.compile(r"^\\begin{captioned_figure}", flags=re.MULTILINE)
    END_PATTERN = re.compile(r"^\\end{captioned_figure}", flags=re.MULTILINE)
    CAPTION_START_PATTERN = re.compile(r"^\\begin{caption}", flags=re.MULTILINE)
    CAPTION_END_PATTERN = re.compile(r"^\\end{caption}", flags=re.MULTILINE)

    def __init__(self, *args, html_class: str, caption_html_class: str, **kwargs):
        super().__init__(*args, **kwargs)
        self.html_class = html_class
        self.caption_html_class = caption_html_class

    def test(self, parent, block):
        return self.START_PATTERN.match(block)

    def run(self, parent, blocks):
        org_blocks = list(blocks)

        # remove figure starting delim
        blocks[0] = self.START_PATTERN.sub("", blocks[0])

        # find and remove caption starting delim
        caption_start_i = None
        for i, block in enumerate(blocks):
            if self.CAPTION_START_PATTERN.match(block):
                # remove ending delim and note which block captions started on
                # (as caption content itself is an unknown number of blocks)
                caption_start_i = i
                blocks[i] = self.CAPTION_START_PATTERN.sub("", block)
                break

        # if no starting delim for caption, restore and do nothing
        if caption_start_i is None:
            # `blocks = org_blocks` doesn't work since lists are passed by pointer in Python (value of reference)
            # so changing the address of `blocks` only updates the local copy of it (the pointer)
            # we need to change the values pointed to by `blocks` (its list elements)
            blocks.clear()
            blocks.extend(org_blocks)
            return False

        # find and remove caption ending delim, and extract element
        # start search at caption starting delim; caption is at end so this is a good optimization
        delim_found = False
        for i, block in enumerate(blocks[caption_start_i:], start=caption_start_i):
            if self.CAPTION_END_PATTERN.search(block):
                delim_found = True
                # remove ending delim
                blocks[i] = self.CAPTION_END_PATTERN.sub("", block)
                # build HTML for caption
                caption_elem = etree.Element("figcaption")
                if self.caption_html_class != "":
                    caption_elem.set("class", self.caption_html_class)
                blocks[i] = blocks[i].rstrip() # remove trailing whitespace from the newline into `\end{}`
                self.parser.parseBlocks(caption_elem, blocks[caption_start_i:i + 1])
                # remove used blocks
                for _ in range(caption_start_i, i + 1):
                    blocks.pop(caption_start_i)
                break
        # if no ending delim for caption, restore and do nothing
        if not delim_found:
            blocks.clear()
            blocks.extend(org_blocks)
            return False

        # find and remove figure ending delim, and extract element
        delim_found = False
        for i, block in enumerate(blocks):
            if self.END_PATTERN.search(block):
                delim_found = True
                # remove ending delim
                blocks[i] = self.END_PATTERN.sub("", block)
                # build HTML for figure
                figure_elem = etree.SubElement(parent, "figure")
                if self.html_class != "":
                    figure_elem.set("class", self.html_class)
                self.parser.parseBlocks(figure_elem, blocks[:i + 1])
                figure_elem.append(caption_elem) # make sure caption comes at the end, and inside `figure_elem`
                # remove used blocks
                for _ in range(i + 1):
                    blocks.pop(0)
                break
        # if no ending delim for figure, restore and do nothing
        if not delim_found:
            blocks.clear()
            blocks.extend(org_blocks)
            return False
        return True


class CaptionedFigureExtension(Extension):
    r"""
    Any chunk of content, such as an image, with a caption underneath.

    Usage:
        .. code-block:: py

            import markdown
            from markdown_environments import CaptionedFigureExtension

            input_text = ...
            output_text = markdown.markdown(input_text, extensions=[
                CaptionedFigureExtension(html_class="never", caption_html_class="gonna")
            ])

    Markdown usage:
        .. code-block:: md

            \begin{captioned_figure}
            <figure content>

            \begin{caption}
            <caption>
            \end{caption}

            \end{captioned_figure}

        becomes…

        .. code-block:: html

            <figure class="[html_class]">
              [figure content]
              <figcaption class="[caption_html_class]">
                [caption]
              </figcaption>
            </figure>

    Note:
        The `caption` block can be placed anywhere within the `captioned_figure` block, as long as, of course, there are
        blank lines before and after the `caption` block.
    """

    def __init__(self, **kwargs):
        """
        Initialize captioned figure extension, with configuration options passed as the following keyword arguments:

            - **html_class** (*str*) -- HTML `class` attribute to add to figures (default: `""`).
            - **caption_html_class** (*str*) -- HTML `class` attribute to add to captions (default: `""`).
        """

        self.config = {
            "html_class": [
                "",
                "HTML `class` attribute to add to captioned figure (default: `\"\"`)."
            ],
            "caption_html_class": [
                "",
                "HTML `class` attribute to add to captioned figure's caption (default: `\"\"`)."
            ]
        }
        utils.init_extension_with_configs(self, **kwargs)

    def extendMarkdown(self, md):
        md.parser.blockprocessors.register(
            CaptionedFigureProcessor(md.parser, **self.getConfigs()), "captioned_figure", 105
        )


def makeExtension(**kwargs):
    return CaptionedFigureExtension(**kwargs)
