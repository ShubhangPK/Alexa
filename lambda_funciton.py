import boto3

#------------------------------Part1--------------------------------
# In this part we define a list that contains the player names, and 
# a dictionary with player biographies


people = {'pen': {'table': 1},
          'cloth': {'table': 1}}
#Probable_Place_List = {
#    "pen":"Try checking behind the table or in the attic"


#------------------------------Part2--------------------------------
# Here we define our Lambda function and configure what it does when 
# an event with a Launch, Intent and Session End Requests are sent. # The Lambda function responses to an event carrying a particular 
# Request are handled by functions such as on_launch(event) and 
# intent_scheme(event).
def lambda_handler(event, context):
    if event['session']['new']:
        on_start()
    if event['request']['type'] == "LaunchRequest":
        return on_launch(event)
    elif event['request']['type'] == "IntentRequest":
        return intent_scheme(event)
    elif event['request']['type'] == "SessionEndedRequest":
        return on_end()
#------------------------------Part3--------------------------------
# Here we define the Request handler functions
def on_start():
    print("Session Started.")

def on_launch(event):
    onlunch_MSG = "Hi, welcome to the Find my things Alexa Skill. I will help you locate your most valuable things. To help me learn better, please report to me where you have previously lost an item.\
    If you would like to hear where the requested item is, you could say for example: where is my pen"
    reprompt_MSG = "Do you want to hear more about a particular item?"
    card_TEXT = "Pick an item."
    card_TITLE = "Choose an item ."
    return output_json_builder_with_reprompt_and_card(onlunch_MSG, card_TEXT, card_TITLE, reprompt_MSG, False)

def on_end():
    print("Session Ended.")
#-----------------------------Part3.1-------------------------------
# The intent_scheme(event) function handles the Intent Request. 
# Since we have a few different intents in our skill, we need to 
# configure what this function will do upon receiving a particular 
# intent. This can be done by introducing the functions which handle 
# each of the intents.
def intent_scheme(event):
    
    intent_name = event['request']['intent']['name']

    if intent_name == "helpFindItem":
        #print(event)
        return find_items(event)       
    elif intent_name == "reportItems":
        return update_table(event)
    elif intent_name in ["AMAZON.NoIntent", "AMAZON.StopIntent", "AMAZON.CancelIntent"]:
        
        return stop_the_skill(event)
    elif intent_name == "AMAZON.HelpIntent":
        return assistance(event)
    elif intent_name == "AMAZON.FallbackIntent":
        return fallback_call(event)
#---------------------------Part3.1.1-------------------------------
# Here we define the intent handler functions
def find_items(event):
    name=event['request']['intent']['slots']['items']['value']
    #item_list_lower=[w.lower() for w in Items_List]
    #if name.lower() in item_list_lower:
    #    reprompt_MSG = "Do you want to hear more about a particular item?"
     #   card_TEXT = "You've picked " + name.lower()
      #  card_TITLE = "You've picked " + name.lower()
      #  return output_json_builder_with_reprompt_and_card(Probable_Place_List[name.lower()], card_TEXT, card_TITLE, reprompt_MSG, False)
    if name in people.keys():
        msg = "Your item is most probably near the " + max(people[name])
        reprompt_MSG = "Do you want to hear more about a particular item?"
        card_TEXT = "Use the full name."
        card_TITLE = "Wrong name."
        return output_json_builder_with_reprompt_and_card(msg, msg, msg, reprompt_MSG, False)
    else:
        wrongname_MSG = "You haven't reported this one before! Please let me know when you find it so I can help you better next time"
        reprompt_MSG = "Do you want to hear more about a particular items?"
        card_TEXT = "Use the full name."
        card_TITLE = "Wrong name."
        return output_json_builder_with_reprompt_and_card(wrongname_MSG, card_TEXT, card_TITLE, reprompt_MSG, False)
        
def update_table(event):
    lostItem = event['request']['intent']['slots']['item']['value']
    foundPlace = event['request']['intent']['slots']['place']['value']
    #Items_List.append(lostItem)
    #Probable_Place_List[lostItem]=str("Try checking near the "+foundPlace)
    b = lostItem
    c = foundPlace
    
    if b in people.keys():
        if c in people[b].keys():
            people[b][c]+=1
        else:
            people[b][c]=1
    else:
        people[b]={}
        people[b][c]=1
    dynamodb = boto3.resource('dynamodb',region_name='us-east-1')
    table = dynamodb.Table('findingitems')
    table.put_item(
    Item={
        'item': lostItem,
        'place': foundPlace,
        
    }
        )

    
    
    card_TEXT = "You've aded the item " + lostItem
    card_TITLE = "  "
    reprompt_MSG = "Your item has been successfully added : "+card_TEXT+" "+card_TITLE
    
    prompt = "awesome"
    return output_json_builder_with_reprompt_and_card(reprompt_MSG, card_TEXT, card_TITLE,prompt, False)
    
        
def stop_the_skill(event):
    stop_MSG = "Thank you. Bye!"
    reprompt_MSG = ""
    card_TEXT = "Bye."
    card_TITLE = "Bye Bye."
    return output_json_builder_with_reprompt_and_card(stop_MSG, card_TEXT, card_TITLE, reprompt_MSG, True)
    
def assistance(event):
    assistance_MSG = "You can choose among these items: " + ', '.join(map(str, Probable_Place_List)) + ". Be sure to use the right name when asking about the item."
    reprompt_MSG = "Do you want to hear more about a particular item?"
    card_TEXT = "You've asked for help."
    card_TITLE = "Help"
    return output_json_builder_with_reprompt_and_card(assistance_MSG, card_TEXT, card_TITLE, reprompt_MSG, False)

def fallback_call(event):
    fallback_MSG = "I can't help you with that, try rephrasing the question or ask for help by saying HELP."
    reprompt_MSG = "Do you want to hear more about a particular items?"
    card_TEXT = "You've asked a wrong question."
    card_TITLE = "Wrong question."
    return output_json_builder_with_reprompt_and_card(fallback_MSG, card_TEXT, card_TITLE, reprompt_MSG, False)
#------------------------------Part4--------------------------------
# The response of our Lambda function should be in a json format. 
# That is why in this part of the code we define the functions which 
# will build the response in the requested format. These functions
# are used by both the intent handlers and the request handlers to 
# build the output.
def plain_text_builder(text_body):
    text_dict = {}
    text_dict['type'] = 'PlainText'
    text_dict['text'] = text_body
    return text_dict

def reprompt_builder(repr_text):
    reprompt_dict = {}
    reprompt_dict['outputSpeech'] = plain_text_builder(repr_text)
    return reprompt_dict
    
def card_builder(c_text, c_title):
    card_dict = {}
    card_dict['type'] = "Simple"
    card_dict['title'] = c_title
    card_dict['content'] = c_text
    return card_dict    

def response_field_builder_with_reprompt_and_card(outputSpeach_text, card_text, card_title, reprompt_text, value):
    speech_dict = {}
    speech_dict['outputSpeech'] = plain_text_builder(outputSpeach_text)
    speech_dict['card'] = card_builder(card_text, card_title)
    speech_dict['reprompt'] = reprompt_builder(reprompt_text)
    speech_dict['shouldEndSession'] = value
    return speech_dict

def output_json_builder_with_reprompt_and_card(outputSpeach_text, card_text, card_title, reprompt_text, value):
    response_dict = {}
    response_dict['version'] = '1.0'
    response_dict['response'] = response_field_builder_with_reprompt_and_card(outputSpeach_text, card_text, card_title, reprompt_text, value)
    return response_dict
