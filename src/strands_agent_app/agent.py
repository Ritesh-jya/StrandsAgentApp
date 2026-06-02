from .gemini_client import GeminiClient
from .tools.amazon_feedback_tool import AmazonFeedbackTool, ProductFeedback


class StrandsAgent:
    def __init__(self, gemini_client: GeminiClient | None = None, amazon_tool: AmazonFeedbackTool | None = None) -> None:
        self.gemini = gemini_client or GeminiClient()
        self.amazon_tool = amazon_tool or AmazonFeedbackTool()

    def get_customer_feedback(self, product_name: str) -> tuple[str, ProductFeedback]:
        feedback = self.amazon_tool.fetch_feedback(product_name)

        review_text = "\n".join(f"{rating} - {text}" for rating, text in feedback.reviews)
        prompt = (
            f"You are a customer-feedback synthesizer for Amazon.in products. "
            f"Use the raw review excerpts below to create a clear summary of customer sentiment, "
            f"top positives, top issues, and overall buying advice for the product '{product_name}'.\n\n"
            f"Product page: {feedback.product_url}\n"
            f"ASIN: {feedback.asin}\n\n"
            f"Raw review excerpts:\n{review_text}\n\n"
            f"Please provide a concise and user-friendly summary."
        )

        summary = self.gemini.chat(prompt)
        return summary, feedback
