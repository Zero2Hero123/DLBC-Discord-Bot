from pymongo import MongoClient
import re

cluster = MongoClient("mongodb+srv://crazen:Vf1b3hXAphxvbdur@dlbcserver.5a3ea.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = cluster["members"]
level_system = db["levels"]
weekly_wordsys = db["weekly_words"]

def add_exp(user_id: int,exp: int):
  leveled_up = False

  level_system.update_one({"_id": user_id}, {"$inc": {"exp": exp}})

  user_data = level_system.find_one({"_id": user_id})
  print(user_data)

  if user_data["exp"] >= user_data["max_exp"]:
    new_exp = user_data["exp"] - user_data["max_exp"]

    new_max_exp = user_data["max_exp"] * 1.1
    new_max_exp = int(new_max_exp)


    level_system.update_one({"_id": user_id}, {"$inc": {"level": 1}})
    level_system.update_one({"_id": user_id}, {"$set": {"max_exp": new_max_exp}})
    level_system.update_one({"_id": user_id}, {"$set": {"exp": new_exp}})

    leveled_up = True

    print(f"Added {exp} to {user_id}.")


  return leveled_up

def is_badword(word,message):
  is_bad = False

  """
  add a way to find if the word is not a white space or not. if so, run lines 19-25; else run lines 26-29
  """

  test_list = []
  word_seperators = ["."," ","-"]

  match = re.search(f"{word}|{word.upper()}|{word.lower()}|{word.capitalize()}",message)
  match_ws = None

  if match != None:
    match_ws = re.search(f" {match.group()} ",message)

    if match_ws == None:
      match_ws = re.search(f"{match.group()} ",message)

      if match_ws == None:
        match_ws = re.search(f"{match.group()} ",message)
    
    print(match_ws)

  # check for whitespaces
  is_whitespace = match_ws != None

  if is_whitespace:
    is_bad = True

    print("whited")
    return {"is_bad": True,"probable_mistake": False}
  
  # check for seperators
  for character in word:

    test_list.append(character)

  for sep in word_seperators:

    word_ = sep.join(test_list)

    if word_ in message or word_.upper() in message or word_.lower() in message or word_.capitalize() in message:
      is_bad = True

      print("sep")
      print(word_)
      return {"is_bad": is_bad,"probable_mistake": False}
    
  
  if word in message:

    print("end 1")
    return {"is_bad": True,"probable_mistake": True}
  else:
    print("end 2")
    return {"is_bad": False,"probable_mistake": False}


  