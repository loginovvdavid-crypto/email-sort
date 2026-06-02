import chardet
class Email:
    def __init__(self, path):
        self.path = path
        self.subject = ""
        self.sender = ""
        self.recipient = ""
        self.date = ""
        self.body = ""
        self.attachments = []
        self.raw = ""
        self.parse_error = False

class EmailReader:
    def read(self, path):
        email = Email(path)
        raw = self._read_file(path)
        if raw is None:
            email.parse_error = True
            return email

        if raw.strip() == "":
            email.parse_error = True
            return email

        email.raw = raw
        email.subject = self._get_header(raw, ["Subject", "Тема"])
        email.sender = self._get_header(raw, ["From", "От кого"])
        email.recipient = self._get_header(raw, ["To", "Кому"])
        email.date = self._get_header(raw, ["Date", "Дата"])
        email.attachments = self._get_attachments(raw)
        email.body = self._get_body(raw)
        return email

    def _read_file(self, path):
        try:
            raw_bytes = path.read_bytes()
        except Exception:
            return None
        detected = chardet.detect(raw_bytes)
        encoding = detected.get("encoding") or "utf-8"

        for enc in [encoding, "utf-8", "cp1251"]:
            try:
                return raw_bytes.decode(enc)
            except Exception:
                continue
        return None

    def _get_header(self, raw, field_names):
        for line in raw.splitlines():
            for name in field_names:
                if line.lower().startswith(name.lower() + ":"):
                    value = line[len(name) + 1:].strip()
                    return value
        return ""

    def _get_attachments(self, raw):
        attachments = []
        attach_names = ["Attachment", "Прикрепил", "Вложение", "Файл"]
        for line in raw.splitlines():
            for name in attach_names:
                if line.lower().startswith(name.lower() + ":"):
                    value = line[len(name) + 1:].strip()
                    if value:
                        attachments.append(value)
        return attachments

    def _get_body(self, raw):
        header_names = [
            "subject", "тема", "from", "от кого",
            "to", "кому", "date", "дата",
            "attachment", "прикрепил", "вложение", "файл"
        ]
        body_lines = []
        found_body = False
        for line in raw.splitlines():
            is_header = any(
                line.lower().startswith(name + ":") for name in header_names
            )
            if not is_header and line.strip():
                found_body = True
            if found_body:
                body_lines.append(line)
        return "\n".join(body_lines).strip()
