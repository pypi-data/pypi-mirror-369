import json
import re
from fastapi import HTTPException

import requests
from loguru import logger
from ai_gateway.config import config
from ai_gateway.schemas.errors import HttpStatusCode


def citics_gpt(messages, model=config.llm.default_model, temperature=0.0) -> dict:
    """调用中信llm api
    """
    url = config.llm.url
    # 要发送的数据
    data = {
        "messages": messages,
        "model": model,
        "stream": False,
        "temperature": temperature,
    }
    api_key = config.llm.api_key
    # 请求头
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    result = {}
    for i in range(max(1, config.llm.retry_count)):
        try:
            response = requests.post(url, data=json.dumps(data), headers=headers, timeout=30)
            result = response.json()["choices"][0]["message"]
            # logger.info(f"{i}:Successfully retrieved result from citics_gpt.")
            break
        except Exception as e:
            logger.error(f"{i}:Fail retrieved result from citics_gpt. error: {e}")
    if len(result) == 0:
        raise HTTPException(
            status_code=HttpStatusCode.SERVICE_UNAVAILABLE_503,
            detail="Fail retrieved result from citics_gpt."
        )
    return result


def citics_gpt_dict(prompt, model=config.llm.default_model) -> dict:
    """calling citics llm api
    """
    result_dict = {}
    message = [{"role": "user", "content": prompt}]
    response = citics_gpt(message, model=model)
    result = response.get('content')
    if not result:
        logger.error(f"GPT api failed result: {result}")
        return result_dict
    try:
        result_dict = json.loads(result)
    except json.JSONDecodeError as e:
        # 检查result中是否包含json格式
        pattern = r"\{[^{}]*\}"
        match = re.search(pattern, result, re.S)
        logger.warning(f"json.loads error, use Re try to extract json object with result: {result}")
        if match:
            try:
                result_dict = json.loads(match.group())
            except json.JSONDecodeError as json_err:
                logger.info(f"match.group is {match.group()}")
                logger.error(json_err)
        else:
            logger.error(f"GPT failed result: {result}, error_info: {e}")
    return result_dict


if __name__ == "__main__":
    res = citics_gpt(
        [{"role": "user", "content": "你好，你是谁？"}],
        model="qwen2"
    )
    print(res)
