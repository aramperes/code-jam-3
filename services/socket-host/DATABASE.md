# Database Documentation

Prefix/namespace: `deathwatch:`

## Usage


* When a user is not authenticated, and tries to create a new username `foo`
  * Generate a discriminator, `discrim`
  * Check if `deathwatch:user_name:foo#discrim` exists.
    * If it exists, generate a new discriminator and try again.
    * If it doesn't exist, create a new token, and set:
      * `deathwatch:token:<token> = "foo#discrim"`
      * `deathwatch:user_name:foo#discrim = "token"`

* When a user is authenticated (token provided):
  * Check if `deathwatch:token:<token>` has a value
    * If there is no value, deny
    * If there is a value, return the value (which should be `<name>#<discrim>`)
