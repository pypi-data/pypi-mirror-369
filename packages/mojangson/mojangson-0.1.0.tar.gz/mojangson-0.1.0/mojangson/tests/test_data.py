parse_test_1_text = r'''{id:"minecraft:diamond_pickaxe",tag:{display:{Name:'{"text":"Кирка хлебушка"}',Lore:['{"text":"MLG PICKAXE DORITOS 420NOSCOPEBLAZEIT"}','{"text":"OH BABY A TRIPLE MOM GET THE CAMERA"}']},Enchantments:[{id:"minecraft:efficiency",lvl:20s},{id:"minecraft:fire_aspect",lvl:2s},{id:"minecraft:fortune",lvl:10s},{id:"minecraft:knockback",lvl:16959s},{id:"minecraft:looting",lvl:10s},{id:"minecraft:sharpness",lvl:16959s},{id:"minecraft:silk_touch",lvl:1s},{id:"minecraft:smite",lvl:16959s}],Unbreakable:1b,Damage:0,AttributeModifiers:[{Name:"generic.maxHealth",AttributeName:"generic.maxHealth",Operation:0,UUIDMost:0L,UUIDLeast:0L,Amount:20.0d},{Name:"generic.movementSpeed",AttributeName:"generic.movementSpeed",Operation:0,UUIDMost:0L,UUIDLeast:0L,Amount:2.0d},{Name:"generic.knockbackResistance",AttributeName:"generic.knockbackResistance",Operation:0,UUIDMost:0L,UUIDLeast:0L,Amount:0.2d},{Name:"generic.attackDamage",AttributeName:"generic.attackDamage",Operation:0,UUIDMost:0L,UUIDLeast:0L,Amount:0.0d}]},Count:1b}'''
parse_test_1_json = {'type': 'compound', 'value': {'id': {'value': 'minecraft:diamond_pickaxe', 'type': 'string'}, 'tag': {'type': 'compound', 'value': {'display': {'type': 'compound', 'value': {'Name': {'type': 'compound', 'value': {'text': {'value': 'Кирка хлебушка', 'type': 'string'}}}, 'Lore': {'type': 'list', 'value': {'type': 'compound', 'value': [{'text': {'value': 'MLG PICKAXE DORITOS 420NOSCOPEBLAZEIT', 'type': 'string'}}, {'text': {'value': 'OH BABY A TRIPLE MOM GET THE CAMERA', 'type': 'string'}}]}}}}, 'Enchantments': {'type': 'list', 'value': {'type': 'compound', 'value': [{'id': {'value': 'minecraft:efficiency', 'type': 'string'}, 'lvl': {'value': 20, 'type': 'short'}}, {'id': {'value': 'minecraft:fire_aspect', 'type': 'string'}, 'lvl': {'value': 2, 'type': 'short'}}, {'id': {'value': 'minecraft:fortune', 'type': 'string'}, 'lvl': {'value': 10, 'type': 'short'}}, {'id': {'value': 'minecraft:knockback', 'type': 'string'}, 'lvl': {'value': 16959, 'type': 'short'}}, {'id': {'value': 'minecraft:looting', 'type': 'string'}, 'lvl': {'value': 10, 'type': 'short'}}, {'id': {'value': 'minecraft:sharpness', 'type': 'string'}, 'lvl': {'value': 16959, 'type': 'short'}}, {'id': {'value': 'minecraft:silk_touch', 'type': 'string'}, 'lvl': {'value': 1, 'type': 'short'}}, {'id': {'value': 'minecraft:smite', 'type': 'string'}, 'lvl': {'value': 16959, 'type': 'short'}}]}}, 'Unbreakable': {'value': 1, 'type': 'byte'}, 'Damage': {'value': 0, 'type': 'int'}, 'AttributeModifiers': {'type': 'list', 'value': {'type': 'compound', 'value': [{'Name': {'value': 'generic.maxHealth', 'type': 'string'}, 'AttributeName': {'value': 'generic.maxHealth', 'type': 'string'}, 'Operation': {'value': 0, 'type': 'int'}, 'UUIDMost': {'value': 0, 'type': 'long'}, 'UUIDLeast': {'value': 0, 'type': 'long'}, 'Amount': {'value': 20, 'type': 'double'}}, {'Name': {'value': 'generic.movementSpeed', 'type': 'string'}, 'AttributeName': {'value': 'generic.movementSpeed', 'type': 'string'}, 'Operation': {'value': 0, 'type': 'int'}, 'UUIDMost': {'value': 0, 'type': 'long'}, 'UUIDLeast': {'value': 0, 'type': 'long'}, 'Amount': {'value': 2, 'type': 'double'}}, {'Name': {'value': 'generic.knockbackResistance', 'type': 'string'}, 'AttributeName': {'value': 'generic.knockbackResistance', 'type': 'string'}, 'Operation': {'value': 0, 'type': 'int'}, 'UUIDMost': {'value': 0, 'type': 'long'}, 'UUIDLeast': {'value': 0, 'type': 'long'}, 'Amount': {'value': 0.2, 'type': 'double'}}, {'Name': {'value': 'generic.attackDamage', 'type': 'string'}, 'AttributeName': {'value': 'generic.attackDamage', 'type': 'string'}, 'Operation': {'value': 0, 'type': 'int'}, 'UUIDMost': {'value': 0, 'type': 'long'}, 'UUIDLeast': {'value': 0, 'type': 'long'}, 'Amount': {'value': 0, 'type': 'double'}}]}}}}, 'Count': {'value': 1, 'type': 'byte'}}}

