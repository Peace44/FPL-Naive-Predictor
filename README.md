**Project Description: FPL Naive Predictor**

The FPL Naive Predictor is a Python-based tool designed to assist Fantasy Premier League (FPL) managers in making data-driven decisions for team selection and player transfers. By leveraging real-time data from the official FPL API, the project analyzes past performances, simulates future gameweeks, and predicts player and team potentials. This comprehensive analysis helps users optimize their fantasy teams to maximize points in upcoming matches.

---

### **Key Features:**

1. **Data Retrieval from FPL API:**
   - **General Information:** Fetches data on teams, player positions, and individual players.
   - **Fixture Data:** Retrieves past and upcoming fixture information, including results and schedules.
   - **Live Gameweek Data:** Accesses per-gameweek statistics for all players up to the current gameweek.

2. **Statistical Computations:**
   - **Team-Level Statistics:**
     - **Matches Played:** Counts the number of matches each team has played.
     - **Goals For/Against:** Calculates total goals scored and conceded by each team.
     - **Clean Sheets:** Tallies the number of matches where a team did not concede any goals.
   - **Player-Level Statistics:**
     - **Total Points:** Aggregates the total FPL points each player has earned.
     - **Average Points per Fixture:** Computes average points based on matches played.
     - **Form:** Assesses recent performance over the last 30 days.
     - **Expected Points (xPts):** Predicts future performance using a weighted sum of form and average points.

3. **Advanced Statistical Functions:**
   - **Golden Ratio Weighting (`golden_sum`):** Applies the golden ratio to blend different statistical measures, giving more weight to recent form.
   - **Average Deviation Calculation (`calculate_avg_deviation`):** Measures consistency by calculating the average absolute deviation from the mean.
   - **Standard Score Computation (`Z`):** Standardizes data using Z-scores for meaningful comparisons.

4. **Simulation of Future Gameweeks:**
   - **User Input for Gameweek Selection:** Allows simulation of specific or multiple future gameweeks based on user preference.
   - **Advantage Calculation:**
     - **FPL Advantage (`fplAdv_nxtGWs`):** Measures overall team advantage considering both offensive and defensive strengths.
     - **Defensive and Attacking Advantages (`defAdv_nxtGWs`, `attAdv_nxtGWs`):** Separates team strengths into defensive and attacking potentials.
   - **Adjusting Player Expected Points:** Modifies player xPts based on upcoming opponent strengths and the calculated advantages.

5. **Team and Player Ranking:**
   - **Team Rankings:**
     - **FPL Potential:** Ranks teams based on overall potential to earn FPL points.
     - **Defensive and Attacking Potentials:** Provides separate rankings for defense and attack.
     - **Z-Scores for Potentials:** Standardizes potentials for cross-team comparisons.
   - **Player Selections:**
     - **Top Players per Team:** Identifies the top-performing players in each team for FPL consideration.
     - **Position-Specific Top Players:** Highlights top defenders, midfielders, and forwards based on expected performance.

6. **Best Team Selection Algorithm:**
   - **Dynamic Formation Selection:** Evaluates multiple formations to maximize total expected points.
   - **Position Allocation:** Distributes players into positions based on calculated potentials and expected points.
   - **Selection Criteria:** Offers selection based on various advantages (FPL, defensive, attacking, average).

7. **Data Export and Logging:**
   - **Timestamped Data Saving:** Stores simulation results and statistics in time-labeled directories for version tracking.
   - **CSV and Text Outputs:** Exports data in accessible formats for further analysis or record-keeping.

8. **User Interaction and Customization:**
   - **Interactive Prompts:** Engages users for inputs on data availability and simulation preferences.
   - **Error Handling:** Provides informative messages in case of missing data or incorrect inputs.
   - **Optional Data Saving:** Allows users to decide whether to save simulation results.

---

### **Technical Highlights:**

