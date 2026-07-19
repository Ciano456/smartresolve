# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

"""
Builds the labelled dataset used to train the FR8 classifiers.

There is no usable real ticket history in the database, only a handful of
test tickets, so this script writes realistic sample tickets instead.
Each category has a small set of hand written templates (title and
description pairs), and this script fills in different locations, teams
and time phrases so the same template does not produce the exact same
sentence twice.

Run it directly with:
    python ml/data/generate_dataset.py

It writes ml/data/tickets_dataset.csv, with one row per ticket and a
template_group column recording which template it came from. That column
is what stops the training command from letting near copies of the same
sentence end up on both sides of the train and validation split.
"""

from __future__ import annotations

import csv
import random
from collections import Counter
from pathlib import Path

# A fixed seed means the generated dataset is the same every time it is
# generated, including repeated calls in the same Python process.
RANDOM_SEED = 42
LOCATIONS = ["Naas office", "Carlow office", "Naas site", "Carlow branch"]
SUBJECTS = ["Finance team", "HR team", "reception", "operations team"]
TIMES = [
    "early this morning",
    "after lunch",
    "during a meeting",
    "after the latest restart",
    "when the office opened",
    "late yesterday",
    "while working remotely",
    "during normal daily work",
]
IMPACTS = [
    "one person is affected",
    "the whole team is affected",
    "work can continue using a temporary workaround",
    "the task is currently blocked",
]

