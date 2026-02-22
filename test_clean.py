from src.api.qa import answer_question, stream_answer_question

print("Test QA:")
res = answer_question(
    "hello there I currently have a problem with my sim I keep losing signal during calls whats the cause"
)
print(res["answer"])
