execute unless score option1 s1p1_obj matches 1 run tellraw @a {"text": "[Ask Even_Gor]", "clickEvent": {"action": "run_command", "value": "/trigger s2p2b_trigger set 1"}, "color": "green"}
execute if score option1 s1p1_obj matches 1 run tellraw @a {"text": "[Ask Even_Gor]", "color": "gray"}
schedule function s2p2b:6 1s
execute as @a at @s run playsound minecraft:block.anvil.step player @s ~ ~ ~
