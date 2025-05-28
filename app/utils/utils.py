from app.models.schemas.message import ContentAi

def content_ai_to_string(content_ai: ContentAi) -> str:
    """
    Convert ContentAi object to a string representation.
    """
    parts = []
    if content_ai.content_analysis:
        parts.append(f"Analysis: {content_ai.content_analysis}")
    if content_ai.content_comment:
        parts.append(f"Comment: {content_ai.content_comment}")
    if content_ai.content_code:
        parts.append(f"Code: {content_ai.content_code}")
    if content_ai.content_executable_code:
        parts.append(f"Executable Code: {content_ai.content_executable_code}")

    return "\n".join(parts) if parts else "No content available"