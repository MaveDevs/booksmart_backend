# booksmart_backend
Backend for our project

# install venv
python -m venv .venv

# activate venv(windows command)
.\.venv\Scripts\activate

# to install requirements: 
pip install -r requirements.txt 

# change the .env and alambic.ini files to the credentials of your own mysql db (db has to be created before you run the migrations from bellow)

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