parse_test_2_text = r'''{"extra":[{"text":"§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f"},{"hoverEvent":{"action":"show_text","value":[{"extra":[{"color":"green","text":"Click to message "},{"bold":true,"color":"green","text":"*Emmers2075"}],"text":""}]},"text":"§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§l§f§f§f§lIRON "},{"clickEvent":{"action":"suggest_command","value":"/msg *Emmers2075 "},"hoverEvent":{"action":"show_text","value":[{"extra":[{"color":"green","text":"Click to message "},{"bold":true,"color":"green","text":"*Emmers2075"}],"text":""}]},"text":"§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§e§e§e§e*Emmers2075§e§e§7§7§7§7: §7§7§7§7§7§7§7§7§7§f§f§f§f"},{"text":"§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f"},{"hoverEvent":{"action":"show_item","value":[{"text":"{id:\"minecraft:netherite_sword\",tag:{RepairCost:7,\"ae_enchantment;headless\":1,Enchantments:[{id:\"minecraft:fire_aspect\",lvl:2s},{id:\"minecraft:mending\",lvl:1s},{id:\"minecraft:sharpness\",lvl:4s}],souls:48,Damage:6,\"ae_enchantment;obliterate\":2,mobtrak:\"7590\",\"ae_enchantment;insomnia\":4,\"ae_enchantment;featherweight\":2,\"ae_enchantment;trap\":2,slots:5,display:{Name:\u0027{\"text\":\"Nightmare\"}\u0027,Lore:[\u0027{\"extra\":[{\"bold\":false,\"italic\":false,\"underlined\":false,\"strikethrough\":false,\"obfuscated\":false,\"color\":\"gray\",\"text\":\"Insomnia IV\"}],\"text\":\"\"}\u0027,\u0027{\"extra\":[{\"bold\":false,\"italic\":false,\"underlined\":false,\"strikethrough\":false,\"obfuscated\":false,\"color\":\"gray\",\"text\":\"Obliterate II\"}],\"text\":\"\"}\u0027,\u0027{\"extra\":[{\"bold\":false,\"italic\":false,\"underlined\":false,\"strikethrough\":false,\"obfuscated\":false,\"color\":\"gray\",\"text\":\"Headless I\"}],\"text\":\"\"}\u0027,\u0027{\"extra\":[{\"bold\":false,\"italic\":false,\"underlined\":false,\"strikethrough\":false,\"obfuscated\":false,\"color\":\"green\",\"text\":\"Featherweight II\"}],\"text\":\"\"}\u0027,\u0027{\"extra\":[{\"bold\":false,\"italic\":false,\"underlined\":false,\"strikethrough\":false,\"obfuscated\":false,\"color\":\"aqua\",\"text\":\"Trap II\"}],\"text\":\"\"}\u0027,\u0027{\"extra\":[{\"bold\":false,\"italic\":false,\"underlined\":false,\"strikethrough\":false,\"obfuscated\":false,\"color\":\"dark_aqua\",\"text\":\"MobTrak Kills: \"},{\"italic\":false,\"color\":\"white\",\"text\":\"7590\"}],\"text\":\"\"}\u0027]}},Count:1b}"}]},"text":"§f§f§f§f§f§f§f[§f§f§f§b§b§b§b§b§b§b§b§b§f§f§f§f§b§b§f§f§f§b§b§b§bNightmare§b§b§f§f§f§f §f§f§bx1§f]"},{"text":"§f§f§f§f§f§f§f §f§f§f§f§f§f§f§f§fmy §f§f§f§f§f§f§f§f§fsword"}],"text":""}'''
parse_test_2_json = {'type': 'compound', 'value': {'extra': {'type': 'list', 'value': {'type': 'compound', 'value': [{'text': {'value': '§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f', 'type': 'string'}}, {'hoverEvent': {'type': 'compound', 'value': {'action': {'value': 'show_text', 'type': 'string'}, 'value': {'type': 'list', 'value': {'type': 'compound', 'value': [{'extra': {'type': 'list', 'value': {'type': 'compound', 'value': [{'color': {'value': 'green', 'type': 'string'}, 'text': {'value': 'Click to message ', 'type': 'string'}}, {'bold': {'type': 'boolean', 'value': True}, 'color': {'value': 'green', 'type': 'string'}, 'text': {'value': '*Emmers2075', 'type': 'string'}}]}}, 'text': {'value': '', 'type': 'string'}}]}}}}, 'text': {'value': '§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§l§f§f§f§lIRON ', 'type': 'string'}}, {'clickEvent': {'type': 'compound', 'value': {'action': {'value': 'suggest_command', 'type': 'string'}, 'value': {'value': '/msg *Emmers2075 ', 'type': 'string'}}}, 'hoverEvent': {'type': 'compound', 'value': {'action': {'value': 'show_text', 'type': 'string'}, 'value': {'type': 'list', 'value': {'type': 'compound', 'value': [{'extra': {'type': 'list', 'value': {'type': 'compound', 'value': [{'color': {'value': 'green', 'type': 'string'}, 'text': {'value': 'Click to message ', 'type': 'string'}}, {'bold': {'type': 'boolean', 'value': True}, 'color': {'value': 'green', 'type': 'string'}, 'text': {'value': '*Emmers2075', 'type': 'string'}}]}}, 'text': {'value': '', 'type': 'string'}}]}}}}, 'text': {'value': '§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§e§e§e§e*Emmers2075§e§e§7§7§7§7: §7§7§7§7§7§7§7§7§7§f§f§f§f', 'type': 'string'}}, {'text': {'value': '§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f§f', 'type': 'string'}}, {'hoverEvent': {'type': 'compound', 'value': {'action': {'value': 'show_item', 'type': 'string'}, 'value': {'type': 'list', 'value': {'type': 'compound', 'value': [{'text': {'value': '{id:"minecraft:netherite_sword",tag:{RepairCost:7,"ae_enchantment;headless":1,Enchantments:[{id:"minecraft:fire_aspect",lvl:2s},{id:"minecraft:mending",lvl:1s},{id:"minecraft:sharpness",lvl:4s}],souls:48,Damage:6,"ae_enchantment;obliterate":2,mobtrak:"7590","ae_enchantment;insomnia":4,"ae_enchantment;featherweight":2,"ae_enchantment;trap":2,slots:5,display:{Name:\'{"text":"Nightmare"}\',Lore:[\'{"extra":[{"bold":false,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"color":"gray","text":"Insomnia IV"}],"text":""}\',\'{"extra":[{"bold":false,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"color":"gray","text":"Obliterate II"}],"text":""}\',\'{"extra":[{"bold":false,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"color":"gray","text":"Headless I"}],"text":""}\',\'{"extra":[{"bold":false,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"color":"green","text":"Featherweight II"}],"text":""}\',\'{"extra":[{"bold":false,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"color":"aqua","text":"Trap II"}],"text":""}\',\'{"extra":[{"bold":false,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"color":"dark_aqua","text":"MobTrak Kills: "},{"italic":false,"color":"white","text":"7590"}],"text":""}\']}},Count:1b}', 'type': 'string'}}]}}}}, 'text': {'value': '§f§f§f§f§f§f§f[§f§f§f§b§b§b§b§b§b§b§b§b§f§f§f§f§b§b§f§f§f§b§b§b§bNightmare§b§b§f§f§f§f §f§f§bx1§f]', 'type': 'string'}}, {'text': {'value': '§f§f§f§f§f§f§f §f§f§f§f§f§f§f§f§fmy §f§f§f§f§f§f§f§f§fsword', 'type': 'string'}}]}}, 'text': {'value': '', 'type': 'string'}}}

