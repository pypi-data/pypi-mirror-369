from asta_summarizer.models.SummarizationType import SummarizationType

thread_tile_prompt = "Given the first message of a conversation, generate a short title for what the conversation is about.\n\n"


def get_summary_prompt_for_type(summarization_type: SummarizationType) -> str:
    if summarization_type == SummarizationType.THREAD_TITLE:
        return thread_tile_prompt
    else:
        return ""
