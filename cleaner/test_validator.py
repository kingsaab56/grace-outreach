from cleaner.modules.validator import validate_emails


emails = [
    "john@gmail.com",
    "test@gmail.com",
    "wrong@yahoo.com",
    "abc@gmail.com",
    "john@gmail.com",
    "invalid"
]


result = validate_emails(emails)

print(result)
