def show_statistics(data):

    success = 0

    if data["total"] > 0:
        success = round(
            (data["valid"] / data["total"]) * 100,
            2
        )

    print("\n========================================")
    print("        EMAIL CLEANING REPORT")
    print("========================================\n")

    print(f"Total Emails : {data['total']}")
    print(f"Valid Gmail  : {data['valid']}")
    print(f"Duplicates   : {data['duplicates']}")
    print(f"Invalid      : {data['invalid']}")
    print(f"Success Rate : {success}%")

    print("\n========================================")