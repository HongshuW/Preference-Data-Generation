from ..utils import gpt_querier as llm

response = llm.generate_gpt_response("Split the following paragraph into claims, then convert each claim to a question that can be answered by True or False.\"This is the dog sitting on the floor. This looks like a wooden object. I think these are the stairs.\"")
print(response)
