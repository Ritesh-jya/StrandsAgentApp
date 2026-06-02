from pathlib import Path

from fpdf import FPDF

from .tools.amazon_feedback_tool import ProductFeedback


class FeedbackPDFReport:
    def create(self, feedback: ProductFeedback, summary: str, output_path: str) -> str:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Amazon.in Customer Feedback Report", ln=True, align="C")
        pdf.ln(6)

        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, f"Product: {feedback.product_name}", ln=True)
        pdf.set_font("Arial", "", 11)
        pdf.cell(0, 8, f"ASIN: {feedback.asin}", ln=True)
        pdf.set_text_color(0, 0, 255)
        pdf.cell(0, 8, feedback.product_url, ln=True, link=feedback.product_url)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(6)

        pdf.set_font("Arial", "B", 13)
        pdf.cell(0, 8, "Summary", ln=True)
        pdf.set_font("Arial", "", 11)
        pdf.multi_cell(0, 7, summary)
        pdf.ln(6)

        pdf.set_font("Arial", "B", 13)
        pdf.cell(0, 8, "Review Table", ln=True)
        pdf.ln(2)

        pdf.set_font("Arial", "B", 11)
        pdf.cell(35, 8, "Rating", border=1)
        pdf.cell(0, 8, "Review excerpt", border=1, ln=True)
        pdf.set_font("Arial", "", 10)

        for rating, review_text in feedback.reviews:
            pdf.cell(35, 8, rating, border=1)
            pdf.multi_cell(0, 8, review_text, border=1)

        pdf.output(str(output_file))
        return str(output_file)
