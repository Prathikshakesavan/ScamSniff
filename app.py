
import streamlit as st
import joblib
import re
from datetime import datetime

# ---------------- PAGE SETTINGS ----------------
st.set_page_config(
    page_title="ScamSniff | Job Detective",
    page_icon="🕵️",
    layout="wide"
)

# ---------------- LOAD AI MODEL ----------------
@st.cache_resource
def load_components():
    model = joblib.load("scamsniff_model.pkl")
    tfidf = joblib.load("tfidf_vectorizer.pkl")
    return model, tfidf

try:
    model, tfidf = load_components()
except Exception:
    st.error(
        "Model files not found! Keep scamsniff_model.pkl, "
        "tfidf_vectorizer.pkl and app.py in the same folder."
    )
    st.stop()

# ---------------- SESSION HISTORY ----------------
if "job_history" not in st.session_state:
    st.session_state.job_history = []

# ---------------- DESIGN AND ANIMATIONS ----------------
st.markdown("""
<style>
.stApp {
    background: #f1f6fc;
    color: #000000;
}

header[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    max-width: 1250px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}

/* Make ordinary text black */
.stApp p,
.stApp label,
.stApp li,
.stApp .stMarkdown,
.stApp [data-testid="stMetricLabel"],
.stApp [data-testid="stMetricValue"],
.stApp [data-testid="stCaptionContainer"] {
    color: #000000;
}

/* Keep headings black */
.stApp h1,
.stApp h2,
.stApp h3,
.stApp h4,
.stApp h5 {
    color: #000000 !important;
}

/* Input fields */
.stApp input,
.stApp textarea,
.stApp [data-baseweb="input"] input,
.stApp [data-baseweb="textarea"] textarea {
    color: #000000 !important;
    background-color: #ffffff !important;
    -webkit-text-fill-color: #000000 !important;
    caret-color: #000000 !important;
}

.stApp input::placeholder,
.stApp textarea::placeholder {
    color: #555555 !important;
    -webkit-text-fill-color: #555555 !important;
}

/* Dropdown and select text */
.stApp [data-baseweb="select"] *,
.stApp [data-baseweb="select"] input {
    color: #000000 !important;
}

/* Navigation header */
.navbar {
    background: #dcecff;
    border: 2px solid #b9d8ff;
    border-radius: 18px;
    padding: 18px 25px;
    margin-bottom: 25px;
    box-shadow: 0 7px 22px rgba(20, 50, 90, 0.08);
}

.brand {
    color: #000000 !important;
    font-size: 30px;
    font-weight: 900;
}

.brand span {
    color: #005cc8 !important;
}

.tagline {
    color: #222222 !important;
    font-size: 13px;
    font-weight: 600;
}

/* Hero section */
.hero {
    background: #ffffff;
    border: 2px solid #d1e4fa;
    border-radius: 24px;
    padding: 28px;
    box-shadow: 0 8px 24px rgba(20, 50, 90, 0.08);
}

.eyebrow {
    color: #005cc8 !important;
    font-weight: 800;
    letter-spacing: 2px;
    font-size: 12px;
}

.hero-title {
    color: #000000 !important;
    font-size: clamp(32px, 4vw, 54px);
    font-weight: 900;
    line-height: 1.15;
    margin: 12px 0;
}

.hero-title span {
    color: #0066d6 !important;
}

.hero-copy {
    color: #222222 !important;
    font-size: 17px;
    line-height: 1.7;
}

/* Detective and floating cards */
.detective-scene {
    min-height: 270px;
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    background: radial-gradient(circle, #d0e9ff, #f1f8ff 70%);
    border-radius: 22px;
}

.detective {
    font-size: 105px;
    animation: detectiveFloat 3s ease-in-out infinite;
    z-index: 2;
    filter: drop-shadow(0 10px 8px rgba(0, 0, 0, .15));
}

.float-card {
    position: absolute;
    background: #ffffff;
    color: #000000 !important;
    border: 1px solid #bfd8f5;
    border-radius: 12px;
    padding: 11px;
    font-size: 13px;
    font-weight: 800;
    box-shadow: 0 5px 15px rgba(0, 0, 0, .10);
    animation: cardFloat 3.5s ease-in-out infinite;
}

.card-job {
    top: 12px;
    left: 2px;
}

.card-scam {
    bottom: 12px;
    left: 2px;
    color: #b00020 !important;
    animation-delay: .5s;
}

.card-resume {
    top: 18px;
    right: 2px;
    animation-delay: 1s;
}

@keyframes detectiveFloat {
    0%, 100% { transform: translateY(0) rotate(-2deg); }
    50% { transform: translateY(-13px) rotate(2deg); }
}

@keyframes cardFloat {
    0%, 100% { translate: 0 0; }
    50% { translate: 0 -9px; }
}

/* Feature cards */
.section-title {
    color: #000000 !important;
    font-size: 27px;
    font-weight: 900;
    margin-top: 24px;
}

.section-subtitle {
    color: #333333 !important;
    margin-bottom: 18px;
}

.feature-card {
    background: #ffffff;
    border: 2px solid #d5e5f7;
    border-radius: 17px;
    padding: 18px;
    min-height: 155px;
    box-shadow: 0 4px 14px rgba(0, 0, 0, .04);
    transition: transform .25s ease, box-shadow .25s ease;
}

.feature-card:hover {
    transform: translateY(-6px);
    box-shadow: 0 10px 22px rgba(0, 70, 150, .14);
}

.feature-icon {
    font-size: 30px;
}

.feature-title {
    color: #000000 !important;
    font-weight: 850;
    font-size: 16px;
    margin-top: 7px;
}

.feature-copy {
    color: #333333 !important;
    font-size: 13px;
    line-height: 1.6;
    margin-top: 6px;
}

/* Buttons */
div.stButton > button {
    background: #075bc7;
    color: #ffffff !important;
    border: none;
    border-radius: 12px;
    min-height: 48px;
    font-weight: 800;
    transition: all .2s ease;
}

div.stButton > button p,
div.stButton > button span {
    color: #ffffff !important;
}

div.stButton > button:hover {
    background: #003f91;
    transform: translateY(-2px);
    box-shadow: 0 6px 15px rgba(0, 80, 180, .20);
}

/* Metrics */
div[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #d3e4f8;
    border-radius: 15px;
    padding: 16px;
}

/* Footer */
.footer {
    margin-top: 30px;
    padding: 24px;
    border-radius: 18px;
    background: #dcecff;
    border: 2px solid #b9d8ff;
    color: #000000 !important;
    text-align: center;
    line-height: 1.8;
}

.footer div {
    color: #000000 !important;
}

/* Reduce animations for accessibility */
@media (prefers-reduced-motion: reduce) {
    .detective, .float-card, .feature-card {
        animation: none !important;
        transition: none !important;
    }
}
</style>
""", unsafe_allow_html=True)

