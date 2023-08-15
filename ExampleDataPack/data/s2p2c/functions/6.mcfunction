execute unless score option2 s1p1_obj matches 1 run tellraw @a {"text": "[Ask Ben]", "clickEvent": {"action": "run_command", "value": "/trigger s2p2c_trigger set 2"}, "color": "green"}
execute if score option2 s1p1_obj matches 1 run tellraw @a {"text": "[Ask Ben]", "color": "gray"}
schedule function s2p2c:7 1s
execute as @a at @s run playsound minecraft:block.anvil.step player @s ~ ~ ~
