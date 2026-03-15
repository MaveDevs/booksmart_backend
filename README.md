# booksmart_backend
Backend for our project

# install venv
python -m venv .venv

# activate venv(windows command)
.\.venv\Scripts\activate

# to install requirements: 
pip install -r requirements.txt 

# change the .env and alambic.ini files to the credentials of your own mysql db (db has to be created before you run the migrations from bellow)

# optional Sentry variables for error monitoring
# SENTRY_DSN=https://<key>@<org>.ingest.sentry.io/<project>
# SENTRY_ENVIRONMENT=development
# SENTRY_TRACES_SAMPLE_RATE=0.0
# SENTRY_PROFILES_SAMPLE_RATE=0.0
# SENTRY_SEND_DEFAULT_PII=false

# to get the db populated(terminal with venv activated):
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head

# to run server:
uvicorn app.main:app --reload

# api documents: 
http://127.0.0.1:8000/docs#/

#to get access first login with endpoint auth>login>access-token and then input the given token in authorize 

How clients connect
wss://your-domain.com/api/v1/ws?token=<JWT>

Flutter 
final channel = WebSocketChannel.connect(
  Uri.parse('wss://your-domain.com/api/v1/ws?token=$jwt'),
);
channel.stream.listen((event) {
  final data = jsonDecode(event);
  // data['type'] is "notification", "message", "appointment", etc.
});

React
const ws = new WebSocket(`wss://your-domain.com/api/v1/ws?token=${jwt}`);
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'notification') { /* update UI */ }
};

Python client
import websockets, asyncio
async def listen():
    async with websockets.connect(f"wss://your-domain.com/api/v1/ws?token={jwt}") as ws:
        async for msg in ws:
            print(msg)

Sentry
- Install dependencies with `pip install -r requirements.txt`.
- Add `SENTRY_DSN` to your runtime environment or `.env`.
- Optional variables: `SENTRY_ENVIRONMENT`, `SENTRY_RELEASE`, `SENTRY_TRACES_SAMPLE_RATE`, `SENTRY_PROFILES_SAMPLE_RATE`, `SENTRY_SEND_DEFAULT_PII`.
- If `SENTRY_DSN` is missing, Sentry stays disabled.