# Fifteen independently worded sample tickets per category. The variety is
# important: validation holds out whole templates, so the classifier has to
# generalise to new ways of describing an issue rather than memorising a few
# sentences with different locations inserted. Boundary examples deliberately
# share vocabulary across categories while the described cause determines the
# label (for example, a permission denial is Access even when it occurs inside
# an application).
TEMPLATES = {
    "hardware": [
        (
            "Laptop will not start",
            "The laptop power light stays off after changing the charger at {location}.",
        ),
        (
            "Monitor has no display",
            "The monitor says no signal although the desktop is running for the {subject}.",
        ),
        (
            "Printer fault",
            "The printer jams on every page and shows a hardware error at {location}.",
        ),
        (
            "Docking station failure",
            "USB devices disconnect whenever the laptop is placed on the dock.",
        ),
        (
            "Router light is off",
            "There is no internet because the physical router has no power at {location}.",
        ),
        (
            "Keyboard keys not responding",
            "Several keyboard keys have stopped working on a desktop used by the {subject}.",
        ),
        (
            "Laptop battery is swollen",
            "The laptop case is lifting near the battery and the device should be inspected.",
        ),
        (
            "Webcam not detected",
            "The external webcam is not recognised after reconnecting it at {location}.",
        ),
        (
            "Projector shows no picture",
            "The meeting-room projector powers on but does not display an image.",
        ),
        (
            "Mouse disconnects",
            "The wired mouse repeatedly disconnects when moved to another USB port.",
        ),
        (
            "Laptop fan is noisy",
            "The laptop fan is grinding loudly and the computer becomes unusually hot.",
        ),
        (
            "Damaged charging port",
            "The charger only works when held at an angle in the laptop socket.",
        ),
        (
            "Headset microphone broken",
            "The headset plays sound but its microphone does not capture any audio.",
        ),
        (
            "Second screen flickering",
            "The physical display flickers with different cables and applications.",
        ),
        (
            "Desktop making warning beeps",
            "The workstation beeps during startup and does not reach the login screen.",
        ),
    ],
    "software": [
        (
            "Application keeps crashing",
            "The finance application closes whenever the {subject} saves a report.",
        ),
        (
            "Update caused an error",
            "The application will not open since yesterday's software update.",
        ),
        (
            "Spreadsheet is frozen",
            "Excel becomes unresponsive when opening the monthly workbook.",
        ),
        (
            "Install approved software",
            "Please install the approved reporting application for the {subject}.",
        ),
        (
            "Login screen freezes",
            "The payroll software accepts my password but freezes while loading.",
        ),
        (
            "PDF files will not open",
            "The document reader reports an error for every PDF downloaded by the {subject}.",
        ),
        (
            "Browser closes unexpectedly",
            "The web browser exits whenever a second tab is opened.",
        ),
        (
            "Incorrect totals in report",
            "The reporting program calculates the wrong total after importing a spreadsheet.",
        ),
        (
            "Email client search broken",
            "The desktop mail application opens normally but returns no search results.",
        ),
        (
            "Calendar application frozen",
            "The calendar stops responding after a meeting invitation is accepted.",
        ),
        (
            "Approved plugin fails to load",
            "The approved browser extension is installed but shows an initialization error.",
        ),
        (
            "Document formatting changed",
            "The word processor moves headings and tables when the file is saved.",
        ),
        (
            "Application licence error",
            "The licensed design program rejects its valid licence after an update.",
        ),
        (
            "Payroll export fails",
            "The payroll application accepts the user login but fails while exporting data.",
        ),
        (
            "Antivirus scan will not finish",
            "The approved antivirus program stops responding midway through a routine scan.",
        ),
    ],
    "network": [
        (
            "Wi-Fi disconnecting",
            "Wireless access drops every few minutes throughout the {location}.",
        ),
        (
            "VPN cannot connect",
            "The VPN times out before reaching the company network from home.",
        ),
        (
            "Shared drive unreachable",
            "The {subject} cannot reach the shared drive over the network.",
        ),
        (
            "Slow connection",
            "Internet performance is extremely slow for everyone at the {location}.",
        ),
        (
            "Cannot reach drive over VPN",
            "My account works locally but the shared drive is unreachable over VPN.",
        ),
        (
            "Wired connection unavailable",
            "The network cable is connected but the workstation cannot reach any internal site.",
        ),
        (
            "Video calls keep dropping",
            "Calls disconnect for several people whenever they use the office network.",
        ),
        (
            "Internal website times out",
            "The intranet cannot be reached from any computer at {location}.",
        ),
        (
            "Remote desktop disconnecting",
            "The remote session drops whenever the VPN connection becomes unstable.",
        ),
        (
            "Network printer unreachable",
            "The printer is powered on but no workstation can contact its network address.",
        ),
        (
            "Office connection lost",
            "Both wired and wireless internet access stopped for the {subject}.",
        ),
        (
            "Cloud files synchronising slowly",
            "File synchronisation stalls only while connected to the {location} network.",
        ),
        (
            "Cannot resolve internal address",
            "The internal server name is not resolving although public websites still load.",
        ),
        (
            "Weak wireless signal",
            "The Wi-Fi signal disappears in part of {location} for every nearby device.",
        ),
        (
            "VPN connected without resources",
            "The VPN reports connected but internal drives and pages remain unreachable.",
        ),
    ],
    "access": [
        (
            "Access denied",
            "Please grant my account permission to the {subject} shared folder.",
        ),
        ("Password reset", "I forgot my password and need a normal account reset."),
        (
            "New starter permissions",
            "A new employee needs approved access to the HR portal.",
        ),
        (
            "Remove leaver access",
            "Please revoke the former employee's account permissions today.",
        ),
        (
            "Cannot log into finance software",
            "The application opens but says my account lacks permission.",
        ),
        (
            "Account locked",
            "My approved account is locked after several failed sign-in attempts.",
        ),
        (
            "Multi-factor code rejected",
            "The portal accepts my password but rejects every authentication code.",
        ),
        (
            "Role permissions missing",
            "I can sign in to the reporting application but cannot access the manager functions.",
        ),
        (
            "Shared mailbox access",
            "Please authorise the {subject} to open the shared mailbox.",
        ),
        (
            "Database permission denied",
            "The database connection succeeds but my user is not authorised to view the records.",
        ),
        (
            "Expired account",
            "The system says my user account has expired and will not allow a sign-in.",
        ),
        (
            "Remove folder permission",
            "Please remove a contractor's access to the confidential project folder.",
        ),
        (
            "Cannot use approved feature",
            "The software loads correctly but says my role is not permitted to use approvals.",
        ),
        (
            "New account request",
            "Please create a standard system account for an approved new team member.",
        ),
        (
            "Permission changed unexpectedly",
            "I can log in but no longer have access to files I was authorised to use.",
        ),
    ],
}

