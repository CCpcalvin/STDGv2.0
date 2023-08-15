execute as @r[scores={s2p2b_trigger=1}] run function s2p2a:0 
execute as @r[scores={s2p2b_trigger=2}] run function s2p2b:0 
execute as @r[scores={s2p2b_trigger=3}] run function s2p2c:0 
execute as @r[scores={s2p2b_trigger=4}] run function s2p2d:0 
execute if score detect Helper matches 1 run schedule function s2p2b:9 2t
