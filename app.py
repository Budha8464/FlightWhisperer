import requests
import os
import json
from dotenv import load_dotenv
import openai
load_dotenv()
import streamlit as st
from groq import Groq

client = Groq(
    api_key=os.getenv("GROQ_API_KEY"),
)

def get_flight(departure_id, arrival_id, outbound_date, return_date):
    base_url = "https://serpapi.com/search"
    params = {
        "engine": "google_flights",
        "departure_id": departure_id,
        "arrival_id": arrival_id,
        "api_key": os.getenv("SERP_API_KEY"),
        "outbound_date": outbound_date,
        "return_date": return_date  
    }
    
    response = requests.get(base_url, params=params)
    return response.json()


tools=[
    {
    "type": "function",
    "function": {
        "name": "get_flight",
        "description": "Get available flights between two locations for given dates",
        "parameters": {
            "type": "object",
            "properties": {
                "departure_id": {
                    "type": "string",
                    "description": "The IATA code of the departure airport, e.g. SFO"
                },
                "arrival_id": {
                    "type": "string",
                    "description": "The IATA code of the arrival airport, e.g. JFK"
                },
                "outbound_date": {
                    "type": "string",
                    "format": "date",
                    "description": "The departure date in YYYY-MM-DD format"
                },
                "return_date": {
                    "type": "string",
                    "format": "date",
                    "description": "The return date in YYYY-MM-DD format"
                }
            },
            "required": ["departure_id", "arrival_id", "outbound_date", "return_date"]
        }
    }
}
]


def get_answer(input_text,client):
    response = client.chat.completions.create(
    model="llama3-70b-8192",
    messages=[
        {
            "role": "system",
            "content": "You are a helpful flight booking assistant. From the given input, I want you to extract the 3 letter airport code for the Origin airport and the Destination airport. Also give an origin date and return date. If no year is mentioned, then the year is 2024. Dates should be in YYYY-MM-DD format.\n\nQ: I want to travel from Kolkata to Amsterdam. I will travel from 23rd March to 4th April.\nA: \nOrigin: CCU\nDestination: AMS\nOrigin date: 2024-03-23\nReturn date: 2024-04-04"
        },
        {
            "role": "user",
            "content": input_text
        },
    ],
    temperature=1,
    max_tokens=1024,
    tools=tools,
    tool_choice="auto"
   )

 # print(json.loads(response['choices'][0]['message']['tool_calls'][0]['function']['arguments']))


 # groq_resp=json.loads(response)
 # arguments = response['choices'][0]['message']['tool_calls'][0]['function']['arguments']

 # print(arguments)
 # response.tool_calls[0].function.arguments

 # We can now capture the arguments:

    groq_response = response.choices[0].message
    args = json.loads(groq_response.tool_calls[0].function.arguments)
 # print(args)

 # print("output")
 # print(get_current_weather(**args))
    flights=get_flight(**args)
 # print(flights)
 # # #  Put this into another LLM call and return the response in text format
    response2 = openai.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
    {
        "role": "system",
        "content": "You are a helpful flight booking assistant. From the given JSON file, give a breakdown of the flight options. If there is an error, explain the error in a professional but fun tone. For each result, don't give the Airline Logo line. Then give a final conclusion with reasons for the best option."
    },
    {
            "role": "user",
            "content": json.dumps(flights)
        }
    ],
    temperature=1,
    max_tokens=1024,
    
    )

    openai_response = response2.choices[0].message.content
    return openai_response

def main():
    st.title("FlightWhisperer")
    st.caption("Hi, I am a Flight booking wizard. Ask me anything!")
    client = Groq(
        api_key=os.getenv("GROQ_API_KEY"),
        )
    # User input
    # st.write("Hi, I am a weather chatbot. Ask me anything!")
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])
        
    # input_text = st.text_input("Type in your question")

    # Ask me button
    if prompt := st.chat_input():
    

        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        response = get_answer(prompt,client)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.chat_message("assistant").write(response)
if __name__ == "__main__":
    main()
