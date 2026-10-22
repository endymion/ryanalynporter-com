"""The standing copy of the Building and Background pages (and their summaries on the home page).

Articles are content items under content/; this module holds what describes Ryan rather than what he wrote.
"""

RESUME_URL = "/resume/Ryan-Porter-resume.pdf"
GITHUB_URL = "https://github.com/AnthusAI"
LINKEDIN_URL = "https://linkedin.com/in/ryanalynporter"
ANTHUS_PROFILE_URL = "https://anth.us/ryan/"

HOME_INTRODUCTION = "I run a lab that invents AI systems, builds them, and keeps them running in production. The writing comes out of that work."
HOME_BACKGROUND = (
    "Thirty years of inventing, building and operating software: a Perl webmail product when Hotmail was new, a BlackBerry "
    "app before the iPhone, a Las Vegas ticketing platform that cleared regulators and audits, and an AI lab that put a "
    "self-improving agent system into commercial production.",
    "B.S. Computer Science, University of Florida. Engineering intern at 3Dfx during the original Voodoo Graphics chipset.",
)
AUTHOR_BLURB = "CTO and applied-AI builder in Miami Beach. I run a lab that invents AI systems, builds them and keeps them running in production."

HOME_GROUPS = (
    ("Products", (
        ("DataParade", "Maps how sensitive data moves through AI-written code, across eight languages plus Terraform."),
        ("B0rd", "A standalone LED-matrix desk display for glanceable agent status."),
    )),
    ("AI solutions", (
        ("Cyclotron", "AI decisions that learn."),
        ("Chatticus", "Shared rooms for humans and bots, with approvals."),
        ("Papyrus", "An automated newsroom — the platform behind the publications above."),
        ("Auritus", "Open text-to-speech narration for any page."),
    )),
    ("Open source", (
        ("Plexus", "Agent and MLOps platform: evaluation, versioning, champion/challenger, feedback flywheel."),
        ("Tactus", "Agent procedures as versioned, executable code."),
        ("Biblicus", "Whole-corpus analysis: topic models, HMMs, retrieval, LLMs."),
        ("Kanbus", "Project management and durable memory for AI agents."),
    )),
)

HOME_STATS = (
    ("15M+", "automated QA decisions in production"),
    ("180B+", "LLM tokens processed"),
    ("$150M+", "ticketing revenue through a platform I built"),
    ("30 yrs", "shipping software"),
)

HOME_ROLES = (
    ("2026 — now", "DataParade", "Chief Technology Officer"),
    ("2023 — now", "Anthus AI Solutions", "Lead AI Solutions Architect"),
    ("2024 — 2026", "Call Criteria / Capacity", "Chief Scientist"),
    ("2014 — 2024", "Tao Group / Hakkasan", "VP Technology, VP Marketing Technology"),
    ("2007 — 2013", "Venue Driver", "CTO"),
    ("1997 — now", "Endymion Corporation", "President"),
)

PRODUCTS = (
    {
        "name": "DataParade", "status": "2026 — ongoing", "role": "CTO", "tint": "anthus",
        "url": "https://github.com/DataParade-io/dataparade-cli", "link_label": "dataparade-cli on GitHub",
        "description": "Helps developers keep up with AI-generated code. A deterministic scan engine maps how sensitive data moves through a codebase across eight languages plus Terraform, and renders it as a reviewable graph.",
    },
    {
        "name": "B0rd", "status": "2026 — ongoing", "role": "Anthus Microelectronics", "tint": "distinctive",
        "url": "https://anth.us/", "link_label": "On anth.us",
        "description": "A standalone LED-matrix desk display for glanceable agent status.",
    },
)

SOLUTIONS = (
    ("Cyclotron", "AI decisions that learn."),
    ("Chatticus", "Shared rooms for humans and bots, with approvals."),
    ("Papyrus", "An automated newsroom — the platform behind the Anthus publications."),
    ("Auritus", "A text-to-speech embed that narrates web pages."),
)

OPEN_SOURCE = (
    ("Plexus", True, "Agent and MLOps platform: classifier execution, evaluation, versioning, champion/challenger and the human-feedback flywheel."),
    ("Tactus", True, "A DSL and runtime expressing agent procedures as versioned, executable code."),
    ("Biblicus", True, "Whole-corpus analysis with topic modeling, hidden Markov models, retrieval and LLMs."),
    ("Kanbus", False, "Project management and durable memory for AI agents."),
    ("Auritus", False, "Open ElevenLabs Audio Native alternative on local GPUs, with AWS fallback."),
    ("VideoML", False, "A declarative DSL for video generation."),
    ("Markus", False, "Anthus-flavored Markdown."),
)

