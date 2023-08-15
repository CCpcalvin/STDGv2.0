execute unless score option4 s1p1_obj matches 1 run tellraw @a {"text": "[Investigate the meteor crater alone]", "clickEvent": {"action": "run_command", "value": "/trigger s1p1_trigger set 4"}, "color": "green"}
execute if score option4 s1p1_obj matches 1 run tellraw @a {"text": "[Investigate the meteor crater alone]", "color": "gray"}
schedule function s1p1:12 1s
execute as @a at @s run playsound minecraft:block.anvil.step player @s ~ ~ ~
