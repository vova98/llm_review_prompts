from openai import OpenAI
from pydantic import BaseModel, conint
from prompts import (
    JUDGE_PROMPT,
    JUDGE_SYSTEM_PROMPT,
    REVIEW_PROMPT, 
    REVIEW_SYSTEM_PROMPT
)


class Comment(BaseModel):
    comment: str
    fixed_code_snippet: str
    necessity: conint(ge=1, le=5)
    line: int


class Review(BaseModel):
    programming_best_practices: list[Comment] = []
    bug_fixes: list[Comment] = []
    modern_python_features: list[Comment] = []
    optimization: list[Comment] = []


def llm_as_a_judge_engine(
    client: OpenAI, 
    model_name: str,
    file_context: str,
    method_context: str,
    affected_context: str,
    review: str,
    commit_msg: str,
):
    prompt = JUDGE_PROMPT.format(
        file_context=file_context,
        method_context=method_context,
        affected_context=affected_context,
        review=review,
        commit_msg=commit_msg,
    )

    messages = [
        {'role': 'system', 'content': JUDGE_SYSTEM_PROMPT},
        {'role': 'user', 'content': prompt},
    ]

    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        max_tokens=500,
        temperature=0.0,
    )
    return response.choices[0].message.content

def review_engine(
        client: OpenAI, 
        model_name: str, 
        code_context: str, 
        few_shot_samples: str
    ) -> Review:
    prompt = REVIEW_PROMPT.format(
        code_context=code_context,
        schema=Review.model_json_schema(),
    )
    messages = [
        {'role': 'system', 'content': REVIEW_SYSTEM_PROMPT + few_shot_samples},
        {'role': 'user', 'content': prompt},
    ]
    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        max_tokens=3000,
        temperature=0.0,
        response_format={
            'type': 'json_object',
            'value': Review.model_json_schema(),
        },
    )
    return response.choices[0].message.content
