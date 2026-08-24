from gmail.drafts.draft_manager import create_draft


result = create_draft(
    "Profile 17",
    "test@gmail.com",
    "Grace Outreach Assistant - Identity Test",
    "This is a test draft for Gmail profile identity verification."
)

print("\nTEST RESULT:")

if result:
    print("SUCCESS")
    print("Draft ID:", result.get("id"))
else:
    print("FAILED")