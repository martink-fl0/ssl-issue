from cs50 import SQL
from flask import flash, redirect

# Score constants
CORRECT_ANSWER = 3
INCORRECT_ANSWER = -1


def end_of_season(db):
    """ Calculates scores for all users for the current season """

    # Check for the current season
    current = db.execute("SELECT season FROM status WHERE current = 'True'")[0]["season"]

    # User's predictions list of dics
    users_predictions = db.execute("SELECT predict.user_id, users.fullname, predict.selection_id, predict.tyres_id FROM predict JOIN users ON predict.user_id = users.id WHERE predict.season_id = ? AND predict.league = 'Elite' ORDER BY users.id, predict.selection_id", current)
    # Actual selections by assets list of dics
    assets_selections = db.execute("SELECT selection_id, fullname, tyres_id FROM selection WHERE season = ? AND league = 'Elite' ORDER BY selection_id", current)

    # To store the scores
    scores = []
    for prediction in users_predictions:
        if (score_dic := {"user_id": prediction['user_id'], "fullname": prediction['fullname'], "score": 0, "picks": 0, "incorrect": 0, "pipis": 0, "correct": 0}) not in scores:
            scores.append(score_dic)

    # Retrieve id for Pipis
    pipis = db.execute("SELECT tyres_id FROM tyres WHERE season = ? and brand = 'Pipirelli'", current)[0]["tyres_id"]

    # Create and set the right/wrong predictions counters to 0 for the asset
    for asset in assets_selections:
        asset['pred_right'] = 0
        asset['pred_wrong'] = 0
        asset['total_pred'] = 0

    # Loop all user predictions
    for prediction in users_predictions:
        # Loop through all assets selections
        for asset in assets_selections:
            # If the user predicted the asset
            if prediction["selection_id"] == asset["selection_id"]:
                # Add one to the asset predicted count
                asset['total_pred'] += 1
                # Loop the scored dictionaries to log answers
                for score in scores:
                    # Localize the user in the scores list of dicts
                    if score["user_id"] == prediction["user_id"]:
                        # Score for correct answer
                        if prediction["tyres_id"] == asset["tyres_id"]:
                            score["score"] += CORRECT_ANSWER
                            score["picks"] += 1
                            score["correct"] += 1
                            # Add to asset dict
                            asset['pred_right'] += 1
                            if prediction["tyres_id"] == pipis:
                                score["pipis"] += 1
                        # Score for incorrect answer
                        elif prediction["tyres_id"] != asset["tyres_id"]:
                            score["score"] += INCORRECT_ANSWER
                            score["picks"] += 1
                            score["incorrect"] += 1
                            # Add to asset dict
                            asset['pred_wrong'] += 1
                            

    # Log the right and wrong predictions for the asset
    for asset in assets_selections:
        if asset['total_pred'] != 0:
            asset['pred_right'] = float(asset['pred_right'] / asset['total_pred'] * 100)
            asset['pred_wrong'] = float(asset['pred_wrong'] / asset['total_pred'] * 100)
        else:
            asset['pred_right'] = None
            asset['pred_wrong'] = None
            asset['total_pred'] = None
        db.execute("UPDATE selection SET pred_right = ?, pred_wrong = ?, total_pred = ? WHERE selection_id = ?", asset['pred_right'], asset['pred_wrong'], asset['total_pred'], asset['selection_id'])

    # Log scores for players
    for score in scores:
        # Calculate correct percentage
        score["correct"] = float(score["correct"] / score["picks"] * 100)
        # Log score to the database
        db.execute("INSERT INTO scores (season, league, user_id, user_name, total_score, number_picks, incorrect, correct_p, perc_correct) VALUES (?, 'Elite', ?, ?, ?, ?, ?, ?, ?)", current, score["user_id"], score["fullname"], score["score"], score["picks"], score["incorrect"], score["pipis"], score["correct"])

    # All set to display in the app!!!
    flash("Season results have been calculated")
    return redirect("/adminpanel")
