execute unless score option3 s1p1_obj matches 1 run tellraw @a {"text": "[Ask Ryan]", "clickEvent": {"action": "run_command", "value": "/trigger s1p1_trigger set 3"}, "color": "green"}
execute if score option3 s1p1_obj matches 1 run tellraw @a {"text": "[Ask Ryan]", "color": "gray"}
schedule function s1p1:11 1s
execute as @a at @s run playsound minecraft:block.anvil.step player @s ~ ~ ~
