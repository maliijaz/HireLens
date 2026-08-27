"""Generate sample PDFs for testing the AI Hiring Assistant."""
from fpdf import FPDF

W = 170  # usable page width with 20mm margins each side


class PDF(FPDF):
    def header(self):
        pass

    def section(self, title: str, body):
        self.set_font("Helvetica", "B", 12)
        self.set_fill_color(220, 220, 220)
        self.cell(W, 7, title, new_x="LMARGIN", new_y="NEXT", fill=True, border=0)
        self.ln(1)
        self.set_font("Helvetica", "", 10)
        if isinstance(body, list):
            for line in body:
                if line == "":
                    self.ln(2)
                else:
                    self.multi_cell(W, 5, line, new_x="LMARGIN", new_y="NEXT")
        else:
            self.multi_cell(W, 5, body, new_x="LMARGIN", new_y="NEXT")
        self.ln(4)

    def name_block(self, name: str, contact: str):
        self.set_font("Helvetica", "B", 16)
        self.cell(W, 10, name, new_x="LMARGIN", new_y="NEXT", align="C")
        self.set_font("Helvetica", "", 10)
        self.cell(W, 6, contact, new_x="LMARGIN", new_y="NEXT", align="C")
        self.ln(4)


def make_resume_1():
    pdf = PDF()
    pdf.set_margins(20, 20, 20)
    pdf.add_page()

    pdf.name_block("ALI HASSAN", "ali.hassan@email.com  |  +92-300-1234567  |  linkedin.com/in/alihassan")

    pdf.section("PROFESSIONAL SUMMARY",
        "Senior Machine Learning Engineer with 6 years of experience building and deploying "
        "production ML systems at scale. Specialised in NLP, recommendation engines, and MLOps. "
        "Reduced model inference latency by 40% and improved prediction accuracy across product lines."
    )

    pdf.section("TECHNICAL SKILLS", [
        "Languages: Python, SQL, Bash",
        "ML Frameworks: scikit-learn, TensorFlow, PyTorch, XGBoost, LightGBM",
        "MLOps: MLflow, Docker, Kubernetes, AWS SageMaker, CI/CD pipelines",
        "Data Engineering: Apache Spark, Pandas, NumPy, Apache Airflow",
        "Other: A/B Testing, Model Monitoring, REST APIs, Git, Feature Stores",
    ])

    pdf.section("PROFESSIONAL EXPERIENCE", [
        "Senior Machine Learning Engineer  |  TechCorp  |  Jan 2022 - Present",
        "- Led a 4-person team building a real-time recommendation engine (2M daily users).",
        "- Designed MLflow experiment tracking and model registry; cut retraining cycle by 30%.",
        "- Deployed models on Kubernetes with auto-scaling; P99 latency under 50ms.",
        "- Implemented feature store using Redis, reducing feature computation time by 60%.",
        "",
        "Machine Learning Engineer  |  DataCo  |  Jun 2020 - Dec 2021",
        "- Built end-to-end NLP pipeline for support ticket classification (92% accuracy).",
        "- Migrated batch scoring from EC2 to AWS SageMaker; saved $18k per year.",
        "- Wrote reusable feature engineering library adopted across 5 projects.",
        "",
        "Data Scientist  |  StartupX  |  Aug 2018 - May 2020",
        "- Developed churn prediction model using gradient boosting (AUC 0.87).",
        "- Set up A/B testing framework reducing time-to-decision from 2 weeks to 3 days.",
        "- Built Tableau dashboards used by C-suite for quarterly planning.",
    ])

    pdf.section("EDUCATION", [
        "M.S. Data Science  |  LUMS, Lahore  |  2018",
        "B.S. Computer Science  |  FAST-NUCES, Lahore  |  2016",
    ])

    pdf.section("CERTIFICATIONS", [
        "AWS Certified Machine Learning - Specialty",
        "Google Professional Data Engineer",
    ])

    pdf.output("sample_resume_1_ali_hassan.pdf")
    print("Created: sample_resume_1_ali_hassan.pdf")


