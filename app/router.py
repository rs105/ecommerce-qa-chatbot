# Import necessary classes and functions from semantic_router
from semantic_router import Route
from semantic_router.routers import SemanticRouter
from semantic_router.encoders import HuggingFaceEncoder

# Initialize Hugging Face encoder using a pre-trained sentence transformer model
encoder = HuggingFaceEncoder(
    name="sentence-transformers/all-MiniLM-L6-v2"
)

# Define a route for FAQ-related queries with a list of sample utterances
faq = Route(
    name='faq',
    utterances=[
        "What is the return policy of the products?",
        "What is the refund policy?",
        "Can I get a refund?",
        "How do refunds work?",
        "How long does it take to get a refund?",
        "How do I request a refund?",
        "Tell me about the refund policy",
        "Refund policy details",
        "I want to know the refund policy",
        "What happens if I want a refund?",
        "How can I claim a refund?",
        "Do I get discount with the HDFC credit card?",
        "How can I track my order?",
        "What payment methods are accepted?",
        "How long does it take to process a refund?",
        "What happens if I receive a defective product?",
        "How do I return a faulty item?",
        "How do I report a damaged product?",
        "Do you accept cash?",
        "Can I pay with cash?",
        "Is cash an accepted payment method?",
        "What types of payments do you accept?",
        "Can I pay with UPI, card, or cash?",
    ]
)

# Define a route for SQL-style or product search queries with relevant utterances
sql = Route(
    name='sql',
    utterances=[
        "I want to buy nike shoes that have 50% discount.",
        "Are there any shoes under Rs. 3000?",
        "Do you have formal shoes in size 9?",
        "Are there any Puma shoes on sale?",
        "What is the price of puma running shoes?",
        "I want to buy nike shoes that have 50% discount.",
        "Are there any shoes under Rs. 3000?",
        "Do you have formal shoes in size 9?",
        "Are there any Puma shoes on sale?",
        "What is the price of puma running shoes?",
        "Show me top 3 nike shoes with rating higher than 4.5.",
        "List top-rated Adidas shoes.",
        "Show best 5 Puma shoes by rating.",
        "What are the highest rated Reebok shoes?",
        "Give me shoes sorted by rating.",
        "I want highly rated sports shoes.",
        "Top selling shoes this month.",
        "Find shoes with more than 4 star rating.",
        "List shoes with excellent ratings.",
        "I want shoes with highest discounts and best ratings."
    ]
)

# Define a route for handling casual or small talk queries
small_talk = Route(
    name='small-talk',
    utterances=[
        "How are you?",
        "What is your name?",
        "Who are you?",
        "Are you a robot?",
        "Are you an AI?",
        "What are you?",
        "What do you do?",
        "Tell me about yourself.",
        "Can you tell me your name?",
        "Are you human?"
    ]
)

# Initialize the semantic router with defined routes and the sentence encoder
# Enable local auto-sync for route vector storage
router = SemanticRouter(
    routes=[faq, sql, small_talk],
    encoder=encoder,
    auto_sync="local",
)

# Run classification examples when the script is executed directly
if __name__ == "__main__":
    # Classify a question about defective product policy
    print(router("What is your policy on defective product?").name)

    # Classify a product search query for Puma shoes
    print(router("Pink Puma shoes in price range 5000 to 1000").name)

    # Classify a small talk query asking for the bot's name
    print(router("What is your name?").name)
