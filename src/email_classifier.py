# Классификатор писем по ключевым словам
class ClassificationResult:
    def __init__(self, category, confidence, reason):
        self.category = category
        self.confidence = confidence
        self.reason = reason

class EmailClassifier:
    RULES = {
        "spam": {
            "subject_keywords": [
                "выиграли", "выиграл", "приз", "лотерея",
                "exclusive offer", "limited time",
                "верификация аккаунта", "подтвердите личность",
                "срочно подтвердите",
            ],
            "body_keywords": [
                "перейдите по ссылке", "click here",
                "нажмите здесь", "corp-password-reset",
            ],
            "sender_keywords": [],
        },
        "monitoring": {
            "subject_keywords": [
                "[critical]", "[warning]", "[info]",
                "плановый отчёт мониторинга", "disk usage",
            ],
            "sender_keywords": [
                "grafana", "alerts@", "noreply@monitoring", "no-reply@monitoring",
            ],
            "body_keywords": [
                "healthcheck", "alert:", "disk usage", "database cluster",
            ],
        },
        "incidents": {
            "subject_keywords": [
                "urgent", "критический инцидент", "массовый сбой",
                "падает", "не работает", "работа остановлена",
                "недоступен", "не отвечает", "ошибка 500",
                "срочно:", "срочно: не работает",
            ],
            "sender_keywords": [],
            "body_keywords": [
                "критический инцидент", "работа полностью остановлена",
                "затронуты примерно", "просим срочно",
            ],
        },
        "hardware": {
            "subject_keywords": [
                "неисправность оборудования", "сломался",
                "проблема с принтер", "проблема с мышь",
                "проблема с гарнитура", "гарнитура",
                "сканер", "ноутбук", "монитор", "клавиатура",
            ],
            "sender_keywords": [],
            "body_keywords": [
                "не определяется системой", "ремонт", "не включается",
            ],
        },
        "software": {
            "subject_keywords": [
                "браузер", "chrome", "zoom", "антивирус",
                "excel", "adobe", "confluence", "gitlab",
                "service desk", "ошибка в", "проблема с установкой",
                "не запускается", "ошибка при",
            ],
            "sender_keywords": [],
            "body_keywords": [
                "не открывает файлы", "перестал запускаться",
                "ошибка при старте", "после обновления системы",
            ],
        },
        "access_requests": {
            "subject_keywords": [
                "запрос доступа", "нет доступа", "нужны права",
                "выдать права", "после перевода",
                "оформление нового сотрудника", "не могу войти",
            ],
            "sender_keywords": [],
            "body_keywords": [
                "предоставить доступ", "подготовить рабочее место",
                "новый сотрудник", "выход на работу",
                "нужны права на",
            ],
        },
        "hr": {
            "subject_keywords": [
                "заявка на отпуск", "больничный", "изменение графика",
                "отпуск", "график работы",
            ],
            "sender_keywords": [],
            "body_keywords": [
                "ежегодный отпуск", "больничный лист",
                "согласовать отпуск",
            ],
        },
        "documents": {
            "subject_keywords": [
                "закрывающие документы", "счёт на оплату",
                "финальная версия", "акт выполненных работ",
                "уточнение по оплате", "договор", "правки к",
                "fwd: акт",
            ],
            "sender_keywords": [],
            "body_keywords": [
                "передать в бухгалтерию", "подписать",
                "оплата по договору", "счёт и акт",
            ],
        },
        "newsletters": {
            "subject_keywords": [
                "корпоративный дайджест", "дайджест",
                "приглашение на демо", "перенос созвона",
                "[it]", "обновления корпоративного",
            ],
            "sender_keywords": [],
            "body_keywords": [
                "плановые технические работы",
                "ряд систем будет недоступен",
                "предлагаю созвон",
            ],
        },
    }
    PRIORITY = [
        "spam", "monitoring", "incidents", "hardware",
        "software", "access_requests", "hr", "documents", "newsletters",
    ]

    def classify(self, email):
        if email.parse_error:
            return ClassificationResult("unknown", "low", "файл не удалось прочитать")

        if not email.subject and not email.body and not email.sender:
            return ClassificationResult("unknown", "low", "письмо пустое")
        subject = email.subject.lower()
        body = email.body.lower()
        sender = email.sender.lower()
        scores = {}

        for category in self.PRIORITY:
            rules = self.RULES[category]
            score = 0

            for kw in rules.get("subject_keywords", []):
                if kw.lower() in subject:
                    score += 3
            for kw in rules.get("sender_keywords", []):
                if kw.lower() in sender:
                    score += 2
            for kw in rules.get("body_keywords", []):
                if kw.lower() in body:
                    score += 1
            scores[category] = score

        best = max(self.PRIORITY, key=lambda c: scores[c])
        if scores[best] == 0:
            return ClassificationResult("unknown", "low", "нет совпадений с правилами")
        score = scores[best]
        if score >= 3:
            confidence = "high"
        elif score >= 1:
            confidence = "medium"
        else:
            confidence = "low"
        return ClassificationResult(best, confidence, f"score={score}")