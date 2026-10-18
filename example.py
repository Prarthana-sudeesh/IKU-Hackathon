import os
import signal
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation, ClientTools
from elevenlabs.conversational_ai.default_audio_interface import DefaultAudioInterface

load_dotenv()

AGENT_ID = "agent_6401m550c7m5f4jt78f4gvf06h7b"

# ---- Accessibility database (add more buildings here) ----
BUILDINGS = {
    "main entrance": "Main Entrance Building: step-free access to reception. 8 steps with handrails on both sides up to the College Café and Alumni Visitors Centre.",
    "library": "Abdus Salam Library: step-free access at both the main entrance and the café entrance.",
    "flowers": "Flowers Building: ramped entrance. Accessible toilet with level access.",
}
STATIONS = {
    "south kensington": "NOT step-free. Stairs only. Do not route wheelchair users here.",
}
HAZARDS = [
    "Exhibition Road is a shared surface with no traditional kerbs. Stay close to the building side.",
    "Exhibition Road can have heavy museum crowds, especially weekends and school holidays.",
]

def lookup(table, query):
    q = (query or "").lower()
    for key, value in table.items():
        if key in q or q in key:
            return value
    return "No data for that yet. Suggest asking at reception or staff."

# ---- Tools: names must match your agent's tools exactly ----
client_tools = ClientTools()
client_tools.register("get_accessibility_info", lambda p: lookup(BUILDINGS, p.get("building")))
client_tools.register("get_lift_status", lambda p: lookup(STATIONS, p.get("station")))
client_tools.register("get_hazards", lambda p: " ".join(HAZARDS))

elevenlabs = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

conversation = Conversation(
    elevenlabs,
    AGENT_ID,
    requires_auth=True,
    audio_interface=DefaultAudioInterface(),
    client_tools=client_tools,
    callback_agent_response=lambda text: print(f"Agent: {text}"),
    callback_user_transcript=lambda text: print(f"You: {text}"),
)

print("Starting... talk to your agent. Press Ctrl + C to stop.")
conversation.start_session()
signal.signal(signal.SIGINT, lambda sig, frame: conversation.end_session())
conversation_id = conversation.wait_for_session_end()
print(f"Conversation ended. ID: {conversation_id}")