simplify_test_data = [
    ('{}', {}),
    ('{key:value}', {'key': 'value'}),
    ('{key:"value"}', {'key': 'value'}),
    ('{key:"va,lue"}', {'key': 'va,lue'}),
    ('{k1:v1,k2:v2}', {'k1': 'v1', 'k2': 'v2'}),
    ('{number:0s}', {'number': 0}),
    ('{number:35.765d}', {'number': 35.765}),
    ('{number:35i}', {'number': 35}),
    ('{number:123b}', {'number': 123}),
    ('{nest:{}}', {'nest': {}}),
    ('{nest:{nest:{}}}', {'nest': {'nest': {}}}),
    ('{id:35,Damage:5,Count:2,tag:{display:{Name:Testing}}}', {
        'id': 35,
        'Damage': 5,
        'Count': 2,
        'tag': {'display': {'Name': 'Testing'}}
    }),
    ('{id:"minecraft:dirt",Damage:0s,Count:1b}', {'id': 'minecraft:dirt', 'Damage': 0, 'Count': 1}),
    ('{key:value,}', {'key': 'value'}),
    ('[0:v1,1:"v2",]', ['v1', 'v2']),
    ('[0:v1,2:v2]', ['v1', None, 'v2']),
    ('[0:"§6Last Killed: None",1:"§6Last Killer: None",2:"§6Rank: §aNovice-III",3:"§6§6Elo Rating: 1000",]', 
     ['§6Last Killed: None', '§6Last Killer: None', '§6Rank: §aNovice-III', '§6§6Elo Rating: 1000']),
    ('{id:1s,Damage:0s,Count:1b,tag:{display:{Name:"§r§6Class: Civilian",Lore:[0:"§6Last Killed: None",1:"§6Last Killer: None",2:"§6Rank: §aNovice-III",3:"§6§6Elo Rating: 1000",],},},}', 
     {
        'id': 1,
        'Damage': 0,
        'Count': 1,
        'tag': {
            'display': {
                'Name': '§r§6Class: Civilian',
                'Lore': ['§6Last Killed: None', '§6Last Killer: None', '§6Rank: §aNovice-III', '§6§6Elo Rating: 1000']
            }
        }
     }),
    ('[1,2,3]', [1, 2, 3]),
    ('[1,2,3,]', [1, 2, 3]),
    ('[]', []),
    ('["a","b;"]', ['a', 'b;']),
    ('{id:"minecraft:yello[w_shulker_box",Count:1b,tag:{BlockEntityTag:{CustomName:"Stacked Totems",x:0,y:0,z:0,id:"minecraft:shulker_box",Lock:""},display:{Name:"Stacked Totems"}},Damage:0s}', 
     {
         'id': 'minecraft:yello[w_shulker_box',
         'Count': 1,
         'tag': {
             'BlockEntityTag': {'CustomName': 'Stacked Totems', 'x': 0, 'y': 0, 'z': 0, 'id': 'minecraft:shulker_box', 'Lock': ''},
             'display': {'Name': 'Stacked Totems'}
         },
         'Damage': 0
     }),
    ('[B;1b,2b,3b,]', {'type': 'byte', 'value': [1, 2, 3]}),
    ('[I;1,2,3]', {'type': 'int', 'value': [1, 2, 3]}),
    ('[L;1l,2l,3l]', {'type': 'long', 'value': [1, 2, 3]}),
    ('{id:"§a"}', {'id': '§a'}),
    ('{id:"a="}', {'id': 'a='})
]


