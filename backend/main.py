from dotenv import load_dotenv
from agent import agent
from fastapi import FastAPI


load_dotenv()


app = FastAPI(
    title="YouTube Channel Analysis Agent", 
    version="1.0.0"
)


@app.get("/")
async def root():
    return {"message": "Welcome to the YouTube Channel Analysis Agent!"}


@app.post("/chat")
async def chat(query: str, user_id: str):

    response = run(query, user_id)

    return {
        "message": "Query processed successfully. Check the console for the agent's response.",
        "success": True,   
        "query": query,
        "response": response
    }



def run(query: str, user_id: str):
    config = {
        "configurable": {
            "thread_id": user_id
        }
    }

    # The agent takes a list of messages, just like a chat
    result = agent.invoke({
        "messages": [
            {"role": "user", "content": query}
        ]
    }, config=config)

    print(result)
    # The final message in the list is the agent's answer
    final_answer = result["messages"][-1].content
    print("\n🤖 Agent Response:\n")
    print(final_answer)

    return final_answer


if __name__ == "__main__":
    # run("Analyze the YouTube channel of MrBeast", 1)
    # run("Summarize this video for me: https://youtu.be/wvNgKx2e_LA?si=wPdDuTYJR4R3Wqkd", 1)
    run("what are the main topics of this video", 1)
    # run("What content strategy is helping MrBeast grow so fast?")
    # run("What are the top-performing video categories on Mr.Beast channel?")
    # run("How often does this channel upload videos?")
    # run("What is the audience targeting strategy of this channel?")
    # run("Summarize the evolution of this channel over the last 2 years.")
    # run("What are the common patterns among the top 20 videos on this channel?")
    # run("Compare this channel with its top competitors.")
    # run("What is the last uploaded video on Mrbeast channel? Summarize its content and analyze its performance so far.")
    # run('Summarize the video titled "50 youtube legends fight" on MrBeast channel')

    