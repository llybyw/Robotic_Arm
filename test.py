from utils_agent import *


AGENT_PROMPT = '请先回到原点，再把绿色立方体放到李云龙上'
prompt_text = AGENT_SYS_PROMPT + AGENT_PROMPT
messages = [{
    'role': 'user',
    'content': [
        {
            'text': prompt_text
        },
    ]
}]

generated_text = generate_plan(messages)
print(generated_text)

