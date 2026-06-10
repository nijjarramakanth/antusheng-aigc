# AIGC Prompts Library - Educational Training System
PROMPTS_DATABASE = [
    {"title": "Creative Story Starter", "category": "text_generation", "difficulty": "beginner", "content": "Write a short 200-word story that begins with: 'The old door creaked open, revealing...'", "example_output": "The old door creaked open, revealing a hidden library filled with glowing books. Each tome seemed to pulse with ancient knowledge...", "use_case": "Perfect for creative writing practice", "tags": ["creative", "storytelling"], "ai_platform": "gemini", "created_by": "admin"},
    {"title": "Email Marketing Copywriting", "category": "text_generation", "difficulty": "beginner", "content": "Write a compelling 150-word email to promote a new eco-friendly product. Include a special discount code.", "example_output": "Subject: Stay Eco-Friendly Today!\n\nDear Friend...", "use_case": "Learn email marketing fundamentals", "tags": ["marketing", "email"], "ai_platform": "gemini", "created_by": "admin"},
    {"title": "Product Description Writer", "category": "text_generation", "difficulty": "beginner", "content": "Write a 100-word product description for a wireless headphone. Focus on benefits.", "example_output": "Experience pure audio bliss...", "use_case": "E-commerce copywriting practice", "tags": ["product", "e-commerce"], "ai_platform": "gemini", "created_by": "admin"},
    {"title": "Social Media Post - Instagram", "category": "text_generation", "difficulty": "beginner", "content": "Create 5 engaging Instagram captions for a fitness brand post.", "example_output": "Rise and grind! 💪 Your morning workout is the best investment...", "use_case": "Master social media engagement", "tags": ["social_media", "instagram"], "ai_platform": "gemini", "created_by": "admin"},
    {"title": "SEO Blog Post Outline", "category": "text_generation", "difficulty": "intermediate", "content": "Create a detailed outline for a 2000-word blog post about dropshipping.", "example_output": "# How to Start Dropshipping\nH2: Introduction\nH2: Understanding Basics...", "use_case": "Learn SEO content structure", "tags": ["seo", "blog"], "ai_platform": "gemini", "created_by": "admin"},
    {"title": "Fantasy Character Design", "category": "image_generation", "difficulty": "beginner", "content": "Create an image of a fantasy elf warrior with glowing blue eyes, wearing silver armor, holding a mystical sword.", "example_output": "[Detailed fantasy illustration]", "use_case": "Character design practice", "tags": ["fantasy", "character"], "ai_platform": "gemini", "created_by": "admin"},
    {"title": "Product Photography - Minimalist", "category": "image_generation", "difficulty": "beginner", "content": "Generate a professional product photo of a luxury wristwatch on white background.", "example_output": "[Professional studio photo]", "use_case": "Product photography styling", "tags": ["product", "photography"], "ai_platform": "gemini", "created_by": "admin"},
    {"title": "Prompt Structure Basics", "category": "prompt_engineering", "difficulty": "beginner", "content": "Learn the basic structure: [Task] + [Context] + [Format] + [Style]", "example_output": "Example of well-structured prompt...", "use_case": "Foundation for AIGC work", "tags": ["fundamentals", "prompt"], "ai_platform": "gemini", "created_by": "admin"},
    {"title": "Role-Based Prompting", "category": "prompt_engineering", "difficulty": "beginner", "content": "Assign a role to AI: 'You are an expert UX designer...'", "example_output": "Detailed UX design description...", "use_case": "Get specialized responses", "tags": ["prompt", "role"], "ai_platform": "gemini", "created_by": "admin"},
    {"title": "Headline Writing - Clickbait Style", "category": "copywriting", "difficulty": "beginner", "content": "Write 5 engaging headlines for a productivity article.", "example_output": "1. This One Weird Trick Will Blow Your Mind...\n2. Billionaires Don't Want You To Know This...", "use_case": "Master headline writing", "tags": ["copywriting", "headlines"], "ai_platform": "gemini", "created_by": "admin"},
]

def get_all_prompts():
    return PROMPTS_DATABASE

def get_prompts_by_category(category):
    return [p for p in PROMPTS_DATABASE if p['category'] == category]

def get_prompts_by_difficulty(difficulty):
    return [p for p in PROMPTS_DATABASE if p['difficulty'] == difficulty]

def search_prompts(query):
    query_lower = query.lower()
    return [p for p in PROMPTS_DATABASE if query_lower in p['title'].lower() or any(query_lower in tag.lower() for tag in p['tags'])]

def get_categories():
    return sorted(list(set(p['category'] for p in PROMPTS_DATABASE)))

def get_tags():
    tags = set()
    for prompt in PROMPTS_DATABASE:
        tags.update(prompt['tags'])
    return sorted(list(tags))
