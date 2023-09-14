from fastapi import FastAPI, HTTPException
from utilties.unique_identifier import gen_id
from classes.validation import ValidationError
from classes.event import Event
from classes.events import Events
from classes.department import Department
from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["http://172.30.192.1:10000"]

# app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
# List to store WebSocket connections
websocket_connections = []

event = None

signature = gen_id()

@app.get('/')
async def get_event():
    return event

@app.get('/get_event_raw')
async def get_event_raw():
    return event.raw

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    websocket_connections.append(websocket)

    while True:
        try:
            msg = await websocket.receive_json()
            action = msg.get("action")

            #print(data)

            if action == "create_event":
                data = msg.get("event")
                await create_event(websocket, data)

            elif action == "ping":
                await websocket.send_json(msg)

            elif action == "check_in":
                data = msg.get("checkin_data")
                await check_in(data)

            elif action == "get_event":
                await get_event(websocket)

            elif action == "delete_event":
                await delete_event(websocket)

            else:
                msg = {"point": "server_updates_error", "error": "Invalid action"}
                await websocket.send_json(msg)

        except HTTPException as e:
            msg = {"point": "server_updates_error", "error": str(e)}
            await broadcast(msg)

        except Exception as e:
            msg = {"point": "server_updates_error", "message": "An error occurred", "error":str(e)}
            await broadcast(msg)
            print(str(e))

async def broadcast(msg):
    # Append server UID
    msg["uid"] = signature

    # Broadcast event to all connected clients
    for connection in websocket_connections:
        await connection.send_json(msg)

async def get_event(websocket: WebSocket):
    msg = {"point": "server_updates_event_info", 'event_title': event.event_title, 'event_code': event.event_code, 'uid': signature}
    await websocket.send_json(msg)

async def create_event(websocket: WebSocket, event_data: dict):
    global event
    print(event_data)
    event_code = event_data.get('event_code')
    event_title = event_data.get('event_title')
    event = Event(event_code, event_title)
    msg = {"point": "server_updates_event_creation", 'message': 'Event created successfully', 'uid': signature}
    await websocket.send_json(msg)

async def check_in(checkin_data: dict):
    global event
    try:
        event.check_in(checkin_data) #TODO: <---- work to do here
        msg = {"point": "server_updates_checkin", 'message': 'Check-in successful', 'data': checkin_data, 'event_title':event.event_title, 'event_code':event.event_code}
        await broadcast(msg)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# TODO
async def delete_event(websocket: WebSocket):
    global event
    try:
        event.end_event()
        del event
        msg = {"point": "server_updates_event_delete", 'message': 'Event ended and removed successfully'}
        await broadcast(msg)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    else:
        msg = {"point": "server_updates_event_delete", "message": "Event not found", 'uid': signature}
        await websocket.send_json(msg)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5000)