from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse, Media
import wiki

app = Flask(__name__)

user_states = {}


@app.route("/", methods=['GET', 'POST'])
def sms_reply():
    # Get the incoming message and sender's phone number
    incoming_msg = request.values.get('Body', '').lower()
    sender = request.values.get('From', '')

    # Start our TwiML response
    resp = MessagingResponse()

    # Check if the user is in the user_states dictionary
    if sender not in user_states:
        user_states[sender] = {'state': 'menu'}

    # Get the current state of the user
    current_state = user_states[sender]['state']

    if current_state == 'menu':
        if 'menu' == incoming_msg:
            # Send the menu options to the user
            resp.message(
                "\nWelcome to TextWiki. Please choose one of the following options (Type 1, 2, or 3):\n\n1. Info\n2. Search for a word\n3. Exit TextWiki")
        elif '1' == incoming_msg or '1.' == incoming_msg:
            # Respond with message for Option 1
            resp.message("TextWiki is designed to offer the features of searching for a word and navigating through the Wikipedia page containing information about that word via text message.\n In its current state 'V1.0' TextWiki allows you to search for a word and view search results in small snippets of information. You may also request for more information about a word if necessary.\n\n---\n\nTextWiki will be 'released' incrementally with upcoming versions including features such as:\n\n V1.1: More robust navigation by means of the navigation bar to view information by section\n V1.2: ChatGPT integration to offer support for topics that do not have sufficient information via the Wikipeadia page\n V1.3: Access to works cited referenced in Wikipedia page\n V1.4: Access to pictures associated with given Wikipedia page.\n\n---\n\nPlease choose one of the following options (Type 1, 2, or 3):\n\n1. Info\n2. Search for a word\n3. Exit TextWiki")
            user_states[sender]['state'] = 'menu'
        elif '2' == incoming_msg or '2.' == incoming_msg:
            # Update the user's state
            user_states[sender]['state'] = 'choose search'
            # Respond with message for Option 2
            resp.message("Please choose search method (Type 1, 2, 3, or 4):\n\n 1. General search \n(Populate topic information navigating by paragraph. Similar to scrolling down Wikipedia page.)\n\n2. Navigated search \n(Populate topic information navigating by table of contents. Similar to using Navigation bar/table of contents on Wikipedia page.)\n\n3. Search images\n\n4. Back to main menu")
        elif '3' == incoming_msg or '3.' == incoming_msg:
            # Respond with message for Option 3
            resp.message("Thanks for using TextWiki! See you again soon")
        else:
            # If the user sends any other message, send an error message
            resp.message("Sorry, we didn't understand your message. Please choose one of the options from the menu.\n\n---\n\nWelcome to TextWiki. Please choose one of the following options (Type 1, 2, or 3):\n\n1. Info\n2. Search for a word\n3. Exit TextWiki")
            user_states[sender]['state'] = 'menu'

    elif current_state == 'choose search':
        if '1' == incoming_msg or '1.' == incoming_msg:
            # Update the user's state
            user_states[sender]['state'] = 'general search'
            resp.message(
                "What topic would you like to search for?\n\n---\n\n*Type '**' to return to main menu*")
        elif '2' == incoming_msg or '2.' == incoming_msg:
            user_states[sender]['state'] = 'navigate search'
            resp.message(
                "What topic would you like to search for?\n\n---\n\n*Type '**' to return to main menu*")
        elif '3' == incoming_msg or '3.' == incoming_msg:
            user_states[sender]['state'] = 'image search'
            resp.message(
                "What images would you like to search for?\n\n*Type '**' ro return to main menu*"
            )
        elif '4' == incoming_msg or '4.' == incoming_msg:
            user_states[sender]['state'] = 'menu'
            resp.message(
                "\nWelcome to TextWiki. Please choose one of the following options (Type 1, 2, or 3):\n\n1. Info\n2. Search for a word\n3. Exit TextWiki")
        else:
            user_states[sender]['state'] = 'choose search'
            resp.message("Sorry, we didn't understand your message. Please choose one of the options from the menu.\n\n---\n\nPlease choose search method (Type 1, 2, 3, or 4):\n\n 1. General search \n(Populate topic information navigating by paragraph. Similar to scrolling down Wikipedia page.)\n\n2. Navigated search \n(Populate topic information navigating by table of contents. Similar to using Navigation bar/table of contents on Wikipedia page.)\n\n3. Search images\n\n4. Back to main menu")

    elif current_state == 'general search':
        if '**' == incoming_msg:
            user_states[sender]['state'] = 'menu'
            resp.message(
                "\nWelcome to TextWiki. Please choose one of the following options (Type 1, 2, or 3):\n\n1. Info\n2. Search for a word\n3. Exit TextWiki")
        else:
            # Concatenate the user's input
            incoming_msg = incoming_msg.replace(' ', '_')
            # Call the wiki.main function with the user's query
            paragraphs, navbar, images, links = wiki.main(incoming_msg)
            user_states[sender]['paragraphs'] = paragraphs

            # Send the first paragraph as a message
            if len(paragraphs) < 2:
                gptParagraph = wiki.gptSearch(incoming_msg)
                resp.message(
                    gptParagraph + "\n\n---\n\nPlease choose one of the following options (Type 1, 2, or 3):\n\n1. Info\n2. Search for a word\n3. Exit TextWiki")
                user_states[sender]['state'] = 'menu'
            else:
                user_states[sender]['current_paragraph'] = 1
                resp.message("Here is information about your requested topic:\n\n" +
                             paragraphs[1] + "\n\n---\n\nPlease choose one of the following options (Type 1, 2, or 3):\n\n1. Learn more about this topic\n2. Search for a different Wikipedia page\n3. Return to the main menu")
                user_states[sender]['nsearch marker'] = False
                user_states[sender]['state'] = 'reading_gsearch'

    elif current_state == 'image search':
        if '**' == incoming_msg:
            user_states[sender]['state'] = 'menu'
            resp.message(
                "\nWelcome to TextWiki. Please choose one of the following options (Type 1, 2, or 3):\n\n1. Info\n2. Search for a word\n3. Exit TextWiki")
        else:
            # Concatenate the user's input
            incoming_msg = incoming_msg.replace(' ', "_")
            paragraphs, navbar, images, links = wiki.main(incoming_msg)
            user_states[sender]['images'] = images

            if len(images) == 0:
                resp.message(
                    "There are not any Wiki images associated with the word " + incoming_msg +
                    "\n\nWhat is the word that you'd like to see images for?\n\n*Type '**' to return to main menu*"
                )
            else:
                user_states[sender]['image_num'] = 0
                user_states[sender]['state'] = 'image reading'
                image_num = user_states[sender]['image_num']
                resp.message(
                    "Here is a photo of a " + incoming_msg + "\n\n" + user_states[sender]['images'][image_num] +
                    "\n\n Please choose one of the following (Type 1, 2, or 3):\n\n1.See another image\n2.Search images for a new word\n3.Return to menu"
                )
                user_states[sender]['image_num'] = image_num + 1
                user_states[sender]['curr_word'] = incoming_msg

    elif current_state == "image reading":
        if '**' == incoming_msg or '3' == incoming_msg or '3.' == incoming_msg:
            user_states[sender]['state'] = 'menu'
            resp.message(
                "\nWelcome to TextWiki. Please choose one of the following options (Type 1, 2, or 3):\n\n1. Info\n2. Search for a word\n3. Exit TextWiki")

        elif '2' == incoming_msg or '2.' == incoming_msg:
            user_states[sender]['state'] = 'image search'
            resp.message(
                "What images would you like to search for?\n\n*Type '**' ro return to main menu*"
            )
        elif '1' == incoming_msg or '1.' == incoming_msg:
            curr_word = user_states[sender]['curr_word']
            images = user_states[sender]['images']
            image_num = user_states[sender]['image_num']
            if image_num == len(images):
                resp.message(
                    "There are no more photos for " + curr_word + " you will be sent back to menu."
                )
                user_states[sender]['state'] = 'menu'
            else:
                resp.message(
                    "Here is a photo of a " + curr_word + "\n\n" + user_states[sender]['images'][image_num] +
                    "\n\n Please choose one of the following (Type 1, 2, or 3):\n\n1.See another image\n2.Search images for a new word\n3.Return to menu"
                )
                user_states[sender]['image_num'] = image_num + 1

    elif current_state == 'navigate search':
        if '**' == incoming_msg:
            user_states[sender]['state'] = 'menu'
            resp.message(
                "\nWelcome to TextWiki. Please choose one of the following options (Type 1, 2, or 3):\n\n1. Info\n2. Search for a word\n3. Exit TextWiki")
        else:
            # Concatenate the user's input
            incoming_msg = incoming_msg.replace(' ', '_')
            # Call the wiki.main function with the user's query
            paragraphs, navbar_elems, images, links = wiki.main(incoming_msg)
            user_states[sender]['curr_word'] = incoming_msg
            # Check if word is less than 2 paragraphs
            # if len(paragraphs) < 2:
            #     gptParagraph = wiki.gptSearch(incoming_msg)
            #     resp.message (gptParagraph + "\n\n---\n\nThis is the extent of information available for this topic.\n\nMain Menu:\n\nPlease choose one of the following options (Type 1, 2, or 3):\n\n1. Info\n2. Search for a word\n3. Exit TextWiki")
            #     user_states[sender]['state'] = 'menu'
            # else:
            resp.message(
                "Which Section would you like to view (Please type the title of the section you want to view from the following list):")
            navbar_items_display = ""
            navbar_items_checker = []
            for item in navbar_elems:
                if item == 'mw-content-text' or item == 'See_also' or item == 'References' or item == 'External_links' or item == 'Further_reading' or item == 'Notes' or item == 'Bibliography':
                    continue
                else:
                    item = item.replace('_', ' ')
                    navbar_items_checker.append(item)
                    navbar_items_display += item + "\n\n========\n"
            resp.message(navbar_items_display +
                         "\n\n---\n\n*Type '**' to return to main menu*")
            user_states[sender]['navbar_checker'] = navbar_items_checker
            user_states[sender]['state'] = 'reading_nsearch'

    elif current_state == 'reading_nsearch':
        if '**' == incoming_msg:
            user_states[sender]['state'] = 'menu'
            resp.message(
                "\nWelcome to TextWiki. Please choose one of the following options (Type 1, 2, or 3):\n\n1. Info\n2. Search for a word\n3. Exit TextWiki")
        else:
            cleaned_message = incoming_msg.capitalize()
            cleaned_message = cleaned_message.strip()
            iterator = 0
            input_correct = False
            for elem in user_states[sender]['navbar_checker']:
                print(elem)
                print("=====")
                print(cleaned_message)
                if cleaned_message == user_states[sender]['navbar_checker'][iterator]:
                    input_correct = True
                    break
                else:
                    iterator += 1
                    continue
            if input_correct is False:
                resp.message(
                    "Input Invalid. Please choose your category from the given list (Please type the title of the section as listed). \n\n * Be sure to check for typos! *")
            else:
                paragraphs, navbar_elems, images, links = wiki.main(
                    user_states[sender]['curr_word'], cleaned_message)
                user_states[sender]['paragraphs'] = paragraphs
                user_states[sender]['current_paragraph'] = 0
                resp.message("Here is information about your requested topic:\n\n" +
                             paragraphs[0] + "\n\n---\n\nPlease choose one of the following options (Type 1, 2, or 3):\n\n1. Learn more about this topic\n2. Search for a different Wikipedia page\n3. Return to the main menu")
                user_states[sender]['nsearch marker'] = True
                user_states[sender]['state'] = 'reading_gsearch'

    elif current_state == 'nsearch_sectionEnd':
        if '1' == incoming_msg or '1.' == incoming_msg:
            # Call the wiki.main function with the user's query
            paragraphs, navbar_elems, images, links = wiki.main(
                user_states[sender]['curr_word'])
            # Check if word is less than 2 paragraphs
            # if len(paragraphs) < 2:
            #     gptParagraph = wiki.gptSearch(incoming_msg)
            #     resp.message (gptParagraph + "\n\n---\n\nThis is the extent of information available for this topic.\n\nMain Menu:\n\nPlease choose one of the following options (Type 1, 2, or 3):\n\n1. Info\n2. Search for a word\n3. Exit TextWiki")
            #     user_states[sender]['state'] = 'menu'
            # else:
            resp.message(
                "Which Section would you like to view (Please type the title of the section you want to view from the following list):")
            navbar_items_display = ""
            navbar_items_checker = []
            for item in navbar_elems:
                if item == 'mw-content-text' or item == 'See_also' or item == 'References' or item == 'External_links' or item == 'Further_reading' or item == 'Notes' or item == 'Bibliography':
                    continue
                else:
                    item = item.replace('_', ' ')
                    navbar_items_checker.append(item)
                    navbar_items_display += item + "\n\n========\n"
            resp.message(navbar_items_display +
                         "\n\n---\n\n*Type '**' to return to main menu*")
            user_states[sender]['navbar_checker'] = navbar_items_checker
            user_states[sender]['state'] = 'reading_nsearch'

        elif '2' == incoming_msg or '2.' == incoming_msg:
            user_states[sender]['state'] = 'choose search'
            resp.message("Please choose search method (Type 1, 2, or 3):\n\n 1. General search (Populate topic information navigating by paragraph. Similar to scrolling down Wikipedia page.)\n\n2. Navigated search (Populate topic information navigating by table of contents. Similar to using Navigation bar/table of contents on Wikipedia page.)\n\n3. Back to main menu")
        elif '3' == incoming_msg or '3.' == incoming_msg:
            user_states[sender]['state'] = 'menu'
            resp.message(
                "\nWelcome to TextWiki. Please choose one of the following options (Type 1, 2, or 3):\n\n1. Info\n2. Search for a word\n3. Exit TextWiki")
        else:
            resp.message("Sorry, we didn't understand your message. Please choose one of the options from the menu (Type 1, 2, or 3):\n\n1. Keep navigating information about this topic (Choose a different section)\n2. Search for a different word\n3. Return to the main menu")

    elif current_state == 'reading_gsearch':
        if '1' == incoming_msg or '1.' == incoming_msg:
            user_states[sender]['current_paragraph'] += 1
            if user_states[sender]['current_paragraph'] < len(user_states[sender]['paragraphs']):
                resp.message("Here is information about your requested topic:\n\n" + user_states[sender]['paragraphs'][user_states[sender]['current_paragraph']] +
                             "\n\n---\n\nPlease choose one of the following options (Type 1, 2, or 3):\n\n1. Learn more about this topic\n2. Search for a different Wikipedia page\n3. Return to the main menu")
            else:
                if user_states[sender]['nsearch marker'] == False:
                    resp.message(
                        "No more information available on this topic at this time.\n\nMain Menu:\n\nPlease choose one of the following options (Type 1, 2, or 3):\n\n1. Info\n2. Search for a word\n3. Exit TextWiki")
                    user_states[sender]['state'] = 'menu'
                else:
                    resp.message("No more information available in this section.\n\n---\n\nPlease choose one of the options from the menu (Type 1, 2, or 3):\n\n1. Continue navigating information about this topic (Choose a different section)\n2. Search for a different word\n3. Return to the main menu")
                    user_states[sender]['state'] = 'nsearch_sectionEnd'

        elif '2' == incoming_msg or '2.' == incoming_msg:
            user_states[sender]['state'] = 'choose search'
            resp.message("Please choose search method (Type 1, 2, or 3):\n\n 1. General search (Populate topic information navigating by paragraph. Similar to scrolling down Wikipedia page.)\n\n2. Navigated search (Populate topic information navigating by table of contents. Similar to using Navigation bar/table of contents on Wikipedia page.)\n\n3. Back to main menu")
        elif '3' == incoming_msg or '3.' == incoming_msg:
            user_states[sender]['state'] = 'menu'
            resp.message(
                "\nWelcome to TextWiki. Please choose one of the following options (Type 1, 2, or 3):\n\n1. Info\n2. Search for a word\n3. Exit TextWiki")
        else:
            resp.message("Sorry, we didn't understand your message. Please choose one of the options from the menu (Type 1, 2, or 3):\n\n1. Learn more about this topic\n2. Search for a different word\n3. Return to the main menu")

    return str(resp)


if __name__ == "__main__":
    app.run(debug=True)
