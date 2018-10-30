# Protocol Documentation

## Frame

**Payload**:

```json
{
  "op": "<protocol>:<action>",
  "session": "<session token given by gateway>",
  "payload": { }
}
```

## `handshake` (gateway)

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

## `lobby` (gateway)

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

  *This message is sent when it is no longer the gateway's task to handle the connection.*

  **Payload**:
  ```json
  {
    "target": "ws://localhost:8081/game/",
    "track_token": "<token defined by the target>"
  }
  ```

## `delivery` (game)

 The `delivery` protocol is the game-host's side of the transfer procedure. Since the game-host needs
 the gateway-host to notify the game-host first, the game-host will wait until it is notified of the session.

### `s-c delivery:ready`

 This message effectively updates the session token on the client side to the game's token.

 **Payload**: none

### `c-s delivery:identify`

 Identifies the client's gateway session to the game-host.
 
 **Payload**: 
 
  ```json
  {
    "track_token": "<track token from gateway>"
  }
  ```
 
### `s-c delivery:waiting`

 Notifies to the client that the game-host is waiting for approval from the gateway-host.
 Should be sent immediately after receiving the `delivery:identify` message.

 **Payload**: *none*
 
### `s-c delivery:upgrade`

 Notifies to the client that the game-host confirmed the client's identify, and will
 send more information soon.

 **Payload**: *none*

## `world` (game)

### `s-c world:init`

 Informs the client about the game/world's initial setup.
 
 ```json
  {
    "terrain": {
      "pieces": 25,
      "piece_size": 10
    }
  }
 ```

### `s-c world:entities`

  Adds and/or deletes a bulk of entities.
  
  ```json
  {
    "entities": [
      {
        "id": "<uuid>",
        "type": "player/prop/...",
        "data": { },
        "action": "add/del"
      }
    ]
  }
  ```

### `s-c world:terrain`

 Terrain is split in equal pieces, defined in the `world:init` message.

  ```json
  {
    "piece": {"x": 0, "y": 0},
    "terrain": ["X", "X", "X..."],
    "features": ["", "", "..."]
  }
 ```

### `s-c world:entity_data`

 Updates the data of a single entity. The `append` property defines whether the entity's current data
 should be replaced (false) or appended (true).

  ```json
  {
    "id": "<uuid>",
    "data": { },
    "append": true
  }
  ```

### `s-c world:ready`

 Notifies the client that the world is ready to be used/played.
 
 **Payload**: *none*