# ---------------- NAVIGATION HEADER ----------------
st.markdown("""
<div class="navbar">
    <div class="brand">🛡️ Scam<span>Sniff</span></div>
    <div class="tagline">
        YOUR AI JOB DETECTIVE • THINK BEFORE YOU APPLY
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------- HERO SECTION ----------------
left, right = st.columns([1.15, 1], gap="large")

with left:
    st.markdown("""
    <div class="hero">
        <div class="eyebrow">🕵️ YOUR JOB SAFETY PARTNER</div>
        <div class="hero-title">
            Your dream job.<br>
            <span>Without the scams.</span>
        </div>
        <div class="hero-copy">
            Meet ScamSniff, your AI job detective. Investigate
            suspicious job postings, discover possible warning signs,
            and make informed decisions before applying.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    if st.button("🔎 Start Your Investigation", use_container_width=True):
        st.session_state.show_analyzer = True

with right:
    st.markdown("""
    <div class="detective-scene">
        <div class="float-card card-job">
            💼 JOB OFFER<br>New opportunity!
        </div>
        <div class="float-card card-scam">
            🚨 SCAM ALERT?
        </div>
        <div class="float-card card-resume">
            📄 RESUME<br>Application found
        </div>
        <div class="detective">🕵️‍♀️</div>
    </div>
    """, unsafe_allow_html=True)

# ---------------- HOW IT WORKS ----------------
st.markdown(
    '<div class="section-title">How ScamSniff Works</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="section-subtitle">'
    'Four simple steps to investigate a job opportunity.'
    '</div>',
    unsafe_allow_html=True
)

features = [
    ("📋", "1. Enter Job Details",
     "Enter the job title, company name, and job description."),
    ("🧠", "2. AI Investigation",
     "The trained model analyses the job description."),
    ("🚨", "3. See the Risk",
     "Review fraud probability, risk level, and warning signs."),
    ("🛡️", "4. Stay Informed",
     "Verify the employer before deciding to apply.")
]

columns = st.columns(4)

for col, (icon, title, description) in zip(columns, features):
    with col:
        st.markdown(f"""
        <div class="feature-card">
            <div class="feature-icon">{icon}</div>
            <div class="feature-title">{title}</div>
            <div class="feature-copy">{description}</div>
        </div>
        """, unsafe_allow_html=True)

# ---------------- JOB ANALYSER ----------------
st.markdown("---")
st.markdown(
    '<div class="section-title">🔎 Investigate a Job Posting</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="section-subtitle">'
    'Enter the job details below. Your job description is analysed '
    'using your saved AI model.'
    '</div>',
    unsafe_allow_html=True
)

job_title = st.text_input(
    "Job Title",
    placeholder="e.g., Data Analyst Intern"
)

company_name = st.text_input(
    "Company Name",
    placeholder="Enter the company name"
)

job_description = st.text_area(
    "Job Description *",
    placeholder=(
        "Paste the full job description, including salary, "
        "requirements and any payment requests..."
    ),
    height=220
)

check_job = st.button(
    "🕵️ Investigate This Job",
    type="primary",
    use_container_width=True
)

# ---------------- RED-FLAG CHECKER ----------------
def find_red_flags(text):
    text = text.lower()
    flags = []

    checks = [
        (
            r"registration fee|pay.{0,30}(fee|deposit)|"
            r"security deposit|upfront payment|processing fee",
            "💳 Possible upfront payment request",
            "Be cautious. Legitimate employers generally should not "
            "ask candidates to pay money to obtain a job."
        ),
        (
            r"guaranteed income|earn ₹?[\d,]+\s*(per day|daily)|"
            r"earn \$?[\d,]+\s*(per day|daily)|easy money|"
            r"unlimited income",
            "💰 Attractive earnings claim",
            "Check whether the advertised salary is realistic "
            "for the job and required experience."
        ),
        (
            r"urgent hiring|limited vacancies|apply immediately|"
            r"act now|only today|hurry",
            "⏰ Urgency or pressure language",
            "Pressure to apply immediately can discourage careful "
            "verification. It is a warning sign, not proof of fraud."
        ),
        (
            r"no experience required|work from home|"
            r"work remotely|instant hiring",
            "🔍 Broad job claim",
            "These phrases can appear in genuine jobs too. "
            "Verify the employer, duties and recruitment process."
        ),
        (
            r"whatsapp only|telegram only|contact.{0,30}whatsapp|"
            r"interview.{0,30}(whatsapp|telegram)",
            "📱 Messaging-only recruitment",
            "Verify that the recruiter and contact details "
            "belong to the actual company."
        )
    ]

    for pattern, title, explanation in checks:
        if re.search(pattern, text):
            flags.append((title, explanation))

    return flags

# ---------------- AI PREDICTION ----------------
if check_job:
    if not job_description.strip():
        st.warning("Please enter a job description first.")
    else:
        try:
            with st.spinner("🕵️ Detective is investigating..."):
                job_vector = tfidf.transform([job_description])
                prediction = model.predict(job_vector)[0]
                probability = float(
                    model.predict_proba(job_vector)[0][1]
                )

            st.markdown("---")
            st.markdown(
                '<div class="section-title">📊 Investigation Report</div>',
                unsafe_allow_html=True
            )

            col1, col2, col3 = st.columns(3)

            with col1:
                if int(prediction) == 1:
                    st.error("🚨 Potentially Fraudulent")
                else:
                    st.success("✅ Likely Genuine")

            with col2:
                st.metric(
                    "Model Fraud Probability",
                    f"{probability * 100:.2f}%"
                )

            if probability < 0.30:
                risk = "LOW"
                with col3:
                    st.success("🟢 LOW Risk")
            elif probability < 0.70:
                risk = "MEDIUM"
                with col3:
                    st.warning("🟠 MEDIUM Risk")
            else:
                risk = "HIGH"
                with col3:
                    st.error("🔴 HIGH Risk")

            st.progress(
                probability,
                text="Model-estimated fraud probability"
            )

            st.caption(
                "Risk levels are based on estimated probability. "
                "They are screening aids, not proof of fraud or legitimacy."
            )

            # Combine fields for the red-flag checklist
            combined_text = (
                (job_title or "") + " " +
                (company_name or "") + " " +
                job_description
            )

            flags = find_red_flags(combined_text)

            st.markdown("### 🧐 Detective's Red-Flag Review")

            if flags:
                st.write(
                    "These phrases were found in the submitted text. "
                    "Please investigate them carefully."
                )
                for title, explanation in flags:
                    st.warning(f"**{title}**\n\n{explanation}")
            else:
                st.info(
                    "No phrases from our checklist were detected. "
                    "This does not guarantee that the job is safe."
                )

            st.markdown("### 🛡️ Before You Apply")
            st.markdown("""
            - Verify the company using its official website.
            - Check that the recruiter's email belongs to the company.
            - Never pay money to secure a job or interview.
            - Never share OTPs, passwords or sensitive banking details.
            """)

            # Save investigation history
            st.session_state.job_history.insert(0, {
                "time": datetime.now().strftime("%d %b %Y, %I:%M %p"),
                "title": job_title.strip() or "Untitled Job",
                "company": company_name.strip() or "Not provided",
                "prediction": (
                    "Potentially Fraudulent"
                    if int(prediction) == 1
                    else "Likely Genuine"
                ),
                "probability": probability,
                "risk": risk
            })

        except Exception as e:
            st.error("The investigation could not be completed.")
            st.exception(e)

# ---------------- INVESTIGATION HISTORY ----------------
st.markdown("---")
st.markdown(
    '<div class="section-title">🗂️ Investigation History</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="section-subtitle">'
    'Jobs checked during the current session.'
    '</div>',
    unsafe_allow_html=True
)

if st.session_state.job_history:
    for item in st.session_state.job_history:
        with st.expander(
            f"{item['title']} — {item['prediction']} ({item['risk']} risk)"
        ):
            st.write("**Company:**", item["company"])
            st.write("**Checked:**", item["time"])
            st.write(
                "**Fraud Probability:**",
                f"{item['probability'] * 100:.2f}%"
            )
            st.write("**Risk Level:**", item["risk"])

    if st.button("🗑️ Clear History"):
        st.session_state.job_history = []
        st.rerun()
else:
    st.info("Your checked jobs will appear here.")

# ---------------- FOOTER ----------------
st.markdown("""
<div class="footer">
    <div style="font-size:27px;font-weight:900;">
        🛡️ ScamSniff
    </div>
    <div>Think before you apply. Investigate before you trust.</div>
    <div style="font-size:13px;margin-top:8px;">
        AI-assisted screening • Always verify job offers independently
    </div>
</div>
""", unsafe_allow_html=True)
