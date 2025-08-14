
from rich import print as rprint

from termprint import print as tp


def main():
    tp.title('Basic colors')
    tp.rprint(f'[{"red"}]This is red')
    tp.rprint(f'[{"green"}]This is green')
    tp.rprint(f'[{"blue"}]This is blue')
    tp.rprint(f'[{"yellow"}]This is yellow')
    tp.rprint(f'[{"magenta"}]This is magenta')
    tp.rprint(f'[{"cyan"}]This is cyan')
    tp.rprint(f'[{"white"}]This is white')
    tp.rprint(f'[{"black"}]This is black')
    tp.rprint(f'[{"purple"}]This is purple')

    tp.title('256 color')

    for i in range(0, 13): 
        rprint(f'[color({(i*20)+0})]{(i*20)+0:3} [color({(i*20)+1})]{(i*20)+1:3} [color({(i*20)+2})]{(i*20)+2:3} [color({(i*20)+3})]{(i*20)+3:3} [color({(i*20)+4})]{(i*20)+4:3} '\
               f'[color({(i*20)+5})]{(i*20)+5:3} [color({(i*20)+6})]{(i*20)+6:3} [color({(i*20)+7})]{(i*20)+7:3} [color({(i*20)+8})]{(i*20)+8:3} [color({(i*20)+9})]{(i*20)+9:3} '\
               f'[color({(i*20)+10})]{(i*20)+10:3} [color({(i*20)+11})]{(i*20)+11:3} [color({(i*20)+12})]{(i*20)+12:3} [color({(i*20)+13})]{(i*20)+13:3} [color({(i*20)+14})]{(i*20)+14:3} '\
               f'[color({(i*20)+15})]{(i*20)+15:3} [color({(i*20)+16})]{(i*20)+16:3} [color({(i*20)+17})]{(i*20)+17:3} [color({(i*20)+18})]{(i*20)+18:3} [color({(i*20)+19})]{(i*20)+19:3} ')
    
    tp.set_color_scheme('basic')
    tp.title(f'basic Scheme: {tp.actual_scheme}')
    for k,v in tp.cc.items():
        if k == 'treelevel':
            rprint(" ".join([f"[{t}]level {i}" for i,t in enumerate(v)]))
        else:
            rprint(f'[{v}]{k}')

    tp.set_color_scheme('truecolor')
    tp.title(f'truecolor Scheme: {tp.actual_scheme}')
    for k,v in tp.cc.items():
        if k == 'treelevel':
            rprint(" ".join([f"[{t}]level {i}" for i,t in enumerate(v)]))
        else:
            rprint(f'[{v}]{k}')
    
    tp.set_color_scheme('256colors')
    tp.title(f'256color Scheme: {tp.actual_scheme}')
    for k,v in tp.cc.items():
        if k == 'treelevel':
            rprint(" ".join([f"[{t}]level {i}" for i,t in enumerate(v)]))
        else:
            rprint(f'[{v}]{k}')

    tp.title('Text exmaples')
    tp.error('This is an error message')
    tp.warning('This is a warning message') 
    tp.info('This is an info message', 'This is the message')

    tp.bullet_list(['item1', 'item2', 'item3'],title='Bullet list')    

    names = [['John', 'Doe',45], ['Jane', 'Doe',56], ['Alice', 'Smith',67]]
    header = ['First Name', 'Last Name', 'Age']
    tp.table(lists= names, columns=header, title='Table example')

    names_dict = {'First Name':'John', 'Last Name':'Doe', 'Age':45}
    tp.dictionary(data=names_dict, title='Dictionary example')

    example_dict = {
        "Contacts": {
        'A': {
            'Person 1': {
                'First Name': 'John',
                'Last Name': 'Doe',
                'Age': 45
            },
        },
        'B': {
            'Person 1': {
                'First Name': 'Jane',
                'Last Name': 'Doe',
                'Age': 56
            },
            'Person 2': {
                'First Name': 'Alice',
                'Last Name': 'Smith',
                'Age': 67
            },
            'Person 3': {
                'First Name': 'Bob',
                'Last Name': 'Brown',
                'Age': 29
            }
        },
        'C': {
            'Person 1': {
                'First Name': 'Charlie',
                'Last Name': 'Davis',
                'Age': 34
            },
            'Person 2': {
                'First Name': 'Diana',
                'Last Name': 'Evans',
                'Age': 42
                }
            }
        }
    }

    tp.tree(example_dict)

if __name__ == '__main__':
    main()