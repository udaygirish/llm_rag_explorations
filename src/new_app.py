from langchain_ollama import ChatOllama

llm = ChatOllama(
    model = "llama3.1",
    temperature = 0.8,
    num_predict = 256,
)


messages = [
    ("system", "You are a helpful translator. Translate the user sentence to French."),
    ("human", "I love programming."),
]
ai_msg = llm.invoke(messages)
print("AI Response:", ai_msg.content)















# from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
# from langchain_huggingface import HuggingFacePipeline

# # llm = HuggingFaceEndpoint(
# #     repo_id="meta-llama/Meta-Llama-3-8B",
# #     task="text-generation",
# #     max_new_tokens=512,
# #     do_sample=False,
# #     repetition_penalty=1.03,
# # )

# llm = HuggingFacePipeline(
#     model="meta-llama/Meta-Llama-3-8B",
#     task="text-generation",
# )

# chat_model = ChatHuggingFace(llm=llm)


# from langchain_core.messages import (
#     HumanMessage,
#     SystemMessage,
# )

# messages = [
#     SystemMessage(content="You're a helpful assistant"),
#     HumanMessage(
#         content="What happens when an unstoppable force meets an immovable object?"
#     ),
# ]

# ai_msg = chat_model.invoke(messages)
# print(ai_msg.content)