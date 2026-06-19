from dotenv import load_dotenv
from agent import agent

load_dotenv()

def run(query: str):
    config = {
        "configurable": {
            "thread_id": "user_123"
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

if __name__ == "__main__":
    # run("Analyze the YouTube channel of MrBeast.")
    # run("What content strategy is helping MrBeast grow so fast?")
    # run("What are the top-performing video categories on Mr.Beast channel?")
    # run("How often does this channel upload videos?")
    # run("What is the audience targeting strategy of this channel?")
    # run("Summarize the evolution of this channel over the last 2 years.")
    # run("What are the common patterns among the top 20 videos on this channel?")
    # run("Compare this channel with its top competitors.")
    # run("What is the last uploaded video on Mrbeast channel? Summarize its content and analyze its performance so far.")
    run('Summarize the video titled "50 youtube legends fight" on MrBeast channel')

    