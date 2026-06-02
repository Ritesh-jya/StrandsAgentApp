from strands_agent_app.agent import StrandsAgent
from strands_agent_app.pdf_report import FeedbackPDFReport


def slugify(text: str) -> str:
    return "_".join(ch for ch in text if ch.isalnum() or ch == " ").strip().replace(" ", "_").lower()


def main() -> None:
    print("Strands Agent Amazon.in Feedback Collector")
    print("Enter a product name and the agent will fetch customer feedback from Amazon.in.")

    product_name = input("Product name: ").strip()
    if not product_name:
        print("No product name provided. Exiting.")
        return

    agent = StrandsAgent()
    try:
        summary, feedback = agent.get_customer_feedback(product_name)
    except Exception as exc:
        print("Error while running the agent:", exc)
        return

    print("\n=== Customer Feedback Summary ===\n")
    print(summary)

    save_pdf = input("\nSave a PDF report with the Amazon link and table of feedback? (y/N): ").strip().lower() == "y"
    if save_pdf:
        default_path = f"feedback_report_{slugify(product_name)}.pdf"
        output_path = input(f"Output file [{default_path}]: ").strip() or default_path
        try:
            report_path = FeedbackPDFReport().create(feedback, summary, output_path)
            print(f"PDF report saved to: {report_path}")
        except Exception as exc:
            print("Failed to generate PDF report:", exc)


if __name__ == "__main__":
    main()