PRODUCTION_SYSTEMS = (
    ("2023 — 2026", "Call Criteria AI lab", "15M+ scoring decisions", "A self-improving QA classifier system: coding agents diagnose reviewer disagreements, propose fixes, and promote only what beats human agreement benchmarks."),
    ("2007 — present", "Venue Driver", "$150M+ ticketing revenue", "Ticketing, reservations and guest management that ran Las Vegas hospitality operations, from on-premises to AWS to serverless."),
)

BACKGROUND_EYEBROW = "CTO · Applied AI and data systems · Miami Beach"
BACKGROUND_SUMMARY = (
    "I put a fully automated, self-improving agent system into commercial production, hands-on through architecture and "
    "code. I build the parts that make enterprise AI trustworthy at scale: ground-truth evaluation, statistically gated "
    "promotion, fine-tuned production models, and a human-feedback flywheel driving automated root-cause analysis."
)

BACKGROUND_STATS = (
    ("15M+", "automated QA scoring decisions, across 2M customer conversations"),
    ("180B+", "LLM tokens in production workloads"),
    ("$64M", "peak monthly revenue through platforms I ran, with no major incidents"),
    ("30+ yrs", "data, cloud, security and mission-critical software"),
)

EXPERIENCE = (
    ("2026 — now", "DataParade", "Chief Technology Officer", (
        "Leads technology at an early-stage privacy and security startup helping developers keep up with AI-generated code.",
        "Directs a deterministic scan engine that maps how sensitive data moves through a codebase, across eight languages plus Terraform.",
        "Shipped the scanner as an open-source, one-command CLI; Plexus scores its accuracy against labeled fixtures.",
    )),
    ("2024 — 2026", "Capacity / Call Criteria", "Chief Scientist", (
        "Built Call Criteria’s AI/ML lab from scratch and carried it through Capacity’s 2025 acquisition.",
        "Delivered a fully automated hill-climbing loop that improves production QA classifiers without human prompt engineering.",
        "Engineered the safeguards for unattended self-modification: changes ship only when they beat human-reviewer agreement by more than chance.",
        "Built the platform fully serverless on AWS, and portable to Kubernetes.",
    )),
    ("2023 — now", "Anthus AI Solutions", "Lead AI Solutions Architect", (
        "Independent AI practice that delivered the Call Criteria engagement.",
        "Maintains the open-source portfolio used at Capacity, DataParade and other clients.",
    )),
    ("2014 — 2024", "Tao Group Hospitality / Hakkasan Group", "VP Technology → VP Marketing Technology", (
        "Led three agile teams through successive acquisitions and two architectural shifts: cloud, then serverless.",
        "Cleared an independent outside audit, and won Nevada Gaming Control Board approval to run on AWS.",
        "Personally built the ticketing and barcode-redemption platform behind $150M+ in ticket sales.",
    )),
    ("1997 — 2014", "Earlier", "Endymion · Venue Driver · Angel Management · CoolJunkie", (
        "Built and licensed a commercial Perl webmail product when Hotmail was a new idea.",
        "Co-founded CoolJunkie, which became Venue Driver; built its ticketing, reservation and guest-management systems as CTO.",
        "Shipping mobile software since the 1990s: WAP, then BlackBerry before the iPhone, then mobile web and iOS.",
    )),
)

EDUCATION = (
    ("University of Florida", "B.S., Computer Science."),
    ("3Dfx Interactive", "Engineering intern on the original Voodoo Graphics chipset; tests for the pixel-accurate simulator and the GL library that became Glide."),
    ("Computer vision research", "DoD-funded multispectral imagery work on automated mine detection and distortion correction."),
    ("SICP teaching assistant", "TA for a Structure and Interpretation of Computer Programs course; research on automated code analysis."),
)

EXPERTISE = (
    ("Applied AI", ("Self-evolving agents", "Hill-climbing optimization", "Fine-tuning", "Evaluation", "Champion/challenger", "Root-cause analysis", "Topic modeling", "MCP", "LLMOps")),
    ("Data engineering", ("Data warehouses", "Data lakes", "Pipelines", "Information architecture", "Corpus analysis", "Regulatory reporting")),
    ("Cloud and governance", ("AWS", "Serverless", "SageMaker", "Kubernetes", "CDK", "Helm", "PCI-scope reduction", "Compliance")),
    ("Engineering", ("Python", "Rust", "Lua", "TypeScript", "Ruby", "C++", "ANTLR", "scikit-learn", "Docker")),
)
