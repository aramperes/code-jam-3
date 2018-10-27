# Protocol Documentation

## Frame

**Payload**:

```json
{
  "op": "<protocol>:<action>",
  "session": "<session token given by server>",
  "payload": { }
}
```

## `handshake`

### `s-c handshake:ready`
  **Payload**:
  
  ```json
  {
    "server_time": 1540549944
  }
  ```

### `c-s handshake:identify`

  **Payload**:
  
  *If no token is provided, the server will assume this is a new user.*
  ```json
  {
    "token": "<user token>"
  }
  ```

  ```json
  {
    "token": null
  }  
  ```
  
### `s-c handshake:user_info`

  **Payload**:
  ```json
  {
    "user": {
      "token": "<token>",
      "name": "<name>#<discrim>"
    }
  }
  ```

### `s-c handshake:prompt_new_user`

  **Payload**:
  ```json
  {
    "transaction_id": "<transaction id>"
  }
  ```

### `c-s handshake:new_user`

  **Payload**:
  ```json
  {
    "transaction_id": "<transaction id>",
    "name": "<name>"
  }
  ```

### `s-c handshake:upgrade`

**Payload**: *none*

## `lobby`

### `c-s lobby:set_state`

  **Payload**:
  
  *One of:*
  
  ```json
  {
    "state": "list"
  }
  ```

  ```json
  {
    "state": "join",
    "lobby_id": "<lobby id>"
  }
  ```

### `c-s lobby:config`

  *Note: This message is used for both creating and updating (**not implemented**) a lobby. If no ID is provided,*
  *the server will assume it is a new lobby.*

  **Payload**:

  ```json
  {
    "name": "<name>",
    "max_players": 2,
    "lobby_id": "<lobby id>|null"
  }
  ```

### `s-c lobby:config_response`

  **Payload**:

  ```json
  {
    "lobby_id": "<lobby_id>|null",
    "error": "<message>|null"
  }
  ```

### `s-c lobby:update_list`

  **Payload**:
  
  ```json
  {
    "lobbies": [
      {
        "id": "<id>",
        "name": "<name>",
        "open": true,
        "created_time": "<creation timestamp>",
        "start_time": "<start timestamp>|null",
        "max_players": 2,
        "players": [
          {
            "name": "<user_name>#<discrim>",
            "ready": false
          }
        ]
      }
    ]
  }
  ```
  

### `s-c lobby:join_response`

  **Payload**:
  
  ```json
  {
    "lobby_id": "<lobby id>",
    "joined": true
  }
  ```

### `s-c lobby:chat_broadcast`

  **Payload**:
  
  ```json
  {
    "user_name": "<user_name>#<discrim>",
    "message": "<message>"
  }
  ```

### `c-s lobby:chat_send`

  **Payload**:
  
  ```json
  {
    "message": "<message>"
  }
  ```

### `c-s lobby:user_ready`

  **Payload**:
  
  ```json
  {
    "ready": true
  }
  ```

### `c-s lobby:quit`

  **Payload**: *none*

### `s-c lobby:transfer`

  **Not currently implemented.**

  *This message is sent when it is no longer the gateway's task to handle the connection.*

  **Payload**:
  ```json
  {
    "target": "ws://localhost:8081/game/",
    "track_token": "<token defined by the target>"
  }
  ```
