execute as @r[scores={s1p1_trigger=1}] run function s2p2a:0 
execute as @r[scores={s1p1_trigger=2}] run function s2p2b:0 
execute as @r[scores={s1p1_trigger=3}] run function s2p2c:0 
execute as @r[scores={s1p1_trigger=4}] run function s2p2d:0 
execute if score detect Helper matches 1 run schedule function s1p1:12 2t
