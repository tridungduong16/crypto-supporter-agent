from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from src.agents.langchain_agent_serve import CryptoSupporterAgent

# Initialize FastAPI app
app = FastAPI()

# Initialize CryptoSupporterAgent
agent = CryptoSupporterAgent()

# Request model for input
class MessageRequest(BaseModel):
    message: str

# Response model for output
class MessageResponse(BaseModel):
    response: str

@app.get("/")
async def root():
    """Root endpoint to check the API status."""
    return {"message": "Crypto Supporter Agent is running!"}

@app.post("/ask", response_model=MessageResponse)
async def process_message(request: MessageRequest):
    """
    Endpoint to process a message through the CryptoSupporterAgent.
    """
    agent_response = agent.process_message(request.message)
    return MessageResponse(response=agent_response)

    # try:
    #     # Process the user message
    #     agent_response = []
    #     config = {"configurable": {"thread_id": "1"}}
    #     response_stream = agent.react_graph.stream(
    #         {"messages": [("user", request.message)]}, config, stream_mode="values"
    #     )
        
    #     for event in response_stream:
    #         last_message = event["messages"][-1].content
    #         agent_response.append(last_message)
    #     return MessageResponse(response=" ".join(agent_response))
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
