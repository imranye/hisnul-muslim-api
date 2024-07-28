import csv
from bs4 import BeautifulSoup

# Assuming you have saved the HTML content in a file named 'duas.html'
with open('output.html', 'r', encoding='utf-8') as file:
    html_content = file.read()

soup = BeautifulSoup(html_content, 'html.parser')

duas = []

for dua_container in soup.find_all('div', class_='dua-container'):
    chapter_title = dua_container.find('div', class_='chapter-title')
    
    if chapter_title:
        chapter_name = chapter_title.find('div').text.strip()
        number_of_duas = chapter_title.find('div', class_='number-of-duas').text.strip()
    else:
        continue  # Skip containers without a chapter title

    arabic_text = dua_container.find('div', class_='arabic-text')
    transliteration = dua_container.find('div', class_='hisnul-transliteration')
    translation = dua_container.find('div', class_='hisnul-translation')
    reference = dua_container.find('div', class_='hisnul-reference')

    if arabic_text and transliteration and translation and reference:
        duas.append({
            'Chapter': chapter_name,
            'Number of Duas': number_of_duas,
            'Arabic': arabic_text.text.strip(),
            'Transliteration': transliteration.text.strip(),
            'Translation': translation.text.strip(),
            'Reference': reference.text.strip()
        })

# Write to CSV file
with open('duas.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['Chapter', 'Number of Duas', 'Arabic', 'Transliteration', 'Translation', 'Reference']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for dua in duas:
        writer.writerow(dua)

print("CSV file 'duas.csv' has been created successfully.")
