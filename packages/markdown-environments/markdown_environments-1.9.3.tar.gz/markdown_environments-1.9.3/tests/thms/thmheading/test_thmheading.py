import pytest

from markdown_environments import ThmsExtension
from ...tests_utils import run_extension_test


@pytest.mark.parametrize(
    "extension, filename_base",
    [
        (ThmsExtension(), "thms/thmheading/success_1"),
        (ThmsExtension(), "thms/thmheading/success_2"),
        (ThmsExtension(), "thms/thmheading/success_3"),
        (ThmsExtension(), "thms/thmheading/success_4"),
        (ThmsExtension(), "thms/thmheading/success_5"),
        (
            ThmsExtension(thm_heading_config={
                "html_id_prefix": "defenestrate-", "html_class": "bottom-text", "emph_html_class": "top-text"
            }),
            "thms/thmheading/success_6"
        ),
        (ThmsExtension(), "thms/thmheading/fail_1")
    ]
)
def test_thmheading(extension, filename_base):
    run_extension_test([extension], filename_base)
