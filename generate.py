#!/usr/bin/python
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import csv, os, re, sys
import codecs

CARD_TEMPLATE_LATEX = u"""
    \\cardfrontfoot{%s}

    \\begin{flashcard}[%s]{%s}

        \Large{%s}

    \\end{flashcard}
"""

VOCAB_FILE = "vocab.csv"
LATEX_TEMPLATE_FILE = "template.tex"

def generate_latex_card(card):
    card = dict(card)
    b = re.compile(ur"\$(.{1})", flags=re.UNICODE)
    u = re.compile(ur"\_(.{1})")
    for k in card.keys():
        card[k] = b.sub(r'{\\bf \1}', card[k])
        card[k] = u.sub(r'\\underline{\1}', card[k])

    return CARD_TEMPLATE_LATEX % (
                                    card["SetNameEng"] + "/" + card["SetNameMac"],
                                    card["TypeNameEng"] + "/" + card["TypeNameMac"],
                                    card["WordEng"], card["WordMac"]
                                 )

def wrap_latex_cards(cards, file_name):
    lines = open(LATEX_TEMPLATE_FILE, "rb").readlines()
    data = "\n".join(lines).replace(u"%__CARDS__%", cards)
    codecs.getwriter('utf-8')(file(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'output', 'latex', file_name + '.tex'), 'w')).write(data)

def generate_anki_card(card):
    card = dict(card)
    b = re.compile(ur"\$(.{1})", flags=re.UNICODE)
    u = re.compile(ur"\_(.{1})")

    for k in card.keys():
        card[k] = b.sub(r'<span style="font-weight:600;">\1</span>', card[k])
        card[k] = u.sub(r'<span style="text-decoration: underline;">\1</span>', card[k])

    return [[card["WordEng"] + "<br>" + "[" + card["SetNameEng"] + " - " + card["TypeNameEng"] + "]",
            card["WordMac"] + "<br>" + "[" + card["SetNameMac"] + " - " + card["TypeNameMac"] + "]"]]


def wrap_anki_cards(cards, file_name):
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'output', 'anki', file_name + '.csv'), 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)   
        
        cards = [["[Copyright & License Notice]{LaTeX template is copyrighted by its author and licensed under GPL. Rendered documents and code used to generate them is copyrighted and is distributed under GNU General Public License. If you have any questions, please contact the author at nikita [at] pchelin.ca]", "Copyright & License Notice"]] + cards

        for card in cards:
            writer.writerow([v.encode('utf8') for v in card])

def main():
    # Read dictionary of words and generate files.
    vocab_dict = {}
    latex_cards = ""
    anki_cards = []
    set_name = None
    filename = 0

    with open(VOCAB_FILE, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in reader:
            a_card = {
                "SetNameEng"  : unicode(row[0], 'utf-8'),
                "SetNameMac"  : unicode(row[1], 'utf-8'),
                "TypeNameEng" : unicode(row[2], 'utf-8'),
                "TypeNameMac" : unicode(row[3], 'utf-8'),
                "WordMac" : unicode(row[4], 'utf-8'),
                "WordEng" : unicode(row[5], 'utf-8')
            }

            # Save cards for each of the sets.
            if set_name is not None and set_name != a_card["SetNameEng"]:
                wrap_latex_cards(latex_cards, set_name)
                latex_cards = generate_latex_card(a_card)
                wrap_anki_cards(anki_cards, set_name)
                anki_cards = generate_anki_card(a_card)
            else:
                latex_cards += generate_latex_card(a_card)
                anki_cards += generate_anki_card(a_card)

            set_name = a_card["SetNameEng"]
    
    # Last set.
    wrap_latex_cards(latex_cards, set_name)
    wrap_anki_cards(anki_cards, set_name)

    # Attempt to generate PDFs from Latex.
    pdf_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'output', 'pdf')

    for f in os.listdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'output', 'latex')):
        if f.endswith(".tex"):
            file_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'output', 'latex', f)

            cmd = "latex --output-format=pdf --output-directory=\"" + pdf_dir + "\" \"" + file_dir + "\""
            #os.system(cmd)

if __name__ == "__main__":
    main()