stringify_test_data = [
    ('{}', '{}'),
    ('{key:value}', '{key:value}'),
    ('{key:"value"}', '{key:value}'),
    ('{key:"va,lue"}', '{key:"va,lue"}'),
    ('{k1:v1,k2:v2}', '{k1:v1,k2:v2}'),
    ('{number:0s}', '{number:0s}'),
    ('{number:35.765d}', '{number:35.765}'),
    ('{number:35i}', '{number:35}'),
    ('{number:123b}', '{number:123b}'),
    ('{nest:{}}', '{nest:{}}'),
    ('{nest:{nest:{}}}', '{nest:{nest:{}}}'),
    ('{id:35,Damage:5,Count:2,tag:{display:{Name:Testing}}}', '{id:35,Damage:5,Count:2,tag:{display:{Name:Testing}}}'),
    ('{id:"minecraft:dirt",Damage:0s,Count:1b}', '{id:"minecraft:dirt",Damage:0s,Count:1b}'),
    ('{key:value,}', '{key:value}'),
    ('[0:v1,1:"v2",]', '[v1,v2]'),
    ('[0:v1,2:v2]', '[0:v1,2:v2]'),
    ('[0:"§6Last Killed: None",1:"§6Last Killer: None",2:"§6Rank: §aNovice-III",3:"§6§6Elo Rating: 1000",]', '["§6Last Killed: None","§6Last Killer: None","§6Rank: §aNovice-III","§6§6Elo Rating: 1000"]'),
    ('{id:1s,Damage:0s,Count:1b,tag:{display:{Name:"§r§6Class: Civilian",Lore:[0:"§6Last Killed: None",1:"§6Last Killer: None",2:"§6Rank: §aNovice-III",3:"§6§6Elo Rating: 1000",],},},}', '{id:1s,Damage:0s,Count:1b,tag:{display:{Name:"§r§6Class: Civilian",Lore:["§6Last Killed: None","§6Last Killer: None","§6Rank: §aNovice-III","§6§6Elo Rating: 1000"]}}}'),
    ('[1,2,3]', '[1,2,3]'),
    ('[1,2,3,]', '[1,2,3]'),
    ('[]', '[]'),
    ('["a","b;"]', '[a,"b;"]'),
    ('{id:"minecraft:yello[w_shulker_box",Count:1b,tag:{BlockEntityTag:{CustomName:"Stacked Totems",x:0,y:0,z:0,id:"minecraft:shulker_box",Lock:""},display:{Name:"Stacked Totems"}},Damage:0s}', '{id:"minecraft:yello[w_shulker_box",Count:1b,tag:{BlockEntityTag:{CustomName:Stacked Totems,x:0,y:0,z:0,id:"minecraft:shulker_box",Lock:""},display:{Name:Stacked Totems}},Damage:0s}'),
    ('[B;1b,2b,3b,]', '[B;1b,2b,3b]'),
    ('[I;1,2,3]', '[I;1,2,3]'),
    ('[L;1l,2l,3l]', '[L;1l,2l,3l]'),
    ('{id:"§a"}', '{id:"§a"}'),
    ('{id:"a="}', '{id:"a="}')
]
