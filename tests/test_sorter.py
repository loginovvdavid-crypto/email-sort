import pytest
from pathlib import Path
from src.email_reader import Email
from src.email_classifier import ClassificationResult
from src.email_sorter import EmailSorter, ALL_CATEGORIES

@pytest.fixture
def setup(tmp_path):
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    output = tmp_path / "output"
    output.mkdir()
    sorter = EmailSorter(output)
    return inbox, output, sorter

def make_email(path: Path) -> Email:
    e = Email(path=path)
    e.subject = "Тест"
    e.sender = "a@b.com"
    return e

def make_result(category: str) -> ClassificationResult:
    return ClassificationResult(category=category, confidence="high", reason="test")

def test_creates_all_category_dirs(tmp_path):
    output = tmp_path / "output"
    output.mkdir()
    EmailSorter(output)
    for cat in ALL_CATEGORIES:
        assert (output / cat).exists()

def test_file_copied_to_correct_category(setup):
    inbox, output, sorter = setup
    mail = inbox / "mail_0001.txt"
    mail.write_text("Subject: Test\nFrom: a@b.com\n\nBody", encoding="utf-8")
    email = make_email(mail)
    result = make_result("incidents")
    target = sorter.sort(email, result)
    assert target.exists()
    assert target.parent.name == "incidents"

def test_original_file_not_deleted(setup):
    inbox, output, sorter = setup
    mail = inbox / "mail_0001.txt"
    mail.write_text("Subject: Test\nFrom: a@b.com\n\nBody", encoding="utf-8")
    sorter.sort(make_email(mail), make_result("spam"))
    assert mail.exists()

def test_duplicate_filename_resolved(setup):
    inbox, output, sorter = setup
    (output / "incidents" / "mail_0001.txt").write_text("existing", encoding="utf-8")
    mail = inbox / "mail_0001.txt"
    mail.write_text("Subject: Test\nFrom: a@b.com\n\nBody", encoding="utf-8")
    target = sorter.sort(make_email(mail), make_result("incidents"))
    assert target.name != "mail_0001.txt"
    assert target.exists()

def test_unknown_category_dir_exists(setup):
    inbox, output, sorter = setup
    assert (output / "unknown").exists()