def make_resume_2():
    pdf = PDF()
    pdf.set_margins(20, 20, 20)
    pdf.add_page()

    pdf.name_block("SARA AHMED", "sara.ahmed@email.com  |  +92-321-9876543")

    pdf.section("PROFESSIONAL SUMMARY",
        "Data Analyst with 2 years of experience in business intelligence and basic predictive modelling. "
        "Comfortable with Python and SQL for data wrangling and reporting. "
        "Eager to transition into a machine learning engineering role and grow technical skills."
    )

    pdf.section("TECHNICAL SKILLS", [
        "Languages: Python, SQL, R (basic)",
        "Libraries: Pandas, NumPy, Matplotlib, Seaborn, scikit-learn (introductory)",
        "BI Tools: Power BI, Tableau, Excel (advanced)",
        "Other: Jupyter Notebook, Git (basic), data cleaning, statistical analysis",
    ])

    pdf.section("PROFESSIONAL EXPERIENCE", [
        "Data Analyst  |  FinanceCo  |  Mar 2024 - Present",
        "- Build and maintain Power BI dashboards for the operations and finance teams.",
        "- Write SQL queries against Oracle DB for monthly and quarterly reporting.",
        "- Built a linear regression model in Python to forecast quarterly revenue (+/- 8% error).",
        "- Collaborate with stakeholders to define KPIs and reporting requirements.",
        "",
        "Junior Data Analyst  |  ConsultingFirm  |  Jan 2023 - Feb 2024",
        "- Cleaned and transformed datasets (up to 500k rows) for client delivery.",
        "- Automated weekly Excel reports using Python scripts, saving 6 hours per week.",
        "- Supported senior analysts in preparing client presentations and insights decks.",
    ])

    pdf.section("EDUCATION", [
        "B.S. Mathematics  |  University of Karachi  |  2022",
    ])

    pdf.section("CERTIFICATIONS", [
        "Google Data Analytics Certificate (Coursera, 2023)",
        "Python for Data Science - IBM (Coursera, 2022)",
    ])

    pdf.output("sample_resume_2_sara_ahmed.pdf")
    print("Created: sample_resume_2_sara_ahmed.pdf")


def make_jd():
    pdf = PDF()
    pdf.set_margins(20, 20, 20)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(W, 10, "Senior Machine Learning Engineer", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(W, 7, "Lahore, Pakistan (Hybrid)  |  Full-Time", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(5)

    pdf.section("ABOUT THE ROLE",
        "We are looking for a Senior Machine Learning Engineer to join our AI platform team. "
        "You will design, build, and maintain ML systems that power our core product features "
        "including personalised recommendations, fraud detection, and demand forecasting. "
        "You will work closely with data engineers, product managers, and software engineers "
        "to take models from experiment through to production."
    )

    pdf.section("REQUIRED SKILLS", [
        "Python (4+ years, production-grade code)",
        "ML frameworks: scikit-learn and TensorFlow or PyTorch",
        "SQL and experience working with large datasets",
        "MLOps: experiment tracking (MLflow), model deployment, and monitoring",
        "Containerisation with Docker; orchestration with Kubernetes or equivalent",
        "Version control with Git and familiarity with CI/CD pipelines",
    ])

    pdf.section("PREFERRED SKILLS", [
        "AWS SageMaker or equivalent cloud ML platform",
        "Distributed computing with Apache Spark",
        "Experience designing and running A/B tests",
        "Familiarity with feature stores (Feast, Tecton, or similar)",
    ])

    pdf.section("KEY RESPONSIBILITIES", [
        "Design, train, and deploy scalable ML models into production environments.",
        "Build and maintain data pipelines and feature engineering workflows.",
        "Monitor model performance in production and implement automated retraining.",
        "Conduct A/B tests and analyse results to guide product decisions.",
        "Collaborate with cross-functional teams on problem framing and solution design.",
        "Mentor junior data scientists and contribute to team coding standards.",
    ])

    pdf.section("REQUIREMENTS", [
        "4+ years of professional experience in machine learning or data science.",
        "B.S. or M.S. in Computer Science, Statistics, Mathematics, or related field.",
        "Strong communication skills - able to present model results to non-technical audiences.",
        "Experience taking at least one ML project from research to production.",
    ])

    pdf.section("WHAT WE OFFER", [
        "Competitive salary with performance-based bonus.",
        "Flexible hybrid working arrangement (3 days in office).",
        "Dedicated ML compute budget and tooling allowance.",
        "Annual learning and conference budget.",
    ])

    pdf.output("sample_job_description.pdf")
    print("Created: sample_job_description.pdf")


if __name__ == "__main__":
    make_resume_1()
    make_resume_2()
    make_jd()
    print("\nAll sample files created. Upload them in the Streamlit app to test.")
