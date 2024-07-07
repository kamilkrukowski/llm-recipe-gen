import pathlib
import re
import os
import argparse

import dotenv
from openai import OpenAI

client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

dotenv.load_dotenv()


def make(prompt: str) -> str:

    response = client.chat.completions.create(model='gpt-3.5-turbo',
    n=1,
    messages=[
        {"role": "system", "content": "You are a professional cookbook editor and writer."},
        {"role": "user", "content": prompt},
    ],
    max_tokens=1024)

    message = response.choices[0].message
    return message['content']

def find_all_tex_files(dir: str):
    return [str(i) for i in list(pathlib.Path(dir).rglob('*.tex'))]

def read_recipe(path: str):
    return open(path, 'r').read()

def generate_main(raw_ai_doc_names: str):
    doc = R"""\documentclass[%
    a4paper,
    %twoside,
    11pt
    ]{article}

    \usepackage[]{inputenc}
    \usepackage{lmodern}
    \usepackage{placeins}
    \usepackage[english]{babel}


    \usepackage{nicefrac}

    \usepackage[
        nowarnings,
    ]
    {xcookybooky}
    
    \usepackage{blindtext}    % only needed for generating test text

    \DeclareRobustCommand{\textcelcius}{\ensuremath{^{\circ}\mathrm{C}}}


    \setcounter{secnumdepth}{1}
    \renewcommand*{\recipesection}[2][]
    {%
        \subsection[#1]{#2}
    }
    \renewcommand{\subsectionmark}[1]
    {% no implementation to display the section name instead
    }


    \usepackage{hyperref}    % must be the last package
    \hypersetup{%
        pdfauthor            = {Kamil Krukowski},
        pdftitle             = {Krukowski Files},
        pdfsubject           = {Recipes},
        pdfkeywords          = {Polish, recipes, cookbook, xcookybooky},
        pdfstartview         = {FitV},
        pdfview              = {FitH},
        pdfpagemode          = {UseNone}, % Options; UseNone, UseOutlines
        bookmarksopen        = {true},
        pdfpagetransition    = {Glitter},
        colorlinks           = {true},
        linkcolor            = {black},
        urlcolor             = {blue},
        citecolor            = {black},
        filecolor            = {black},
    }

    \hbadness=10000	% Ignore underfull boxes

    \begin{document}

    \title{Krukowski Cookbook}
    \author{Kamil Krukowski\\ \href{mailto:kamiljkrukowski@gmail.com}{kamiljkrukowski@gmail.com}}
    \maketitle

    \begin{abstract}
        \noindent A curated selection of family favorite recipes developed by Kamil Krukowski.
    \end{abstract}

    \tableofcontents

    %REPLACE_THIS_HERE%
    
    \end{document} 
    """
    generated_recipes = raw_ai_doc_names
    lines = ["\t\include{./recipes/raw_ai/" + f"{name}.tex" + "}" for name in generated_recipes]
    replacement = "\n".join(lines)
    with open('./latex/main.tex', 'w') as f:
        f.write(doc.replace('%REPLACE_THIS_HERE%', replacement))

def render():
    os.system('cd latex/ && pdflatex --interaction=nonstopmode main.tex && cd ../')

recipes = {i.split('/')[-1]: read_recipe(i) for i in find_all_tex_files('./latex/recipes/handmade')}

_str_elems = []
for recipe_name in recipes.keys():
    _str_elems.append(f"Here is a recipe for {recipe_name}:\n")
    _str_elems.append(recipes[recipe_name])

sample_recipes = "\n".join(_str_elems[:10])

HEADER = "Here is a sample collection of recipes:\n" + sample_recipes

def generate_recipe(recipe_name: str) -> None:

    target = recipe_name.replace(' ', '')

    prompt = HEADER + f"Please make a recipe in the above collections style of a {target}."
    path = './latex/recipes/raw_ai/' + f"{target}.tex"
    if not os.path.exists(path):
        print(f"Generating {target}")
        try:
            result = make(prompt)
            clean_subset = re.search(pattern = '\\\\begin\{recipe\}[\s\S]+?\\\\end\{recipe\}', string=result).group(0)
            with open(path, "w") as f:
                f.write(clean_subset)
        except Exception as e:
            print("Failed to generate recipe for ", target)
            print(e)
            pass

parser = argparse.ArgumentParser(description='Generate a recipe')
parser.add_argument('-r', '--recipe', type=str, help='The name of the recipe to generate', default='Lemon Squares')

target_recipe = parser.parse_args().recipe
print("Recipe is: ", target_recipe)

generate_recipe(target_recipe)
target_recipe_list = [target_recipe]
generate_main([i.replace(' ', '') for i in target_recipe_list])
#render()





