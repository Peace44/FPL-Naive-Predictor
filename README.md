# FPL-Naive-Predictor

FPL Naive Predictor is a Python project that predicts and simulates Fantasy Premier League (FPL) performance over 1, 2, or 3 gameweeks. The project uses a simple naive approach to predict FPL points, based on historical data and basic statistics.



## Installation
To install FPL Naive Predictor, follow these steps:



Clone the repository to your local machine using Git or download the zip file.
Install the required dependencies using pip. You can do this by running the following command in your terminal or command prompt:

```bash
pip install -r requirements.txt
```



## Usage
Once you have installed the project, you can use it to predict and simulate FPL performance by following these steps:

Open the fpl_naive_predictor.py file in your Python editor or IDE.
Modify the team_id, num_gameweeks, and use_form variables to suit your needs. team_id should be set to the ID of the FPL team you want to predict for, num_gameweeks should be set to the number of gameweeks you want to simulate, and use_form should be set to True if you want to use recent form to make predictions, or False if you want to use historical data only.
Run the fpl_naive_predictor.py file in your Python editor or IDE.
The script will output the predicted FPL points for each player in your team over the specified number of gameweeks, as well as the total predicted points for your team.



## How it works
FPL Naive Predictor uses a simple approach to predict FPL points, based on historical data and basic statistics. The project calculates the average points per game (PPG) for each player over the previous four gameweeks (if use_form is set to True) or over the entire season (if use_form is set to False).

The project then calculates a predicted score for each player in your team, based on the following formula:

makefile
Copy code
predicted_score = (player_ppg * fixture_difficulty) / 2
where player_ppg is the player's average PPG, and fixture_difficulty is a difficulty rating for the upcoming fixture based on the FPL fixture difficulty rating system.

Finally, the project adds up the predicted scores for all players in your team over the specified number of gameweeks to calculate the total predicted points for your team.



## Contributing
If you want to contribute to FPL Naive Predictor, you can do so by:

Forking the repository.
Making your changes.
Submitting a pull request.

## License
FPL Naive Predictor is licensed under the MIT License. See LICENSE for more information.



