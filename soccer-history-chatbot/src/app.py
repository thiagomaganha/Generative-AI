import gradio as gr
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage

#Load Chroma vector database
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
db = Chroma(persist_directory="chroma_store", embedding_function=embeddings)
retriever = db.as_retriever(search_kwargs={"k":3})

#Custom prompt template
custom_prompt = """
You are a helpful assistant specialized in soccer history.
Use the provided context to answer the question.
If the answer is not in the context, respond with "I don't know."

Context:
{context}
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", custom_prompt),
    ("human", "{input}")
])

#Setup LLM model 
llm = ChatOpenAI(
    temperature=0,
    model="gpt-4o-mini",
    max_tokens=1000,        
    timeout=30,             
    max_retries=3,          
    streaming=True          
)

question_answer_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)

chat_history = []
chat_history_messages = []

def chat(query, history):
    global chat_history

    chat_history_for_chain = []
    for human_msg, ai_msg in chat_history:
        chat_history_for_chain.append(HumanMessage(content=human_msg))
        chat_history_for_chain.append(AIMessage(content=ai_msg))

    result = rag_chain.invoke({
        "input": query,
        "chat_history": chat_history_for_chain
    })

    chat_history.append((query, result["answer"]))

    sources = []
    for doc in result["context"]:
        src = doc.metadata.get("source", "unknown")
        page = doc.metadata.get("page", "N/A")
        sources.append(f"{src} (page {page})")
    citation_text = "\n\nSources:\n" + "\n".join(set(sources)) if sources else ""

    chat_history_messages.append({"role": "user", "content": query})
    chat_history_messages.append({"role": "assistant", "content": result["answer"] + citation_text})

    return "", chat_history_messages 

with gr.Blocks() as client:
    gr.Markdown("## 📚 The World Cup history chatbot")
    chatbot_ui = gr.Chatbot(type="messages")
    msg = gr.Textbox(placeholder="Ask me about the history of soccer and the FIFA World Cups...")
    clear = gr.Button("Clear Chat")

    # Submit query
    msg.submit(chat, [msg, chatbot_ui], [msg, chatbot_ui])

    # Clear chat history
    def reset_chat():
        global chat_history, chat_history_messages
        chat_history = []
        chat_history_messages = []
        return []

    clear.click(reset_chat, None, chatbot_ui, queue=False)

client.launch(share=True)