- **Python Libraries Used:**
  - **Requests:** For HTTP requests to the FPL API.
  - **Pandas and NumPy:** For data manipulation and statistical calculations.
  - **Collections:** For organizing players by position and team.
- **Data Structures:**
  - **DataFrames:** Used extensively to store and manipulate player and team data.
  - **Dictionaries and Lists:** For efficient data access and aggregation.
- **Mathematical Concepts:**
  - **Golden Ratio:** Employed to weight recent performance more heavily.
  - **Z-Score Standardization:** For normalizing potentials across different scales.
- **Modular Functions:**
  - **`golden_sum`:** Calculates weighted sums using the golden ratio.
  - **`calculate_avg_deviation`:** Computes consistency metrics for player performances.
  - **`Z`:** Standardizes a series using Z-scores.

---

### **Workflow Overview:**

1. **Initialization:**
   - Imports necessary libraries.
   - Defines API endpoints.
   - Fetches general data (teams, players, positions) from the FPL API.

2. **Historical Data Processing:**
   - Collects past fixture results.
   - Calculates team statistics (matches played, goals for/against, clean sheets).
   - Optionally integrates previous gameweek trends if available.

3. **Player Statistics Calculation:**
   - For each player, computes:
     - Total points.
     - Average points per fixture.
     - Form and expected points.
     - Consistency measures (average deviations).

4. **Team Statistics Calculation:**
   - Aggregates player stats to the team level.
   - Separates statistics for defensive and attacking units.
   - Calculates potentials and standardizes them using Z-scores.

5. **Future Fixture Simulation:**
   - Prompts the user for gameweeks to simulate.
   - Processes upcoming fixtures to calculate team advantages.
   - Adjusts player expected points based on these advantages.

6. **Ranking and Selection:**
   - Sorts teams and players based on calculated potentials and advantages.
   - Creates matrices for top FPL players, defenders, and attackers per team.
   - Forms decision matrices to assist in team selection.

7. **Best Team Formation:**
   - Utilizes the `select_best_team` function to pick the optimal lineup.
   - Considers multiple formations and selects based on the highest total expected points.
   - Generates a readable output of the selected team by position.

8. **Output Generation:**
   - Displays matrices and selected teams in the console.
   - Offers the option to save all results to files in a structured directory.

---

### **Purpose and Benefits:**

- **Data-Driven Decision Making:** Empowers FPL managers with statistical insights rather than relying on intuition alone.
- **Optimized Team Selection:** Helps users maximize their FPL points by selecting players with the highest expected returns.
- **Future Planning:** By simulating upcoming gameweeks, users can strategize transfers and substitutions in advance.
- **Comprehensive Analysis:** Provides both team-level and player-level insights, covering overall performance, attack, and defense.
- **User-Friendly Interaction:** Interactive prompts and clear outputs make the tool accessible even for users with limited programming experience.

---

### **Conclusion:**

The FPL Naive Predictor is a robust tool that bridges real-world football data with fantasy league strategy. By combining API data retrieval, statistical analysis, and predictive modeling, it offers a comprehensive solution for FPL managers aiming to enhance their team's performance. Whether you're a casual player or a seasoned veteran, this project provides valuable insights to inform your gameweek decisions and overall FPL strategy.

---

### **Usage Notes:**

- **Prerequisites:** Ensure you have Python installed along with the required libraries (`requests`, `pandas`, `numpy`, etc.).
- **Running the Script:** Execute the script in a Python environment. Follow the interactive prompts for data inputs and preferences.
- **Data Saving:** Choose to save the results when prompted. Data will be organized in a timestamped directory for easy reference.
- **Customization:** The code can be extended or modified to include additional statistical measures or to adjust the weighting in predictions.

---

**Disclaimer:** While the FPL Naive Predictor provides data-driven recommendations, the unpredictable nature of sports means that actual results may vary. Users should consider multiple sources of information when making FPL decisions.
