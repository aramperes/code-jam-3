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
  **Payload**: *none*

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
      "name": "<name>"
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
    "state": "view",
    "lobby_id": "<lobby id>"
  }
  ```
  
  ```json
  {
    "state": "join",
    "lobby_id": "<lobby id>"
  }
  ```

### `c-s lobby:create`

  **Payload**:

  ```json
  {
    "name": "<name>",
    "max_players": 2
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
        "start_time": "<start timestamp | null>",
        "max_players": 2,
        "users": [
          {
            "name": "<user name>",
            "ready": false
          }
        ]
      }
    ]
  }
  ```

### `s-c lobby:response`

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
    "from": "<user name>",
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
