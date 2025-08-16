def loop(num, commands):
    for _ in range(num):
        for command in commands:
            exec(command)

def join(items, debug_mode=False):
    return_value = ''
    
    for item in items:
        return_value += str(item)
        if debug_mode:
            print(f'i val:  {item}')
            print(f'r val:  {return_value}')
        else:
            pass
    return return_value


# usage :
# from KMK_tools import loop
# from KMK_tools import join
# 
#  
# loop(num=8, commands=[
#     'print(\'hello\')',
#     'input(\'what is your name : \')'
#     ])
#
# 
# print(
#     join(
#         items=
#             [
#             'kmk ',
#             'hello ',
#             'world'
#             ],
#             debug_mode=True)
#     )