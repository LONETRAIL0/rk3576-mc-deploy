execute as @e[type=item] store result score @s ci_age run data get entity @s Age
kill @e[type=item,scores={ci_age=1200..}]
tellraw @a {"text":"[清道夫] 掉落物清理完成","color":"gray"}
execute store result score #lastclear ci_age run time query gametime
schedule function clear_items:warn 540s replace