# A few extra sentences that get stitched onto a normal ticket to make it
# security related, regardless of which category it belongs to. This is
# what gives the is_security_related column something real to learn from,
# a security concern can show up inside a hardware ticket just as easily
# as a software one.
SECURITY_VARIANTS = [
    (
        "Suspicious email reported",
        "A suspicious email asks me to open an attachment and enter my password.",
    ),
    ("Possible malware", "A malware warning appeared after an unexpected download."),
    (
        "Unauthorised access concern",
        "I noticed unauthorised access to my account this morning.",
    ),
    (
        "Possible credential theft",
        "An unexpected page requested my username, password, and authentication code.",
    ),
    (
        "Ransomware concern",
        "A message claims company files were encrypted and demands payment.",
    ),
    (
        "Spoofed sender reported",
        "The message appears to impersonate a manager and requests confidential data.",
    ),
    (
        "Unknown administrator activity",
        "An unrecognised administrator changed settings without approval.",
    ),
    (
        "Possible data breach",
        "Confidential company information may have been exposed to an unknown person.",
    ),
    (
        "Stolen work device",
        "A company device containing work information has been reported stolen.",
    ),
    (
        "Virus warning",
        "The security scanner detected a possible virus during this incident.",
    ),
    (
        "Suspicious sign-in page",
        "A fake-looking login page appeared and asked me to confirm my credentials.",
    ),
    (
        "Lost company device",
        "A work device containing company data cannot be located.",
    ),
]


def generate_examples(per_category: int = 180) -> list[dict[str, str | bool]]:
    """Build the full list of sample tickets, one dict per row."""
    random_source = random.Random(RANDOM_SEED)
    rows: list[dict[str, str | bool]] = []
    for category, templates in TEMPLATES.items():
        for index in range(per_category):
            # Cycle through the templates for this category rather than
            # picking randomly, so every template ends up with roughly
            # the same number of examples.
            template_index = index % len(templates)
            title, description = templates[template_index]
            location = random_source.choice(LOCATIONS)
            subject = random_source.choice(SUBJECTS)
            description = description.format(location=location, subject=subject)
            # Adds a bit more variety on top of the location and subject,
            # so not every ticket built from the same template reads
            # identically.
            occurrence = index // len(templates)
            description = (
                f"{description} It started {TIMES[occurrence % len(TIMES)]} and "
                f"{IMPACTS[(occurrence // len(TIMES)) % len(IMPACTS)]}."
            )
            # Roughly one in seven tickets gets a security angle added on
            # top of its normal category.
            is_security_related = index % 7 == 0
            if is_security_related:
                security_title, security_text = SECURITY_VARIANTS[
                    index % len(SECURITY_VARIANTS)
                ]
                title = f"{title} - {security_title}"
                description = f"{description} {security_text}"
            rows.append(
                {
                    "title": title,
                    "description": description,
                    "category": category,
                    "is_security_related": is_security_related,
                    # Records which template built this row, so the
                    # training command can keep whole templates together
                    # on one side of the split. See train_classifiers.py
                    # for why that matters.
                    "template_group": f"{category}-{template_index}",
                }
            )
    random_source.shuffle(rows)
    return rows


def main() -> None:
    rows = generate_examples()
    output_path = Path(__file__).with_name("tickets_dataset.csv")
    with output_path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    categories = Counter(str(row["category"]) for row in rows)
    security_count = sum(bool(row["is_security_related"]) for row in rows)
    print(f"Wrote {len(rows)} tickets to {output_path}")
    print(f"Categories: {dict(sorted(categories.items()))}")
    print(f"Security related: {security_count}")


if __name__ == "__main__":
    main()
