from sys import exit

from rich import print

import requests

MENU_TEXT = """Select a number:
(1) Definition
(2) Synonyms
(3) Anytonyms
"""


def get_definition(word, response_content):
    definition = response_content["meanings"][0]["definitions"][0]["definition"]
    part_of_speech = response_content["meanings"][0]["partOfSpeech"]

    print(f"[b]{word.title()}[/b] [u]{part_of_speech.lower()}[/u]: {definition}")


def get_synonyms(response_content):
    all_synonyms = []

    # Loop through all meanings
    for meaning in response_content["meanings"]:
        all_synonyms.extend(meaning.get("synonyms", []))

        for definition in meaning["definitions"]:
            all_synonyms.extend(definition.get("synonyms", []))

    # Remove duplicates
    all_synonyms = list(set(all_synonyms))

    if all_synonyms:
        for synonym in all_synonyms:
            print("*", synonym)
    else:
        print("[b]No synonyms found.[/b]")


def get_antonyms(response_content):
    all_antonyms = []

    for meaning in response_content["meanings"]:
        all_antonyms.extend(meaning.get("antonyms", []))

        for definition in meaning["definitions"]:
            all_antonyms.extend(definition.get("antonyms", []))

    all_antonyms = list(set(all_antonyms))

    if all_antonyms:
        for antonym in all_antonyms:
            print("*", antonym)
    else:
        print("[b]No anytonyms found.[/b]")


def main():
    print(MENU_TEXT)
    choice = input(">> ")
    if choice not in [
        "1",
        "2",
        "3",
    ]:
        print("[bold red]Invalid choice[/bold red]")
        exit(1)

    word = input("Word: ")
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    response = requests.get(url)

    if response.status_code == 200:
        response_content = response.json()[0]

        if choice == "1":
            get_definition(word, response_content)
        elif choice == "2":
            get_synonyms(response_content)
        elif choice == "3":
            get_antonyms(response_content)

    else:
        print(f"ERROR: {response.status_code}")
        exit(1)


if __name__ == "__main__":
    main()
