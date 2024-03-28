from langchain_community.llms import ChatGLM
from langchain.chains import LLMMathChain, LLMChain
from langchain.prompts import PromptTemplate
from langchain.agents.agent_types import AgentType
from langchain.agents import Tool, initialize_agent


chatglm_server_url = "http://192.168.0.127:5000/chat"
llm = ChatGLM(endpoint_url=chatglm_server_url,
              max_token=8000,
              #history=[['']],
              top_p=0.9,
              model_kwargs={"sample_model_args": False})

word_problem_template = """你是一个推理代理，负责解决用户基于逻辑的问题。
从逻辑上得出解决方案，并实事求是。在你的答案中，清楚地详细说明所涉及的步骤，并给出最终的答案。
用要点来回答问题。问题 {question} 答案"""

math_assistant_prompt = PromptTemplate(
    input_variables=["question"],
    template=word_problem_template
)

word_problem_chain = LLMChain(llm=llm,
                              prompt=math_assistant_prompt)
word_problem_tool = Tool.from_function(name="Reasoning Tool",
                                       func=word_problem_chain.run,
                                       description="当你需要回答基于逻辑或推理的问题时很有用",
                                    )

problem_chain = LLMMathChain.from_llm(llm=llm)
math_tool = Tool.from_function(name="Calculator",
                               func=problem_chain.run,
                               description=" 当你需要回答数字问题时很有用。这个工具只适用于数学问题。只输入数学表达式，不输入文本",
                               )

agent = initialize_agent(
    tools=[math_tool, word_problem_tool],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=False,
    handle_parsing_errors=True
)

if __name__ == '__main__':
    print(agent.invoke({'input':'1000的平方根是多少?'}))
    print(agent.invoke({'input':'小明的姐姐比他大10岁。小明出生在新中国刚成立的时候。小明的姐姐是什么时候出生的?'}))
