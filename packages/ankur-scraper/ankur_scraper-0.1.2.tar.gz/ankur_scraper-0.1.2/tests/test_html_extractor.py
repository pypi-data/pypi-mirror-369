from core.html_extractor import extract_text_sections

def test_extracts_sections_with_titles():
    html = """
        <html><body>
        <h2>About Us</h2>
        <p>We are a technology company solving problems with AI.</p>
        <h2>Services</h2>
        <p>We offer NLP, Computer Vision, and more.</p>
        </body></html>
    """
    sections = extract_text_sections(html)
    assert isinstance(sections, list)
    assert len(sections) >= 2
    assert all(isinstance(s, tuple) for s in sections)
    assert any("About Us" in s[0] for s in sections)
