"""Tests for Gutenberg ingestion module."""

from storywizard.ingestion.gutenberg import _strip_gutenberg_boilerplate, CANDIDATES


class TestStripBoilerplate:
    def test_strips_standard_header_footer(self):
        text = (
            "Some header stuff\n"
            "*** START OF THE PROJECT GUTENBERG EBOOK TEST ***\n"
            "Actual book content here.\n"
            "More content.\n"
            "*** END OF THE PROJECT GUTENBERG EBOOK TEST ***\n"
            "Footer stuff\n"
        )
        result = _strip_gutenberg_boilerplate(text)
        assert "Actual book content" in result
        assert "More content" in result
        assert "header stuff" not in result
        assert "Footer stuff" not in result

    def test_strips_alternate_markers(self):
        text = (
            "Preamble\n"
            "*** START OF THIS PROJECT GUTENBERG EBOOK TEST ***\n"
            "The real content.\n"
            "End of the Project Gutenberg EBook of Test\n"
            "Trailing\n"
        )
        result = _strip_gutenberg_boilerplate(text)
        assert "The real content" in result
        assert "Preamble" not in result

    def test_no_markers(self):
        text = "Just plain text with no Gutenberg markers."
        result = _strip_gutenberg_boilerplate(text)
        assert result == text

    def test_case_insensitive(self):
        text = (
            "Header\n"
            "*** start of the project gutenberg ebook test ***\n"
            "Content.\n"
            "*** end of the project gutenberg ebook test ***\n"
            "Footer\n"
        )
        result = _strip_gutenberg_boilerplate(text)
        assert "Content" in result
        assert "Header" not in result

    def test_empty_input(self):
        assert _strip_gutenberg_boilerplate("") == ""

    def test_only_start_marker(self):
        text = (
            "Header\n"
            "*** START OF THE PROJECT GUTENBERG EBOOK TEST ***\n"
            "Content goes on forever..."
        )
        result = _strip_gutenberg_boilerplate(text)
        assert "Content goes on forever" in result
        assert "Header" not in result

    def test_only_end_marker(self):
        text = (
            "Content from the beginning.\n"
            "*** END OF THE PROJECT GUTENBERG EBOOK TEST ***\n"
            "Footer"
        )
        result = _strip_gutenberg_boilerplate(text)
        assert "Content from the beginning" in result
        assert "Footer" not in result


class TestCandidates:
    def test_all_candidates_have_metadata(self):
        for book_id, meta in CANDIDATES.items():
            assert meta.title, f"Book {book_id} missing title"
            assert meta.author, f"Book {book_id} missing author"
            assert meta.gutenberg_id == book_id
            assert meta.genre, f"Book {book_id} missing genre"

    def test_expected_books_present(self):
        assert 43 in CANDIDATES  # Jekyll & Hyde
        assert 84 in CANDIDATES  # Frankenstein
        assert 11 in CANDIDATES  # Alice in Wonderland
        assert 46 in CANDIDATES  # A Christmas Carol
        assert 174 in CANDIDATES  # Dorian Gray
