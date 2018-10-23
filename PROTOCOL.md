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
      "id": "<id>",
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

### `c-s lobby:state`

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

### `s-c lobby:update_list`

  **Payload**:
  
  ```json
  [
    {
      "lobby_id": "<id>",
      "state": "open|closed",
      "created_time": "<creation timestamp>",
      "start_time": "<start timestamp | null>",
      "users": ["user_a", "user_b"]
    }
  ]
  ```

### `s-c lobby:join_response`

  **Payload**:
  
  ```json
  {
    "lobby_id": "<lobby id>",
    "joined": true
  }
  ```

### `s-c lobby:chat_recv`

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
