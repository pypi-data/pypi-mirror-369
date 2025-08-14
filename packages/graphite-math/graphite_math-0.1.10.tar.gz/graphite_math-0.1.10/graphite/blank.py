import pyperclip, json
with open('val.json', 'r', encoding='utf-8') as f:
    raw_data = json.load(f)
latex_list = [pair['latex'] for pair in raw_data['pairs'] if pair.get('latex') is not None]
pyperclip.copy('[\n'+str(latex_list)[1:-1] + '\n]')