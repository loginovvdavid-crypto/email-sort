import pytest
from pathlib import Path
from src.email_reader import EmailReader, Email

@pytest.fixture
def reader():
    return EmailReader()

@pytest.fixture
def tmp_email(tmp_path):
    def _make(content: str, filename: str = "mail_test.txt") -> Path:
        p = tmp_path / filename
        p.write_text(content, encoding="utf-8")
        return p
    return _make

def test_reads_subject_and_sender(reader, tmp_email):
    path = tmp_email("Subject: Тест письма\nFrom: user@example.com\n\nТело письма")
    email = reader.read(path)
    assert email.subject == "Тест письма"
    assert email.sender == "user@example.com"

def test_reads_russian_headers(reader, tmp_email):
    path = tmp_email("Тема: Привет\nОт кого: Иван <ivan@corp.ru>\n\nТекст")
    email = reader.read(path)
    assert email.subject == "Привет"
    assert "Иван" in email.sender

def test_empty_file_sets_parse_error(reader, tmp_email):
    path = tmp_email("")
    email = reader.read(path)
    assert email.parse_error is True

def test_missing_subject_returns_empty_string(reader, tmp_email):
    path = tmp_email("From: someone@example.com\n\nТело без темы")
    email = reader.read(path)
    assert email.subject == ""
    assert email.parse_error is False

def test_reads_attachment(reader, tmp_email):
    path = tmp_email("Subject: Тест\nFrom: a@b.com\nПрикрепил: file.pdf\n\nТекст")
    email = reader.read(path)
    assert "file.pdf" in email.attachments

def test_nonexistent_file_sets_parse_error(reader, tmp_path):
    email = reader.read(tmp_path / "does_not_exist.txt")
    assert email.parse_error is True

def test_reads_body_correctly(reader, tmp_email):
    path = tmp_email("Subject: Тест\nFrom: a@b.com\n\nПривет!\nКак дела?")
    email = reader.read(path)
    assert "Привет" in email.body