import streamlit as st
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import urllib.parse as urlparse
import streamlit.components.v1 as components

# Function to execute when a session ends
def perform_cleanup(session_id):
    print(f"Performing cleanup actions for session: {session_id}")
    # Add any other necessary cleanup actions here

# Initialize Session State
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if 'current_active' not in st.session_state:
    st.session_state.current_active = True
if 'counter' not in st.session_state:
    st.session_state.counter = 0

# Display the current session status
st.write(f"Session ID: {st.session_state.session_id}")
st.write(f"Counter: {st.session_state.counter}")

# JavaScript to detect page unload
js_code = f"""
<script>
    function notifyServer() {{
        fetch('http://localhost:8000/end_session?session_id={st.session_state.session_id}', {{method: 'GET'}});
    }}
    window.addEventListener('beforeunload', notifyServer);
</script>
"""
components.html(js_code, height=0)

# Custom handler for HTTP server
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/end_session'):
            query_components = urlparse.parse_qs(urlparse.urlparse(self.path).query)
            session_id = query_components.get("session_id", [None])[0]
            if session_id:
                print(f"Session {session_id} ended")
                perform_cleanup(session_id)
                st.session_state.current_active = False

        self.send_response(200)
        self.end_headers()

# Start HTTP server in a separate thread
def start_server():
    server = HTTPServer(('localhost', 8000), SimpleHandler)
    server.serve_forever()

server_thread = threading.Thread(target=start_server)
server_thread.daemon = True
server_thread.start()

# Simulate session activity
st.session_state.counter += 1

# Monitor session activity and perform actions
if not st.session_state.current_active:
    st.write("Session has been marked as ended. Performing necessary actions.")
    st.experimental_rerun()  # Example of triggering re-run or logging out
else:
    st.write("Session still active.")