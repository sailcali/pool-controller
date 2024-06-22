POOL CONTROLLER

Flask API for networked control of a Jandy 3 way valve.
Current implementation utilizes two thermistors connected
to a raspberry pi for temperature sensing in a rooftop 
solar heating system. Temperature values control the 
valve position. 

A seperate main program is used for updating the values.

API routes:

GET / Returns the current pool status

POST /valve Manually opens or closes the solar 

POST /temp Change the max temp for the pool

POST /config Updates any of the configuration values

PUT /refresh-valve Called at a frequency to maintain valve setting
