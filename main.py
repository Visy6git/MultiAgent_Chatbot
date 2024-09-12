import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os
import shelve

# Load environment variables
load_dotenv()
grok_key = os.getenv('GROQ_API_KEY')
groq_client = Groq(api_key=grok_key)

if "groq_model" not in st.session_state:
    st.session_state["groq_model"] = "llama3-70b-8192"

USER_AVATAR = "👤"
BOT_AVATAR = "🤖"

# Load chat history from shelve file
def load_chat_history():
    with shelve.open("chat_history") as db:
        return db.get("messages", [])

# Save chat history to shelve file
def save_chat_history(messages):
    with shelve.open("chat_history") as db:
        db["messages"] = messages

if 'messages' not in st.session_state:
    st.session_state['messages'] = load_chat_history()  # Load history into session state if not already

with st.sidebar:
    if st.button("Delete Chat History"):
        st.session_state.messages = []
        save_chat_history([])

# Component and System Agent
def component_system_agent(prompt):
    sys_msg = (
        "You are an autonomous agent responsible for managing and optimizing key electric vehicle (EV) components and systems, ensuring seamless integration, performance, and compliance. "
        "Your role includes overseeing battery packs, Battery Management Systems (BMS), supercapacitors, energy storage, and thermal management systems, as well as managing powertrain components like motors, power electronics, and transmissions."
    )
    function_convo = [{'role': 'system', 'content': sys_msg}, {'role': 'user', 'content': prompt}]
    chat_completion = groq_client.chat.completions.create(messages=function_convo, model='llama3-70b-8192')
    return chat_completion.choices[0].message.content, "Component & System Agent"

# Testing and Validation Agent
def testing_validation_agent(prompt):
    sys_msg = (
        "You are an autonomous agent responsible for testing and validating electric vehicle (EV) components and systems. "
        "Your role includes conducting electrical, battery, charger, and software/cybersecurity tests to ensure compliance with industry standards."
    )
    function_convo = [{'role': 'system', 'content': sys_msg}, {'role': 'user', 'content': prompt}]
    chat_completion = groq_client.chat.completions.create(messages=function_convo, model='llama3-70b-8192')
    return chat_completion.choices[0].message.content, "Testing & Validation Agent"

# Regulatory and Compliance Agent
def regulatory_compliance_agent(prompt):
    sys_msg = (
        "You are an autonomous agent responsible for ensuring regulatory compliance of electric vehicles (EVs). "
        "Your role involves ensuring compliance with safety, environmental, and performance standards, including ISO, IEC, NEMA, and other global regulations."
    )
    function_convo = [{'role': 'system', 'content': sys_msg}, {'role': 'user', 'content': prompt}]
    chat_completion = groq_client.chat.completions.create(messages=function_convo, model='llama3-70b-8192')
    return chat_completion.choices[0].message.content, "Regulatory & Compliance Agent"

# Market Analysis and Policy Agent
def market_analysis_policy_agent(prompt):
    sys_msg = (
        "You are an autonomous agent responsible for analyzing the electric vehicle (EV) market and monitoring government policies and incentives. "
        "Your role includes studying market trends, policy changes, and consumer demands, as well as tracking the latest incentives and collaborations in the EV ecosystem."
    )
    function_convo = [{'role': 'system', 'content': sys_msg}, {'role': 'user', 'content': prompt}]
    chat_completion = groq_client.chat.completions.create(messages=function_convo, model='llama3-70b-8192')
    return chat_completion.choices[0].message.content, "Market Analysis & Policy Agent"

# Main Agent to synthesize responses, includes chat history for memory
def main_agent(prompt, response):
    sys_msg = (
        "You are the main agent responsible for analyzing electric vehicle (EV)-related queries. You will help the user with answers that are to the point, precise, and easy to understand. "
        "You will collaborate with other agents' responses to form the best possible response to the user's query. Be empathetic and helpful to the user. Your answers will be in points simplistic and readable less words than the context"
    )

    # Use the full chat history as context, including previous user/assistant exchanges
    conversation_history = "\n".join(
        [f"{msg['role'].upper()}: {msg['content']}" for msg in st.session_state['messages']]
    )
    
    # Pass the entire chat history with the new prompt
    prompt = (f'USER PROMPT: {prompt}\n\n RELATED CONTEXT: {response} \n\n Conversation History:\n{conversation_history}')
    function_convo = [{'role': 'system', 'content': sys_msg}, {'role': 'user', 'content': prompt}]
    chat_completion = groq_client.chat.completions.create(messages=function_convo, model='llama3-70b-8192')
    
    return chat_completion.choices[0].message.content

# Classifier Agent that routes queries to the appropriate agent
def classifier_agent(prompt):
    sys_msg = (
        'You are an AI function calling model. You will determine whether the prompt is related to "Component & Systems of electric vehicles", '
        '"Testing & Validation in electric vehicles", "Regulatory & Compliance in electric vehicles", "Market Analysis & Policy Agent in electric vehicles", or "None". '
        'You will respond with only one selection from this list: ["component_system_agent", "testing_validation_agent", "regulatory_compliance_agent", "market_analysis_policy_agent", "None"]. '
        'Do not respond with anything but the most logical selection from that list with no explanations.'
    )
    function_convo = [{'role': 'system', 'content': sys_msg}, {'role': 'user', 'content': prompt}]
    chat_completion = groq_client.chat.completions.create(messages=function_convo, model='llama3-70b-8192')
    
    return chat_completion.choices[0].message.content

# Display chat messages
for message in st.session_state['messages']:
    avatar = USER_AVATAR if message['role'] == 'user' else BOT_AVATAR
    with st.chat_message(message['role'], avatar=avatar):
        st.markdown(message['content'])

# Main chat interface
if prompt := st.chat_input("How can I help?"):
    st.session_state['messages'].append({"role": "user", "content": prompt})

    # Display user message
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(prompt)
    
    with st.chat_message("assistant", avatar=BOT_AVATAR):
        message_placeholder = st.empty()

    # Classify the prompt and get the respective agent's response
    classified_agent = classifier_agent(prompt)

    # Route the prompt to the appropriate agent based on classifier response
    if classified_agent == "component_system_agent":
        response, agent_name = component_system_agent(prompt)
    elif classified_agent == "testing_validation_agent":
        response, agent_name = testing_validation_agent(prompt)
    elif classified_agent == "regulatory_compliance_agent":
        response, agent_name = regulatory_compliance_agent(prompt)
    elif classified_agent == "market_analysis_policy_agent":
        response, agent_name = market_analysis_policy_agent(prompt)
    else:
        response, agent_name = "None", "Main Agent"

    # Synthesize final response from main agent using memory and context
    main_response = main_agent(prompt, response)
    st.session_state['messages'].append({"role": "assistant", "content": main_response})

    # Display the classifier and agent response with memory
    with st.expander(f"Classifier categorized the prompt under: {agent_name}"):
        st.write(response)
    
    with st.chat_message("assistant", avatar=BOT_AVATAR):
        st.markdown(main_response)

# Save chat history after interaction
save_chat_history(st.session_state['messages'])
