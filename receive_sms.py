from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse, Media
import wiki

app = Flask(__name__)

user_states = {}

@app.route("/", methods=['GET', 'POST'])
def sms_reply():
    # Get the incoming message and sender's phone number
    incoming_msg = request.values.get('Body', '').lower()
    #Concatenate the user's input
    incoming_msg = incoming_msg.replace(' ', '_')
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
            resp.message("\nWelcome to TextWiki. Please choose one of the following options (Type 1, 2, or 3):\n\n1. Info\n2. Search for a word\n3. Exit TextWiki")
        elif '1' == incoming_msg or '1.' == incoming_msg:
            # Respond with message for Option 1
            resp.message("TextWiki is designed to offer the features of searching for a word and navigating through the Wikipedia page containing information about that word via text message.\n In its current state 'V1.0' TextWiki allows you to search for a word and view search results in small snippets of information. You may also request for more information about a word if necessary.\n\n---\n\nTextWiki will be 'released' incrementally with upcoming versions including features such as:\n\n V1.1: More robust navigation by means of the navigation bar to view information by section\n V1.2: ChatGPT integration to offer support for topics that do not have sufficient information via the Wikipeadia page\n V1.3: Access to works cited referenced in Wikipedia page\n V1.4: Access to pictures associated with given Wikipedia page.\n\n---\n\nPlease choose one of the following options (Type 1, 2, or 3):\n\n1. Info\n2. Search for a word\n3. Exit TextWiki")
            # resp.message("TextWiki will be 'released' incrementally with upcoming versions including features such as:\n\n V1.1: More robust navigation by means of the navigation bar to view information by section\n V1.2: ChatGPT integration to offer support for topics that do not have sufficient information via the Wikipeadia page\n V1.3: Access to works cited referenced in Wikipedia page\n V1.4: Access to pictures associated with given Wikipedia page.")
            # resp.message("Please choose one of the following options (Type 1, 2, or 3):\n\n1. Info\n2. Search for a word\n3. Exit TextWiki")
            user_states[sender]['state'] = 'menu'
        elif '2' == incoming_msg or '2.' == incoming_msg:
            # Update the user's state
            user_states[sender]['state'] = 'choose search'
            # Respond with message for Option 2
            resp.message("Please choose search method (Type 1, 2, or 3):\n\n 1. General search \n(Populate topic information navigating by paragraph. Similar to scrolling down Wikipedia page)\n\n 2. Navigated search \n(Populate topic information navigating by table of contents. Similar to using Navigation bar/table of contents on Wikipedia page.)\n\n3. Back to main menu")
        elif '3' == incoming_msg or '3.' == incoming_msg:
            # Respond with message for Option 3
            resp.message("Thanks for using TextWiki! See you again soon")
        else:
            # If the user sends any other message, send an error message
            resp.message("Sorry, we didn't understand your message. Please choose one of the options from the menu.")
    
    elif current_state == 'choose search':
        if '1' == incoming_msg or '1.' == incoming_msg:
            # Update the user's state
            user_states[sender]['state'] = 'general search'
            resp.message("What topic would you like to search for?")
        elif '2' == incoming_msg or '2.' == incoming_msg:
            user_states[sender]['state'] = 'navigate search'
            resp.message("What topic would you like to search for?")
            # msg = resp.message ("This feature is currently in development! Please check back soon for a more robust search experience :D !")
            # msg.media("https://img.freepik.com/free-vector/abstract-coming-soon-halftone-style-background-design_1017-27282.jpg")
        elif '3' == incoming_msg or '3.' == incoming_msg:
            user_states[sender]['state'] = 'menu'
            resp.message("\nWelcome to TextWiki. Please choose one of the following options (Type 1, 2, or 3):\n\n1. Info\n2. Search for a word\n3. Exit TextWiki")
    
    elif current_state == 'general search':
        # Call the wiki.main function with the user's query
        paragraphs, navbar = wiki.main(incoming_msg)
        user_states[sender]['paragraphs'] = paragraphs

        # Send the first paragraph as a message
        if len(paragraphs) < 2:
            gptParagraph = wiki.gptSearch(incoming_msg)
            resp.message (gptParagraph)
            resp.message("Please choose one of the following options (Type 1, 2, or 3):\n\n1. Info\n2. Search for a word\n3. Exit TextWiki")
            user_states[sender]['state'] = 'menu'
        else:
            user_states[sender]['current_paragraph'] = 1
            resp.message("Here is information about your requested topic:\n\n" + paragraphs[1])
            resp.message("Please choose one of the following options (Type 1, 2, or 3):\n\n1. Learn more about this topic\n2. Search for a different Wikipedia page\n3. Return to the main menu")
            user_states[sender]['state'] = 'reading_gsearch'

    elif current_state == 'navigate search':
        # Call the wiki.main function with the user's query
        paragraphs, navbar_elems = wiki.main(incoming_msg)
        user_states[sender]['curr_word'] = incoming_msg
        # Add if statement to check if word is less than 2 paragraphs
        resp.message("Which Section would you like to view (please type the name of the section you want to view):")
        navbar_items = ""
        for item in navbar_elems:
            if item == 'mw-content-text' or item == 'See_also' or item == 'References' or item == 'External_links' or item == 'Further_reading' or item == 'Notes':
                continue
            else:
                item = item.replace('_', ' ')
                navbar_items += item + "\n\n========\n"
        resp.message(navbar_items)
        user_states[sender]['state'] = 'reading_nsearch'


    elif current_state == 'reading_nsearch':
        paragraphs, navbar_elems = wiki.main(user_states[sender]['curr_word'], incoming_msg.capitalize())
        # Send the first paragraph as a message
        # if len(paragraphs) < 2:
        #     gptParagraph = wiki.gptSearch(incoming_msg)
        #     resp.message (gptParagraph)
        #     resp.message("Please choose one of the following options (Type 1, 2, or 3):\n\n1. Info\n2. Search for a word\n3. Exit TextWiki")
        #     user_states[sender]['state'] = 'menu'
        # else:
        user_states[sender]['current_paragraph'] = 1
        resp.message("Here is information about your requested topic:\n\n" + paragraphs[1])
        resp.message("Please choose one of the following options (Type 1, 2, or 3):\n\n1. Learn more about this topic\n2. Search for a different Wikipedia page\n3. Return to the main menu")
        user_states[sender]['state'] = 'reading_gsearch'

        

    elif current_state == 'reading_gsearch':
        if '1' == incoming_msg or '1.' == incoming_msg:
            user_states[sender]['current_paragraph'] += 1
            if user_states[sender]['current_paragraph'] < len(user_states[sender]['paragraphs']):
                resp.message("Here is information about your requested topic:\n\n" + user_states[sender]['paragraphs'][user_states[sender]['current_paragraph']])
                resp.message("Please choose one of the following options (Type 1, 2, or 3):\n\n1. Learn more about this topic\n2. Search for a different Wikipedia page\n3. Return to the main menu")
            else:
                resp.message("No more information available on this topic at this time. Type 'menu' to return to the main menu.")
                user_states[sender]['state'] = 'menu'
        elif '2' == incoming_msg or '2.' == incoming_msg:
            user_states[sender]['state'] = 'choose search'
            resp.message("Please choose search method (Type 1, 2, or 3):\n\n 1. General search (Populate topic information navigating by paragraph. Similar to scrolling down Wikipedia page)\n 2. Navigated search (Populate topic information navigating by table of contents. Similar to using Navigation bar/table of contents on Wikipedia page.)\n3. Back to main menu")
        elif '3' == incoming_msg or '3.' == incoming_msg:
            user_states[sender]['state'] = 'menu'
            resp.message("\nWelcome to TextWiki. Please choose one of the following options (Type 1, 2, or 3):\n\n1. Info\n2. Search for a word\n3. Exit TextWiki")        
        else:
            resp.message("Sorry, we didn't understand your message. Please choose one of the options from the menu (Type 1, 2, or 3):\n\n1. Learn more about this topic\n2. Search for a different word\n3. Return to the main menu")


    return str(resp)



if __name__ == "__main__":
    app.run(debug=True)
