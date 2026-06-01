import pytest
from pathlib import Path
from src.report import Report, ProcessingRecord, ReportGenerator
@pytest.fixture
def sample_report():
    report = Report()
    report.started_at = "2025-01-01T10:00:00"
    report.finished_at = "2025-01-01T10:00:01"
    records = [
        ProcessingRecord("mail_0001.txt", "incidents", "high", "score=6", "Сбой", "a@b.com"),
        ProcessingRecord("mail_0002.txt", "spam", "high", "score=3", "Выиграли!", "spam@x.com"),
        ProcessingRecord("mail_0003.txt", "unknown", "low", "нет совпадений", "", ""),
    ]
    for r in records:
        report.add(r)
    return report

def test_report_total(sample_report):
    assert sample_report.total == 3

def test_report_processed(sample_report):
    assert sample_report.processed == 2

def test_report_errors(sample_report):
    assert sample_report.errors == 1

def test_report_category_counts(sample_report):
    assert sample_report.category_counts["incidents"] == 1
    assert sample_report.category_counts["spam"] == 1
    assert sample_report.category_counts["unknown"] == 1

def test_report_saves_txt(tmp_path, sample_report):
    gen = ReportGenerator(tmp_path)
    gen.save(sample_report)
    txt_file = tmp_path / "report.txt"
    assert txt_file.exists()
    content = txt_file.read_text(encoding="utf-8")
    assert "incidents" in content
    assert "spam" in content

def test_report_saves_json(tmp_path, sample_report):
    import json
    gen = ReportGenerator(tmp_path)
    gen.save(sample_report)
    json_file = tmp_path / "report.json"
    assert json_file.exists()
    data = json.loads(json_file.read_text(encoding="utf-8"))
    assert data["total"] == 3
    assert data["by_category"]["spam"] == 1

def test_report_insights_mention_unknown(tmp_path, sample_report):
    gen = ReportGenerator(tmp_path)
    gen.save(sample_report)
    content = (tmp_path / "report.txt").read_text(encoding="utf-8")
    assert "unknown" in content.lower()

def test_empty_report(tmp_path):
    report = Report()
    report.started_at = "2025-01-01T10:00:00"
    report.finished_at = "2025-01-01T10:00:00"
    gen = ReportGenerator(tmp_path)
    gen.save(report)
    assert (tmp_path / "report.txt").exists()