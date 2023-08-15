scoreboard objectives add s1p1_trigger trigger
scoreboard objectives add Helper dummy
scoreboard players set detect Helper 1
scoreboard players enable @a s1p1_trigger
schedule function s1p1:8 1s
tellraw @a {"text": "請選擇：", "color": "green"}
