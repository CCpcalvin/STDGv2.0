scoreboard objectives add s2p2b_trigger trigger
scoreboard objectives add Helper dummy
scoreboard players set detect Helper 1
scoreboard players enable @a s2p2b_trigger
schedule function s2p2b:5 1s
tellraw @a {"text": "請選擇：", "color": "green"}
