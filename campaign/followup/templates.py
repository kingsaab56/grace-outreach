FOLLOWUP_TEMPLATES = {

    "initial": {
        "subject": "Professional Architectural & Estimating Services",
        "body": """
Hello {{name}},

We provide Architectural Drawings and Construction Estimating services.

Please let us know if we can assist you with any upcoming projects.

Thank you.
"""
    },

    "followup_1": {
        "subject": "Just checking in",
        "body": """
Hello {{name}},

I wanted to follow up on my previous email.

Please let me know if you have any upcoming projects.

Thank you.
"""
    },

    "followup_2": {
        "subject": "Any upcoming projects?",
        "body": """
Hello {{name}},

I hope you're doing well.

I just wanted to check whether you have any current or upcoming projects where we can help.

Thank you.
"""
    },

    "final": {
        "subject": "Final Follow-Up",
        "body": """
Hello {{name}},

This is my final follow-up.

If now isn't the right time, no problem. We'd be happy to connect whenever you need Architectural or Estimating services.

Thank you.
"""
    }

}


def get_template(name):
    return FOLLOWUP_TEMPLATES.get(name)