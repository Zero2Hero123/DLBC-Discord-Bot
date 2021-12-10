from pymongo import MongoClient

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

# CHRISTMAS EVENT STUFF


  